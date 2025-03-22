import os.path
import base64
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'C:\ksp.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)
    return service

def list_messages(service, user_id='me'):
    query = 'barshlomo95@gmail.com'
    results = service.users().messages().list(userId=user_id, q=query).execute()
    messages = results.get('messages', [])
    print(f"Found {len(messages)} messages from today@kspmail.co.il")
    return messages

def get_message(service, user_id, msg_id):
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    payload = message['payload']
    headers = payload.get('headers')
    parts = payload.get('parts')
    data = ''
    images = []

    if parts:
        for part in parts:
            if part['mimeType'] == 'text/html':
                data = part['body']['data']
                break

    if data:
        msg_str = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')
        soup = BeautifulSoup(msg_str, 'html.parser')
        text = soup.get_text()
        images = [img['src'] for img in soup.find_all('img')]
        return text, images
    return 'No message content found.', []

def main():
    service = get_gmail_service()
    messages = list_messages(service)
    email_list = []

    for msg in messages:
        print(f"Processing message ID: {msg['id']}")
        msg_content, images = get_message(service, 'me', msg['id'])
        print(f"Text content: {msg_content[:100]}...")  # הדפסת תחילת הטקסט כדי לא להעמיס על הקונסול
        print(f"Found {len(images)} images")
        # יצירת מילון עם המידע על המייל
        email_data = {
            'id': msg['id'],
            'text': msg_content,
            'images': images,
            'link': 'https://ksp.co.il/item/F4388AX'
        }
        email_list.append(email_data)

    # שמירת המידע בפורמט JSON לקובץ
    with open('emails.json', 'w', encoding='utf-8') as f:
        json.dump(email_list, f, ensure_ascii=False, indent=4)

    print("All messages have been processed and saved to emails.json")

if __name__ == '__main__':
    main()
