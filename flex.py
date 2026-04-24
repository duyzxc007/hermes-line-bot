from linebot.models import FlexSendMessage
import json

def create_welcome_checklist_flex() -> FlexSendMessage:
    """Returns a nicely formatted Flex Message acting as an Onboarding Checklist."""
    bubble_string = """
    {
      "type": "bubble",
      "header": {
        "type": "box",
        "layout": "vertical",
        "backgroundColor": "#F4F6F8",
        "contents": [
          {
            "type": "text",
            "text": "✨ ยินดีต้อนรับสู่ HERMES ✨",
            "weight": "bold",
            "color": "#1DB446",
            "size": "md",
            "align": "center"
          }
        ]
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "spacing": "md",
        "contents": [
          {
            "type": "text",
            "text": "ผมคือ AI ผู้ช่วยอัจฉริยะส่วนตัวของคุณ เพื่อให้ผมจดจำข้อมูลและแยกบัญชีรายจ่ายของคุณได้อย่างถูกต้อง รบกวนกดปุ่มเพื่อแนะนำตัวหน่อยครับ 👇",
            "wrap": true,
            "size": "sm",
            "color": "#333333"
          },
          {
            "type": "separator",
            "margin": "md"
          },
          {
            "type": "button",
            "style": "primary",
            "color": "#0367D3",
            "margin": "md",
            "action": {
              "type": "postback",
              "label": "1️⃣ แจ้งชื่อเล่นของคุณ",
              "data": "ignore",
              "inputOption": "openKeyboard",
              "fillInText": "ฉันต้องการตั้งชื่อของฉันคือ: "
            }
          },
          {
            "type": "button",
            "style": "secondary",
            "margin": "sm",
            "action": {
              "type": "postback",
              "label": "2️⃣ แจ้งข้อมูล/สิ่งที่ชอบ",
              "data": "ignore",
              "inputOption": "openKeyboard",
              "fillInText": "ช่วยจำข้อมูลส่วนตัวของฉัน: "
            }
          },
          {
            "type": "button",
            "style": "link",
            "margin": "sm",
            "action": {
              "type": "message",
              "label": "ดูคู่มือการใช้งานบอททั้งหมด",
              "text": "เมนูช่วยเหลือ"
            }
          }
        ]
      }
    }
    """
    flex_dict = json.loads(bubble_string)
    return FlexSendMessage(alt_text="ยินดีต้อนรับสู่ Hermes! กรุณาแนะนำตัวเพื่อเริ่มต้น", contents=flex_dict)

def get_expense_receipt_flex(amount: str, category: str, item: str, date: str) -> FlexSendMessage:
    """Returns a rich Flex Message Receipt for expense logging."""
    bubble_string = f"""
    {{
      "type": "bubble",
      "size": "mega",
      "header": {{
        "type": "box",
        "layout": "vertical",
        "contents": [
          {{
            "type": "box",
            "layout": "vertical",
            "contents": [
              {{
                "type": "text",
                "text": "EXPENSE RECEIPT",
                "color": "#ffffff66",
                "size": "sm"
              }},
              {{
                "type": "text",
                "text": "{category}",
                "color": "#ffffff",
                "size": "xl",
                "flex": 4,
                "weight": "bold"
              }}
            ]
          }}
        ],
        "paddingAll": "20px",
        "backgroundColor": "#0367D3",
        "spacing": "md",
        "height": "100px",
        "paddingTop": "22px"
      }},
      "body": {{
        "type": "box",
        "layout": "vertical",
        "contents": [
          {{
            "type": "text",
            "text": "บันทึกรายจ่ายเรียบร้อย",
            "weight": "bold",
            "size": "md",
            "margin": "md"
          }},
          {{
            "type": "text",
            "text": "{item}",
            "size": "xxs",
            "color": "#aaaaaa",
            "wrap": True
          }},
          {{
            "type": "separator",
            "margin": "xxl"
          }},
          {{
            "type": "box",
            "layout": "horizontal",
            "margin": "xxl",
            "contents": [
              {{
                "type": "text",
                "text": "AMOUNT",
                "size": "sm",
                "color": "#555555",
                "flex": 0
              }},
              {{
                "type": "text",
                "text": "฿ {amount}",
                "size": "sm",
                "color": "#111111",
                "align": "end"
              }}
            ]
          }},
          {{
            "type": "box",
            "layout": "horizontal",
            "contents": [
              {{
                "type": "text",
                "text": "DATE",
                "size": "sm",
                "color": "#555555",
                "flex": 0
              }},
              {{
                "type": "text",
                "text": "{date}",
                "size": "sm",
                "color": "#111111",
                "align": "end"
              }}
            ]
          }}
        ]
      }}
    }}
    """
    flex_dict = json.loads(bubble_string)
    return FlexSendMessage(alt_text="Expense Receipt", contents=flex_dict)

