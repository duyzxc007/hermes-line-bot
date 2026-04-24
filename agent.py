import os
import sqlite3
import pytz
from datetime import datetime
from dotenv import load_dotenv
import contextvars

from langchain_openai import ChatOpenAI
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.agents import initialize_agent, AgentType
from langchain_core.tools import tool
from langchain.memory import ConversationBufferWindowMemory

load_dotenv()

bkk_tz = pytz.timezone('Asia/Bangkok')

# 1. Context variable to hold the user_id for the current request
current_user_id = contextvars.ContextVar("current_user_id", default="")

# 2. Setup Vector Database (Chroma) for RAG Memory
DB_DIR = "./chroma_db"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vector_store = Chroma(embedding_function=embeddings, persist_directory=DB_DIR)

# 3. Setup SQLite Database for Expenses and User Profiles
EXPENSE_DB = "expenses.db"

def init_db():
    conn = sqlite3.connect(EXPENSE_DB)
    c = conn.cursor()
    # New Table for Location Persistence (Multi-Tenant Profile)
    c.execute('''CREATE TABLE IF NOT EXISTS users_profile
                 (user_id TEXT PRIMARY KEY,
                  display_name TEXT,
                  last_address TEXT,
                  last_lat REAL,
                  last_lng REAL,
                  updated_at DATETIME)''')
    
    # Try to add display_name if it doesn't exist (migration)
    try:
        c.execute("ALTER TABLE users_profile ADD COLUMN display_name TEXT")
    except:
        pass
        
    conn.commit()
    conn.close()

init_db()

def update_user_location(user_id: str, address: str, lat: float, lng: float):
    """Helper for main.py to save the user's latest location."""
    now_str = datetime.now(bkk_tz).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(EXPENSE_DB)
    c = conn.cursor()
    c.execute('''INSERT INTO users_profile (user_id, last_address, last_lat, last_lng, updated_at) 
                 VALUES (?, ?, ?, ?, ?) 
                 ON CONFLICT(user_id) DO UPDATE SET 
                    last_address=excluded.last_address,
                    last_lat=excluded.last_lat,
                    last_lng=excluded.last_lng,
                    updated_at=excluded.updated_at
              ''', (user_id, address, lat, lng, now_str))
    conn.commit()
    conn.close()

