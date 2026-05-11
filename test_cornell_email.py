import smtplib
from email.mime.text import MIMEText

# Your Gmail credentials
EMAIL = "oropel42408@gmail.com"
PASSWORD = "kqkcnxyzuthozonf"  # Replace with your app password (no spaces)
RECIPIENT = "oropel42408@gmail.com"     # Send to yourself

print("Testing Gmail alert system...")
print(f"From: {EMAIL}")
print(f"To: {RECIPIENT}")
print("-" * 40)

try:
    # Gmail SMTP settings
    print("Connecting to Gmail SMTP...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)
    
    # Create email
    msg = MIMEText("""
    ✅ SUCCESS! Your Lab Inventory System email alerts are working!
    
    Test Time: {current_time}
    
    You will now receive email notifications when:
    - Items go out of stock
    - Items fall below minimum stock levels
    
    This is an automated test message.
    """.format(current_time=__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    
    msg['Subject'] = "✅ Lab Inventory Alert Test - SUCCESS!"
    msg['From'] = EMAIL
    msg['To'] = RECIPIENT
    
    server.send_message(msg)
    server.quit()
    
    print("✅ Email sent successfully!")
    print(f"Check {RECIPIENT} inbox in a few moments")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    print("\nCommon fixes:")
    print("1. Did you generate an App Password? (not your regular password)")
    print("2. Did you copy the 16 characters without spaces?")
    print("3. Is 2FA enabled on your Google account? (required for app passwords)")
    print("\nGenerate app password here: https://myaccount.google.com/apppasswords")