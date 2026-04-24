import os
import sqlite3
import base64
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage,
    AudioMessage, AudioSendMessage, LocationMessage, ImageSendMessage, FollowEvent
)
from dotenv import load_dotenv

from line_client import line_bot_api, handler
from scheduler import scheduler
from agent import ask_hermes, update_user_location
from vision import analyze_image_base64
from voice import convert_m4a_to_wav, transcribe_audio, generate_tts, STATIC_DIR

load_dotenv()

app = FastAPI()

# Mount static folder for LINE to reach TTS audio files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Expose Base URL for ngrok/domain so audio files have an absolute URL
# Fallback to local if not set, but LINE audio requires https !
BASE_URL = os.getenv("BASE_URL", "https://ace-lioness-instantly.ngrok-free.app")

# Initialize Group Chat SQLite directly
DATA_DIR = os.environ.get("DATA_DIR", ".")
GROUP_DB = os.path.join(DATA_DIR, "groups.db")
def init_group_db():
    conn = sqlite3.connect(GROUP_DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, group_id TEXT, user_id TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()
init_group_db()

def log_group_message(group_id, user_id, message):
    conn = sqlite3.connect(GROUP_DB)
    c = conn.cursor()
    c.execute("INSERT INTO messages (group_id, user_id, message) VALUES (?, ?, ?)", (group_id, user_id, message))
    conn.commit()
    conn.close()

def get_group_history(group_id, limit=20):
    conn = sqlite3.connect(GROUP_DB)
    c = conn.cursor()
    c.execute("SELECT user_id, message FROM messages WHERE group_id=? ORDER BY id DESC LIMIT ?", (group_id, limit))
    rows = c.fetchall()
    conn.close()
    return reversed(rows) # Chronological

@app.on_event("startup")
def startup_event():
    print("Starting APScheduler...")
    scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

def send_hermes_response(user_id, reply_token, prompt_text, is_audio_reply=False):
    """Core function to interact with Hermes and route response properly."""
    reply_text = ask_hermes(prompt_text, user_id)
    
    # 🌟 MAGIC INTERCEPTORS: Check if Hermes created an Image or a Flex Message
    if reply_text.startswith("FLEX_EXPENSE:"):
        # Format string: FLEX_EXPENSE: amount|category|item
        parts = reply_text.replace("FLEX_EXPENSE:", "").split("|")
        if len(parts) >= 3:
            from line_flex import get_expense_receipt_flex
            from datetime import datetime
            flex_msg = get_expense_receipt_flex(parts[0], parts[1], parts[2], datetime.now().strftime("%Y-%m-%d %H:%M"))
            line_bot_api.reply_message(reply_token, flex_msg)
            return

    elif reply_text.startswith("IMAGE_GEN:"):
        # Format string: IMAGE_GEN: url
        image_url = reply_text.replace("IMAGE_GEN:", "").strip()
        line_bot_api.reply_message(reply_token, ImageSendMessage(original_content_url=image_url, preview_image_url=image_url))
        return
        
    # Default Text Reply
    messages = [TextSendMessage(text=reply_text)]
    
    if is_audio_reply:
        # Generate TTS and attach Audio Message!
        audio_filename = generate_tts(reply_text)
        if audio_filename:
            audio_url = f"{BASE_URL}/static/{audio_filename}"
            # Duration is dummy 5000ms for simplicity
            messages.append(AudioSendMessage(original_content_url=audio_url, duration=5000))
            
    line_bot_api.reply_message(reply_token, messages)

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature.")
    return "OK"

# Schema for LIFF API Payload
class LocationPayload(BaseModel):
    user_id: str
    lat: float
    lng: float
    address: str

@app.post("/api/update_location")
def api_update_location(payload: LocationPayload):
    """Receives silent background location data from the LIFF Mini App."""
    update_user_location(payload.user_id, payload.address, payload.lat, payload.lng)
    return {"status": "success", "message": "Location updated"}

@handler.add(FollowEvent)
def handle_follow(event):
    from line_flex import create_welcome_checklist_flex
    flex_msg = create_welcome_checklist_flex()
    line_bot_api.reply_message(event.reply_token, flex_msg)

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = event.source.user_id
    text = event.message.text
    
    # --- Interceptors for Rich Menu ---
    user_text = text.strip()
    if user_text == "เมนูช่วยเหลือ":
        from line_flex import create_help_flex_message
        flex_msg = create_help_flex_message()
        line_bot_api.reply_message(event.reply_token, flex_msg)
        return
        
    elif user_text == "สรุปบัญชีให้หน่อย":
        from datetime import datetime
        conn = sqlite3.connect(os.path.join(os.environ.get("DATA_DIR", "."), "expenses.db"))
        c = conn.cursor()
        month_str = datetime.now().strftime("%Y-%m")
        
        # Query overall total
        c.execute("SELECT sum(amount) FROM expenses WHERE timestamp LIKE ?", (f"{month_str}%",))
        res = c.fetchone()
        overall_total = res[0] if res and res[0] else 0.0
        
        # Query breakdown by person
        c.execute("""
            SELECT p.display_name, e.user_id, sum(e.amount) 
            FROM expenses e 
            LEFT JOIN users_profile p ON e.user_id = p.user_id 
            WHERE e.timestamp LIKE ? 
            GROUP BY e.user_id, p.display_name
            ORDER BY sum(e.amount) DESC
        """, (f"{month_str}%",))
        
        breakdown_rows = c.fetchall()
        breakdown = []
        for row in breakdown_rows:
            name = row[0]
            if not name:
                name = f"User {row[1][-4:]}"
            breakdown.append((name, row[2]))
            
        conn.close()
        
        from line_flex import get_expense_summary_flex
        flex_msg = get_expense_summary_flex("เดือนนี้ (This Month)", f"{overall_total:,.2f}", breakdown)
        line_bot_api.reply_message(event.reply_token, flex_msg)
        return
        
    elif user_text == "ฟีเจอร์แปลภาษา":
        try:
            from agent import get_or_create_agent
            user_agent = get_or_create_agent(user_id)
            user_agent.memory.chat_memory.add_user_message("ฉันต้องการใช้ฟีเจอร์แปลภาษาข้อความถัดไป")
            user_agent.memory.chat_memory.add_ai_message("พิมพ์ข้อความที่ต้องการให้แปลมาได้เลยครับ")
        except: pass
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="พิมพ์ภาษาอะไรมาก็ได้เลยค๊าบ เดี๋ยวผมแปลให้ 🇬🇧🇹🇭🇯🇵"))
        return
        
    elif user_text == "วาดรูปภาพ":
        try:
            from agent import get_or_create_agent
            user_agent = get_or_create_agent(user_id)
            user_agent.memory.chat_memory.add_user_message("ฉันต้องการใช้ฟีเจอร์วาดรูปภาพ (ใช้เครื่องมือวาดรูปภาพเมื่อฉันพิมพ์สิ่งที่ต้องการ)")
            user_agent.memory.chat_memory.add_ai_message("เตรียมพู่กันพร้อมแล้ว! ใส่ Prompt หรือระบุสิ่งที่คุณอยากให้วาดได้เลยครับ")
        except: pass
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="เตรียมพู่กันพร้อมแล้ว! ใส่ Prompt เล่ารายละเอียดสิ่งที่คุณอยากให้วาดมาได้เลยครับ 🎨✨"))
        return
        
    elif user_text == "ค้นหาข้อมูลในเว็บ":
        try:
            from agent import get_or_create_agent
            user_agent = get_or_create_agent(user_id)
            user_agent.memory.chat_memory.add_user_message("ฉันต้องการใช้ค้นหาข้อมูลในเว็บด้วยเครื่องมือ web_search สำหรับข้อความถัดไป")
            user_agent.memory.chat_memory.add_ai_message("ฉันสแตนด์บายเตรียมค้นหาบนเว็บแล้ว พิมพ์คีย์เวิร์ดมาได้เลยครับ")
        except: pass
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="ฉันสแตนด์บายรอรับคีย์เวิร์ดแล้ว! พิมพ์เรื่องที่คุณอยากรู้มาได้เลยครับ เดี๋ยวไปค้นในอินเทอร์เน็ตมาให้ 🌐🔍"))
        return
    
    # Handle Group Chats
    if event.source.type == "group":
        group_id = event.source.group_id
        log_group_message(group_id, user_id, text)
        
        # Only answer if provoked
        if "@บอท" in text or "@bot" in text.lower():
            if "สรุป" in text:
                history = get_group_history(group_id)
                chat_log = "\\n".join([f"User {u[-4:]}: {m}" for u, m in history])
                prompt = f"นี่คือประวัติแชทกลุ่มล่าสุด: \\n{chat_log}\\n ช่วยสรุปให้ฟังหน่อยว่าคุยเรื่องอะไรกันบ้าง"
                send_hermes_response(user_id, event.reply_token, prompt)
            else:
                send_hermes_response(user_id, event.reply_token, text)
        return
        
    # Standard Private Message
    send_hermes_response(user_id, event.reply_token, text)