def get_user_profile(user_id: str):
    """Retrieves the user's display name and last known location tuple."""
    conn = sqlite3.connect(EXPENSE_DB)
    c = conn.cursor()
    c.execute("SELECT display_name, last_address, last_lat, last_lng FROM users_profile WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row

# --- Tools Definition ---

@tool
def set_my_name(name: str) -> str:
    """Useful for when the user tells you their name. You will log and remember their name."""
    uid = current_user_id.get()
    conn = sqlite3.connect(EXPENSE_DB)
    c = conn.cursor()
    c.execute("INSERT INTO users_profile (user_id, display_name) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET display_name=?", (uid, name, name))
    conn.commit()
    conn.close()
    return f"Successfully saved name as: {name}"

@tool
def save_personal_data(text: str) -> str:
    """Useful for when you need to remember or save personal information, notes, or facts about ANY user."""
    uid = current_user_id.get()
    
    # Find out their name
    profile = get_user_profile(uid)
    name = profile[0] if (profile and profile[0]) else "คนในครอบครัว"
    
    tagged_text = f"[บันทึกโดย {name}]: {text}"
    
    # Save with user_id metadata but we won't strictly enforce it on search, making it shared memory!
    vector_store.add_texts(texts=[tagged_text], metadatas=[{"user_id": uid, "name": name}])
    return f"Successfully saved the personal information in the family database: '{tagged_text}'"

@tool
def search_personal_data(query: str) -> str:
    """Useful for when you need to answer questions about ANY user's past, notes, or things they told you to remember."""
    try:
        # Search global RAG without user_id filter! Shared mind!
        results = vector_store.similarity_search(query, k=5)
        if not results:
            return "ไม่พบข้อมูลความจำใดๆ ที่ตรงกับข้อค้นหานี้เลย"
        
        docs = "\n".join([f"- {doc.page_content}" for doc in results])
        return f"นี่คือประวัติความจำ (ที่ระบุด้วยป้ายชื่อว่าใครเป็นคนจด) ที่ฉันหาเจอจากข้อมูลส่วนกลางของตู้เซฟ:\n{docs}"
    except Exception as e:
        return f"Memory search error: {str(e)}"

@tool(return_direct=True)
def record_expense(data: str) -> str:
    """Useful for recording the user's expenses or when they tell you they bought something. 
    data MUST be a comma-separated string exactly like "item,amount,category".
    Example: "กาแฟ,80,ค่าอาหาร" """
    parts = [p.strip() for p in data.split(',')]
    if len(parts) != 3:
        return "Error: You must provide exactly 3 values separated by commas: item,amount,category"
    
    item, amount_str, category = parts
    try:
        amount = float(amount_str)
    except:
        return "Error: amount must be a valid number"

    uid = current_user_id.get()
    now_str = datetime.now(bkk_tz).strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect(EXPENSE_DB)
    c = conn.cursor()
    c.execute("INSERT INTO expenses (user_id, item, amount, category, timestamp) VALUES (?, ?, ?, ?, ?)",
              (uid, item, amount, category, now_str))
    conn.commit()
    conn.close()
    
    # MAGIC STRING used by main.py to send a Flex Message
    return f"FLEX_EXPENSE:{amount}|{category}|{item}"

@tool
def summarize_expenses(period: str) -> str:
    """Useful for when the user asks for a summary of their expenses. 
    period can be 'today', 'month', or 'all'."""
    uid = current_user_id.get()
    now = datetime.now(bkk_tz)
    
    conn = sqlite3.connect(EXPENSE_DB)
    c = conn.cursor()
    
    if period == "today":
        date_str = now.strftime("%Y-%m-%d")
        c.execute("SELECT sum(amount) FROM expenses WHERE user_id=? AND timestamp LIKE ?", (uid, f"{date_str}%"))
    elif period == "month":
        month_str = now.strftime("%Y-%m")
        c.execute("SELECT sum(amount) FROM expenses WHERE user_id=? AND timestamp LIKE ?", (uid, f"{month_str}%"))
    else:
        c.execute("SELECT sum(amount) FROM expenses WHERE user_id=?", (uid,))
        
    total = c.fetchone()[0]
    conn.close()
    
    if total is None:
        return "You have no recorded expenses for this period."
    return f"Total expenses for {period} is {total} บาท."

@tool
def set_reminder(data: str) -> str:
    """Useful for when the user asks you to remind them about something at a specific time.
    data MUST be a comma-separated string exactly like "YYYY-MM-DD HH:MM:SS,message".
    Example: "2026-04-21 09:00:00,ประชุมเช้า" """
    parts = data.split(',', 1)
    if len(parts) != 2:
        return "Error: You must provide exactly 2 values separated by comma: time_str,message"
    
    time_str = parts[0].strip()
    message = parts[1].strip()

    from scheduler import add_reminder
    uid = current_user_id.get()
    try:
        job_id = add_reminder(time_str, message, uid)
        return f"Successfully set a reminder for '{time_str}'. I will remind you: {message}"
    except Exception as e:
        return f"Failed to set reminder. Error: {str(e)}."

@tool
def web_search(query: str) -> str:
    """Useful for when you need to search the Internet for current events, weather, news, or general facts that you don't know."""
    try:
        # Using ddgs library directly for better reliability and avoiding Langchain deprecation issues
        from ddgs import DDGS
        # backend='html' prevents the DuckDuckGo API SPAM cache poisoning issue for Thai keywords
        results = DDGS().text(query, backend="html", region="th-th", max_results=5)
        if not results:
            return "No internet search results found."
        
        formatted = []
        for r in results:
            formatted.append(f"Title: {r.get('title', '')}\nSnippet: {r.get('body', '')}")
            
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Internet Search failed: {str(e)}"

@tool
def get_stock_price(symbol: str) -> str:
    """Useful for getting the REAL-TIME or LATEST stock price and financial data.
    Input must be a stock symbol (e.g., 'PR9', 'PTT', 'AAPL'). 
    If it's a Thai stock, just send the symbol like 'PR9'."""
    try:
        import yfinance as yf
        symbol = symbol.strip().upper()
        # Auto append .BK for Thai stocks if no suffix is provided
        if "." not in symbol:
            symbol = f"{symbol}.BK"
            
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info or "currentPrice" not in info:
            # Fallback for non-Thai stocks if .BK was wrongly appended
            if symbol.endswith(".BK"):
                symbol_us = symbol.replace(".BK", "")
                ticker = yf.Ticker(symbol_us)
                info = ticker.info
                if not info or "currentPrice" not in info:
                    return f"ไม่พบข้อมูลราคาหุ้นแบบ Real-time สำหรับ {symbol_us}"
                symbol = symbol_us
            else:
                return f"ไม่พบข้อมูลราคาหุ้นแบบ Real-time สำหรับ {symbol}"
                
        current_price = info.get("currentPrice", "N/A")
        previous_close = info.get("regularMarketPreviousClose", "N/A")
        currency = info.get("currency", "THB")
        
        try:
            change = float(current_price) - float(previous_close)
            pct_change = (change / float(previous_close)) * 100
            change_str = f"{change:+.2f} ({pct_change:+.2f}%)"
        except:
            change_str = "N/A"
            
        name = info.get("longName", symbol)
        
        return f"ข้อมูลหุ้น {name} ({symbol}):\nราคาปัจจุบัน: {current_price} {currency}\nการเปลี่ยนแปลง: {change_str}\n(ดึงข้อมูลล่าสุดแบบ Real-time/Delayed 15m)"
    except Exception as e:
        return f"Stock fetch error: {str(e)}"

@tool(return_direct=True)
def generate_image(prompt: str) -> str:
    """Useful for when the user asks you to draw or generate an image. 
    prompt MUST be a descriptive English prompt describing the scene visually."""
    import urllib.parse
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?nologo=true"
    
    # MAGIC STRING used by main.py to send an ImageMessage
    return f"IMAGE_GEN:{image_url}"

@tool
def get_weather(dummy: str) -> str:
    """Useful for getting the LIVE current local weather conditions of the user. Pass any string as input (e.g. 'now')."""
    uid = current_user_id.get()
    prof = get_user_profile(uid)
    if not prof or not prof[2]:
        return "ไม่สามารถเช็คได้ กรุณาบอกให้ผู้ใช้ 'กดแชร์ Location' ในแชทก่อน เพื่อลงทะเบียนพิกัดบ้าน!"
    
    lat, lng = prof[2], prof[3]
    import requests
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current=temperature_2m,relative_humidity_2m,precipitation,weather_code"
        res = requests.get(url).json()
        
        current = res.get('current', {})
        if not current:
            return "ไม่สามารถดึงข้อมูลอากาศได้ในขณะนี้"
            
        temp = current.get('temperature_2m')
        humid = current.get('relative_humidity_2m')
        rain = current.get('precipitation')
        code = current.get('weather_code')
        
        # WMO Weather interpretation
        w_map = {
            0: "Clear sky (ท้องฟ้าแจ่มใส ไม่มีเมฆ)",
            1: "Mainly clear (มีเมฆบางส่วน)",
            2: "Partly cloudy (มีเมฆเป็นส่วนมาก)",
            3: "Overcast (มืดครึ้ม)",
            45: "Fog (มีหมอกหนา)",
            51: "Light Drizzle (ฝนตกปรอยๆ)",
            61: "Rain (ฝนตกปานกลาง)",
            63: "Heavy Rain (ฝนตกหนัก)",
            65: "Heavy intense rain (ฝนตกหนักมาก)",
            80: "Rain showers (ฝนตกเป็นหย่อมๆ)",
            95: "Thunderstorm (พายุฝนฟ้าคะนอง)",
            96: "Thunderstorm with hail (พายุฝนฟ้าคะนองพร้อมลูกเห็บ)"
        }
        desc = w_map.get(code, "ไม่ทราบสภาพ (Unknown condition)")
        
        return f"พิกัดล่าสุดที่อยู่: (Lat:{lat}, Lng:{lng})\nอุณหภูมิ: {temp}°C\nความชื้น: {humid}%\nปริมาณน้ำฝน: {rain}mm\nสภาพอากาศ: {desc}"
    except Exception as e:
        return f"การเชื่อมต่อระบบอากาศล้มเหลว: {str(e)}"

# Tools List
tools = [set_my_name, save_personal_data, search_personal_data, record_expense, summarize_expenses, set_reminder, web_search, get_stock_price, generate_image, get_weather]

# --- LLM and Agent Factory (Multi-Tenant) ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

llm = ChatOpenAI(
    model="nousresearch/hermes-3-llama-3.1-405b", 
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.3,
    max_tokens=2048
)

# Global dictionary to map User ID -> Their specific Agent Executor
agent_cache = {}

def get_or_create_agent(user_id: str):
    if user_id in agent_cache:
        return agent_cache[user_id]
        
    # Create Independent Memory for this user!
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history", 
        k=5, 
        return_messages=True
    )

    agent_kwargs = {
        "system_message": "You are Hermes, an extremely smart personal assistant. You are talking to a user in Thailand timezone. "
                          "Always use natural Thai language to reply. "
                          "***CRITICAL INSTRUCTION***: If the user sends you a sentence or text in ANY language other than Thai, "
                          "you must automatically translate it into beautiful Thai language as part of your answer! "
                          "You have access to tools. Be helpful and polite."
    }

    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        agent_kwargs=agent_kwargs,
        verbose=True,
        handle_parsing_errors=True
    )
    
    agent_cache[user_id] = agent
    return agent

