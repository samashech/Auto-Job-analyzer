import requests

# You must generate these via Telegram
TELEGRAM_BOT_TOKEN = "your_bot_token_here"
TELEGRAM_CHAT_ID = "your_chat_id_here"

def send_telegram_alert(message_text: str, image_path: str):
    """Sends a text message and an image to a Telegram chat."""
    
    # 1. Send the text message
    text_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(text_url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message_text})
    
    # 2. Send the image
    photo_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as image_file:
        files = {"photo": image_file}
        data = {"chat_id": TELEGRAM_CHAT_ID}
        requests.post(photo_url, data=data, files=files)
