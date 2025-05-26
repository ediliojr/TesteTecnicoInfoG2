import os
from twilio.rest import Client

twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_whatsapp_from = "whatsapp:+14155238886"

client = Client(twilio_sid, twilio_token)


def send_whatsapp_message(to_number: str, message: str):
    message = client.messages.create(
        body=message, from_=twilio_whatsapp_from, to=f"whatsapp:{to_number}"
    )
    return message.sid