def ask_hermes(message: str, user_id: str) -> str:
    """Process a message through the agent with full Multi-Tenant awareness."""
    token = current_user_id.set(user_id)
    
    try:
        # Get isolation logic:
        user_agent = get_or_create_agent(user_id)
        
        # 1. Base Time Context
        prompt_context = f"[System Time (Thailand): {datetime.now(bkk_tz).strftime('%Y-%m-%d %H:%M:%S')}]"
        
        # 2. Profile Context
        prof = get_user_profile(user_id)
        if prof:
            name, last_addr, last_lat, last_lng = prof
            if name:
                prompt_context += f" [User Name (Current Speaker): {name}]"
                
                # Apply Custom Persona Instructions for Duy
                if name.strip().lower() in ["ดุ๊ย", "duy"]:
                    prompt_context += (
                        "\n[CRITICAL PERSONA OVERRIDE]: "
                        "1. โทน: Professional + เป็นกันเองแบบ Senior Engineer (No fluff, รับมุกตลกได้). "
                        "2. คุณถูกบังคับให้เริ่มต้นคำตอบด้วย 'Executive Summary' เสมอ! "
                        "3. คำตอบต้อง 'Decision-ready' (เสมอ Option + Recommendation + Reason Trade-off). "
                        "4. ถ้าบรรยายข้อมูลซับซ้อน ให้ใช้ Framework, Checklist, หรือ ตาราง. "
                        "5. กฎเหล็ก: ถ้าไม่ชัวร์ให้บอก 'ไม่แน่ใจ' ห้ามมั่ว และเสนอวิธีเช็ก!"
                    )
            
            if last_addr:
                prompt_context += f" [User's current known location (Address, Lat, Lng): {last_addr} ({last_lat},{last_lng})]"
            
        # 3. Assemble Full Prompt
        prompt = f"{prompt_context} \nUser says: {message}"
        
        response = user_agent.run(prompt)
        return response
    except Exception as e:
        return f"ขออภัย เกิดข้อผิดพลาดในการประมวลผล: {str(e)}"
    finally:
        current_user_id.reset(token)

if __name__ == "__main__":
    print("Testing Agent. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        reply = ask_hermes(user_input, "TEST_USER_123")
        print(f"Hermes: {reply}")