@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):
    if hasattr(event.source, 'group_id'): return # Ignore images in groups for now
    user_id = event.source.user_id
    line_bot_api.push_message(user_id, TextSendMessage(text="📸 ขอใช้สายตาดูรูปแปปนึงนะครับ..."))
    
    content = line_bot_api.get_message_content(event.message.id)
    image_bytes = b"".join([chunk for chunk in content.iter_content()])
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    
    vision_description = analyze_image_base64(base64_image)
    fake_user_message = (
        f"[คำบรรยายภาพสลิป/บิล: {vision_description}]\n"
        "กฎในการวิเคราะห์สลิปของฉัน (ชื่อจริงคือ 'ปุณยวัจน์'):\n"
        "1. ส่วนใหญ่สลิปที่ฉันส่งมาคือ 'รายจ่าย'\n"
        "2. ให้ดูชื่อ 'ผู้โอน' และ 'ผู้รับโอน' ถ้า 'ปุณยวัจน์' เป็นผู้รับเงิน ถือว่าเป็น 'รายรับ' แต่ถ้าเป็นผู้โอน หรือเป็นบิลซื้อของทั่วไป ถือว่าเป็น 'รายจ่าย'\n"
        "ช่วยสรุปให้ฟังหน่อยว่าสลิปนี้คืออะไร และถ้าเป็น 'รายจ่าย' ให้ใช้เครื่องมือ record_expense บันทึกบัญชีให้ฉันด้วย (ถ้าเป็นรายรับ แค่สรุปแจ้งให้ทราบก็พอ)"
    )
    
    send_hermes_response(user_id, event.reply_token, fake_user_message)

