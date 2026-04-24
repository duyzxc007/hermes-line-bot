# Hermes LINE Bot 🤖

บอท LINE อัจฉริยะที่เชื่อมต่อกับโมเดล Hermes (ผ่าน OpenRouter) พร้อมความสามารถในการดึงข้อมูลหุ้น, ค้นหาเว็บ, และจัดการฐานข้อมูลส่วนตัว

## ⚙️ ขั้นที่ 1: ตั้งค่า API Keys (Critical Step ⚠️)
**จุดนี้คนพลาดบ่อยที่สุด: ระบบจะรันไม่ขึ้น หรือบอทจะไม่ตอบ หากไม่มีไฟล์ตั้งค่ารหัสผ่าน**

ให้คัดลอกไฟล์ `.env.example` แล้วเปลี่ยนชื่อเป็น `.env` (ไม่มีชื่อข้างหน้า มีแต่จุดและตัวอักษร)
จากนั้นเปิดไฟล์ `.env` และกรอกข้อมูล API ของคุณ:

```env
# รับ API Key สำหรับโมเดล AI ได้ที่ openrouter.ai
OPENROUTER_API_KEY=ใส่_api_key_ของ_openrouter_ที่นี่

# รับ Token และ Secret ได้จากการสร้าง Messaging API ที่ developers.line.biz
LINE_CHANNEL_ACCESS_TOKEN=ใส่_token_ของ_line_ที่นี่
LINE_CHANNEL_SECRET=ใส่_secret_ของ_line_ที่นี่
```

---

## 🐳 วิธีรันผ่าน Docker (แนะนำสำหรับขึ้นเซิร์ฟเวอร์)
หากรันบนเครื่องที่มี Docker ให้เปิด Terminal ในโฟลเดอร์นี้และพิมพ์คำสั่งเดียว:
```bash
docker compose up -d --build
```
ระบบจะสร้างฐานข้อมูลถาวรไว้ที่โฟลเดอร์ `bot_data` อัตโนมัติ

---

## 💻 วิธีรันบนเครื่องใหม่ (ไม่ผ่าน Docker)
หากต้องการรันบนคอมพิวเตอร์ทั่วไป (เช่น Windows, Mac) ให้ทำตามขั้นตอนต่อไปนี้:

1. **ติดตั้ง Python**: ตรวจสอบว่าในเครื่องมี Python 3.10+ (ดาวน์โหลดจาก python.org)
2. **เปิด Terminal/Command Prompt** เข้ามาที่โฟลเดอร์โปรเจกต์
3. **สร้างและเปิดใช้งาน Virtual Environment (ทางเลือกแต่แนะนำ):**
   ```bash
   python -m venv venv
   # สำหรับ Windows:
   venv\Scripts\activate
   # สำหรับ Mac/Linux:
   source venv/bin/activate
   ```
4. **ติดตั้งไลบรารีที่จำเป็น:**
   ```bash
   pip install -r requirements.txt
   ```
5. **รันตัวบอท:**
   ```bash
   python main.py
   ```
6. **เปิดช่องทางเชื่อมโยง (Ngrok):**
   เปิด Terminal อีกหน้าต่างหนึ่ง แล้วรันคำสั่ง:
   ```bash
   ngrok http 8000
   ```
   จากนั้นนำลิงก์ `https://...` ที่ได้จาก ngrok ไปใส่ใน Webhook URL ของ LINE Developers (เติม `/webhook` ต่อท้ายด้วย)
