import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def generate_otp():
    """Generate a 6-digit random OTP."""
    return str(random.randint(100000, 999999))

def send_otp(receiver_email, otp):
    """Send an OTP to the specified email address using Gmail SMTP."""
    sender_email = "ajeetsingh789866@gmail.com"
    sender_password = "gtpd arig stqp knpy"  # Gmail App Password (not actual Gmail login)

    subject = "Your OTP for Head_Count Miner"
    body = f"Your OTP code is: {otp}"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        return True
    except Exception as e:
        print("[Error] OTP sending failed:", e)
        return False