@handler.add(MessageEvent, message=AudioMessage)
def handle_audio_message(event):
    user_id = event.source.user_id
    line_bot_api.push_message(user_id, TextSendMessage(text="🎤 กำลังถอดรหัสเสียงของคุณครับ..."))
    
    content = line_bot_api.get_message_content(event.message.id)
    m4a_path = os.path.join(STATIC_DIR, f"{event.message.id}.m4a")
    wav_path = os.path.join(STATIC_DIR, f"{event.message.id}.wav")
    
    with open(m4a_path, "wb") as f:
        for chunk in content.iter_content():
            f.write(chunk)
            
    if convert_m4a_to_wav(m4a_path, wav_path):
        transcribed_text = transcribe_audio(wav_path)
        prompt = f"[ฉันพูดด้วยเสียงมาว่า: '{transcribed_text}'] กรุณาตอบกลับสิ่งที่ฉันพูด"
        # Request Audio Reply!
        send_hermes_response(user_id, event.reply_token, prompt, is_audio_reply=True)
    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="ขออภัย มีปัญหาในการแปลงไฟล์เสียงครับ"))

@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    user_id = event.source.user_id
    title = event.message.title or "ไม่มีชื่อสถานที่"
    address = event.message.address
    lat = event.message.latitude
    lng = event.message.longitude
    
    # SAVE Location to Database persistently!
    update_user_location(user_id, address, lat, lng)
    
    prompt = f"[ฉันส่งพิกัดแผนที่มาให้คุณ: ชื่อ '{title}', ที่อยู่: '{address}', ละติจูด: {lat}, ลองจิจูด: {lng}] ให้คุณเป็นไกด์/นักสำรวจ บอกฉันทีว่าแถวนี้เป็นยังไง หรือใช้ web_search หาร้านอาหารน่าสนใจใกล้ๆ ฉัน"
    send_hermes_response(user_id, event.reply_token, prompt)

if __name__ == "__main__":
    import uvicorn
    import sys
    import subprocess
    import os
    import multiprocessing

    multiprocessing.freeze_support()
    
    if getattr(sys, 'frozen', False):
        print("Starting Ngrok Tunnel...")
        ngrok_path = os.path.join(sys._MEIPASS, "ngrok.exe") if hasattr(sys, '_MEIPASS') else "ngrok.exe"
        try:
            subprocess.Popen([ngrok_path, "http", "--domain=ace-lioness-instantly.ngrok-free.app", "8000"], creationflags=0x00000010)
        except Exception as e:
            print(f"Failed to start ngrok: {e}")
            
        print("Starting FastAPI Backend...")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
