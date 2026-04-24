import os
from linebot import LineBotApi, WebhookHandler
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    print("WARNING: LINE Credentials not found in .env file.")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def push_message_to_user(user_id: str, message_text: str):
    """Utility function to send a proactive message to a user."""
    from linebot.models import TextSendMessage
    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=message_text))
        print(f"Pushed message to {user_id}: {message_text}")
    except Exception as e:
        print(f"Failed to push message: {e}")
