Set WshShell = CreateObject("WScript.Shell")

' สั่งรัน Ngrok แบบซ่อนหน้าต่าง
WshShell.Run "ngrok.exe http --domain=ace-lioness-instantly.ngrok-free.app 8000", 0, False

' สั่งรันบอท Python แบบซ่อนหน้าต่าง
WshShell.Run "python -m uvicorn main:app --host 0.0.0.0 --port 8000", 0, False

Set WshShell = Nothing