def create_help_flex_message() -> FlexSendMessage:
    """Returns a nicely formatted Flex Message explaining bot capabilities."""
    bubble_string = """
    {
      "type": "bubble",
      "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "HERMES ASSISTANT",
            "weight": "bold",
            "color": "#1DB446",
            "size": "sm"
          },
          {
            "type": "text",
            "text": "คู่มือการใช้งานบอท 🤖",
            "weight": "bold",
            "size": "xl",
            "margin": "md"
          }
        ]
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "ลิสต์ฟังก์ชันที่สามารถสั่งได้:",
            "weight": "bold",
            "size": "md",
            "color": "#333333"
          },
          {
            "type": "separator",
            "margin": "md"
          },
          {
            "type": "box",
            "layout": "vertical",
            "margin": "md",
            "spacing": "sm",
            "contents": [
              {
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                  { "type": "text", "text": "✅", "size": "sm", "flex": 1 },
                  { "type": "text", "text": "คุยโต้ตอบและจำข้อมูลดุจมนุษย์", "wrap": true, "color": "#666666", "size": "sm", "flex": 7 }
                ]
              },
              {
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                  { "type": "text", "text": "✅", "size": "sm", "flex": 1 },
                  { "type": "text", "text": "พยากรณ์อากาศจากพิกัด GPS", "wrap": true, "color": "#666666", "size": "sm", "flex": 7 }
                ]
              },
              {
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                  { "type": "text", "text": "✅", "size": "sm", "flex": 1 },
                  { "type": "text", "text": "ลงบัญชีรายจ่ายอัตโนมัติและสรุปยอด", "wrap": true, "color": "#666666", "size": "sm", "flex": 7 }
                ]
              },
              {
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                  { "type": "text", "text": "✅", "size": "sm", "flex": 1 },
                  { "type": "text", "text": "แปลภาษาและค้นหาข้อมูลบนอินเทอร์เน็ต", "wrap": true, "color": "#666666", "size": "sm", "flex": 7 }
                ]
              },
              {
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                  { "type": "text", "text": "✅", "size": "sm", "flex": 1 },
                  { "type": "text", "text": "วาดภาพตามสั่งจากอาร์ตพรอมต์", "wrap": true, "color": "#666666", "size": "sm", "flex": 7 }
                ]
              },
              {
                "type": "box",
                "layout": "baseline",
                "spacing": "sm",
                "contents": [
                  { "type": "text", "text": "✅", "size": "sm", "flex": 1 },
                  { "type": "text", "text": "วิเคราะห์สลิปและรูปภาพด้วย Vision", "wrap": true, "color": "#666666", "size": "sm", "flex": 7 }
                ]
              }
            ]
          }
        ]
      },
      "footer": {
        "type": "box",
        "layout": "vertical",
        "spacing": "sm",
        "contents": [
          {
            "type": "button",
            "style": "link",
            "height": "sm",
            "action": {
              "type": "message",
              "label": "ลองให้วาดรูปเลย",
              "text": "วาดรูปภาพ"
            }
          }
        ],
        "flex": 0
      }
    }
    """
    flex_dict = json.loads(bubble_string)
    return FlexSendMessage(alt_text="คู่มือการใช้งานบอท Hermes", contents=flex_dict)

def get_expense_summary_flex(period_name: str, total_amount: str, breakdown: list = None) -> FlexSendMessage:
    """Returns a Yellow/Red rich Flex Message for expense summary with optional breakdown."""
    
    flex_dict = {
      "type": "bubble",
      "size": "mega",
      "header": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "EXPENSE SUMMARY",
            "color": "#ffffff66",
            "size": "sm",
            "weight": "bold"
          },
          {
            "type": "text",
            "text": "สรุปยอดรายจ่าย",
            "color": "#ffffff",
            "size": "xl",
            "weight": "bold"
          }
        ],
        "paddingAll": "20px",
        "backgroundColor": "#FFC107",
        "spacing": "md"
      },
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "text",
            "text": "ยอดรวมหนี้สิน/รายจ่าย",
            "weight": "bold",
            "size": "md",
            "margin": "md",
            "color": "#d32f2f"
          },
          {
            "type": "separator",
            "margin": "lg"
          }
        ]
      }
    }
    
    body_contents = flex_dict["body"]["contents"]
    
    # Inject Breakdown if exists
    if breakdown and len(breakdown) > 0:
        breakdown_box = {
            "type": "box",
            "layout": "vertical",
            "margin": "lg",
            "spacing": "sm",
            "contents": []
        }
        for name, amount in breakdown:
            breakdown_box["contents"].append({
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": f"👤 {name}",
                        "size": "sm",
                        "color": "#555555",
                        "flex": 2
                    },
                    {
                        "type": "text",
                        "text": f"฿ {amount:,.2f}",
                        "size": "sm",
                        "color": "#111111",
                        "align": "end",
                        "weight": "bold",
                        "flex": 1
                    }
                ]
            })
        body_contents.append(breakdown_box)
        body_contents.append({
            "type": "separator",
            "margin": "lg"
        })
        
    # Append Period and Total Result
    body_contents.append({
        "type": "box",
        "layout": "horizontal",
        "margin": "lg",
        "contents": [
            {
            "type": "text",
            "text": "PERIOD",
            "size": "sm",
            "color": "#999999",
            "weight": "bold"
            },
            {
            "type": "text",
            "text": period_name,
            "size": "sm",
            "color": "#111111",
            "align": "end",
            "weight": "bold"
            }
        ]
    })
    
    body_contents.append({
        "type": "box",
        "layout": "horizontal",
        "margin": "md",
        "contents": [
            {
            "type": "text",
            "text": "TOTAL",
            "size": "sm",
            "color": "#999999",
            "weight": "bold"
            },
            {
            "type": "text",
            "text": f"฿ {total_amount}",
            "size": "xl",
            "color": "#d32f2f",
            "align": "end",
            "weight": "bold"
            }
        ]
    })
    
    return FlexSendMessage(alt_text="สรุปบัญชีรายจ่าย", contents=flex_dict)

