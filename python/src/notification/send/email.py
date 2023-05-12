import smtplib, os, json
from email.message import EmailMessage

def notification(message):
    try:
        message = json.loads(message)
        pdf_fid = message["pdf_fid"]
        sender_address = os.environ.get("GMAIL_ADDRESS")
        sender_password = os.environ.get("GMAIL_PASSWORD")
        recevier_address = message["username"]
        
        msg = EmailMessage()
        msg.set_content(f'pdf file id: {pdf_fid} is now ready!')
        msg["Subject"] = "PDF Download"
        msg["From"] = sender_address
        msg["to"] = recevier_address
        
        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.starttls()
        session.login(sender_address, sender_password)
        session.send_message(msg, sender_address, recevier_address)
        session.quit()
        print("Mail sent")
        
    except Exception as err:
        print(err)
        return err
        
