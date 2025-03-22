import os.path
import base64
import json
import time
import random
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import telebot

# טוקן הבוט של טלגרם ומזהה הערוץ
TELEGRAM_BOT_TOKEN = '7500097967:AAEDwdqqQWFtWLSzqxye8P2pyQoTBjegzXg'
CHANNEL_ID = '-1002357300753'
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# אם משנים את SCOPES, יש למחוק את הקובץ token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# רשימה של טקסטים רנדומליים עם הנעה לפעולה ואומוג'י
call_to_action_texts = [
    "📢 **קנה עכשיו!**",
    "🔥 **עבור למבצע!**",
    "🌟 **קנה עוד היום!**",
    "✨ **מבצע מיוחד!**",
    "🚀 **הזדרז לרכוש!**",
    "🛒 **קנה בקליק!**",
    "🔔 **הזמן עכשיו!**",
    "🎉 **נצל את ההזדמנות!**",
    "💥 **מבצע מדהים!**",
    "🛍️ **קנה במחיר משתלם!**",
    "⚡ **מבצע מוגבל!**",
    "🏷️ **הנחות ענק!**",
    "🚨 **רכוש עכשיו ותחסוך!**",
    "💸 **מחיר ללא תחרות!**",
    "🆓 **משלוח חינם בקנייה מעל סכום מסוים!**",
    "📦 **הזמן עכשיו וקבל משלוח חינם!**",
    "💎 **מבצע ייחודי רק להיום!**",
    "🛒 **קנה עכשיו וקבל מתנה!**",
    "🔥 **מבצע חם!**",
    "🎁 **קנה כעת והפתע מישהו מיוחד!**"
]

# רשימה של טקסטים רנדומליים לקישור
link_texts = [
    "קנה עכשיו",
    "עבור לרכישה",
    "למבצע",
    "קנה כאן",
    "הזמן עכשיו",
    "לרכישה",
    "לקניה",
    "קבל הצעה",
    "לחץ כאן",
    "עבור להצעה"
]

# פונקציה לבחירת טקסט רנדומלי עם הנעה לפעולה
def get_random_call_to_action():
    return random.choice(call_to_action_texts)

# פונקציה לבחירת טקסט רנדומלי עבור הקישור
def get_random_link_text(link):
    link_text = random.choice(link_texts)
    return f"[{link_text}]({link})"

# פונקציה לשליחת הודעה לטלגרם
def send_message_to_telegram(text, images, link, is_new=False):
    try:
        # יצירת ההודעה עם הטקסט והקישור
        if is_new:
            message = f"🎉 **מבצע חדש נכנס!** 🎉\n\n{text}\n\n{get_random_call_to_action()} {get_random_link_text(link)}"
        else:
            message = f"{text}\n\n{get_random_call_to_action()} {get_random_link_text(link)}"
        bot.send_message(CHANNEL_ID, message, parse_mode='Markdown')
        for image in images:
            # שליחת התמונה עם הטקסט והקישור
            caption = f"{get_random_call_to_action()} {get_random_link_text(link)}"
            bot.send_photo(CHANNEL_ID, image, caption=caption, parse_mode='Markdown')
        print("Message sent to Telegram")
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Failed to send message: {e}")

# פונקציה לקבלת שירות ה-Gmail
def get_gmail_service():
    creds = None
    # הקובץ token.json מאחסן את האסימונים של המשתמש ונוצר אוטומטית כאשר תהליך האישור מסתיים בפעם הראשונה.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # אם אין אסימונים (תקפים), אפשר למשתמש להיכנס.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'C:\ksp.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # שמירת האסימונים להפעלה הבאה
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

# פונקציה לקבלת רשימת הודעות
def list_messages(service, user_id='me'):
    query = 'today@kspmail.co.il'
    results = service.users().messages().list(userId=user_id, q=query).execute()
    messages = results.get('messages', [])
    print(f"Found {len(messages)} messages from today@kspmail.co.il")
    return messages

# פונקציה לקבלת תוכן הודעה
def get_message(service, user_id, msg_id):
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    payload = message['payload']
    headers = payload.get('headers')
    parts = payload.get('parts')
    data = ''
    images = []

    # אם להודעה יש חלקים שונים, מוצאים את ה-HTML
    if parts:
        for part in parts:
            if part['mimeType'] == 'text/html':
                data = part['body']['data']
                break

    # אם יש נתונים, מפענחים את תוכן ה-HTML
    if data:
        msg_str = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')
        soup = BeautifulSoup(msg_str, 'html.parser')
        text = soup.get_text()
        images = [img['src'] for img in soup.find_all('img')]
        return text, images
    return 'No message content found.', []

# הפונקציה הראשית שמבצעת את כל התהליך
def main():
    service = get_gmail_service()
    processed_messages = set()
    message_queue = []
    
    while True:
        print("Checking for new messages...")
        messages = list_messages(service)
        
        for msg in messages:
            if msg['id'] not in processed_messages:
                print(f"New message found with ID: {msg['id']}")
                msg_content, images = get_message(service, 'me', msg['id'])
                print(f"Text content: {msg_content[:100]}...")  # הדפסת תחילת הטקסט כדי לא להעמיס על הקונסול
                print(f"Found {len(images)} images")
                send_message_to_telegram(msg_content, images, 'https://ksp.co.il/item/F17786AX', is_new=True)
                processed_messages.add(msg['id'])
                time.sleep(10)  # השהיה של 10 שניות בין כל הודעה כדי למנוע עומס

        if message_queue:
            print("Sending next message from the queue...")
            msg_content, images = message_queue.pop(0)
            send_message_to_telegram(msg_content, images, 'https://ksp.co.il/item/F17786AX')
            time.sleep(10)  # השהיה של 10 שניות בין כל הודעה כדי למנוע עומס

        print("Waiting for 5 minutes before checking again...")
        time.sleep(300)  # השהיה של 5 דקות לפני בדיקה נוספת

if __name__ == '__main__':
    main()
