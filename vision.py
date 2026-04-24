import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize OpenAI Client pointing to OpenRouter
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=OPENROUTER_API_KEY,
)

def analyze_image_base64(base64_image: str) -> str:
    """Sends a base64 encoded image to a Vision model and returns the description."""
    try:
        response = client.chat.completions.create(
            # Use GPT-4o-mini for better Thai OCR and avoiding strict PII blocks on bank slips
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "นี่คือรูปภาพอะไร? หากเป็นสลิปโอนเงิน (Bank slip) หรือใบเสร็จ กรุณาดึงรายละเอียด: ยอดเงิน, วันที่, ลำดับเวลา, ชื่อ-นามสกุล 'ผู้โอน' และ 'ผู้รับโอน' แบบละเอียด (เพื่อใช้แยกแยะรายรับ/รายจ่ายของ ปุณยวัจน์)"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            }
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"ขออภัย ระบบอ่านภาพขัดข้อง: {str(e)}"
