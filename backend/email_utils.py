import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

async def send_verification_code_email(to_email: str, code: str, user_name: str):
    """Send 6-digit verification code email"""
    
    # Email content
    subject = "Password Reset Code - NutriTracker"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .code-box {{ 
                background-color: #f0f8ff;
                border: 2px dashed #4CAF50;
                padding: 20px;
                text-align: center;
                margin: 20px 0;
                border-radius: 8px;
            }}
            .code {{ 
                font-size: 36px;
                font-weight: bold;
                letter-spacing: 8px;
                color: #4CAF50;
                font-family: 'Courier New', monospace;
            }}
            .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            .warning {{ background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🥗 NutriTracker</h1>
                <p style="margin: 0;">Your Health, Your Journey</p>
            </div>
            <div class="content">
                <h2>Hello {user_name},</h2>
                <p>You requested to reset your password for your NutriTracker account.</p>
                
                <p>Here is your verification code:</p>
                
                <div class="code-box">
                    <div class="code">{code}</div>
                    <p style="margin: 10px 0 0 0; color: #666; font-size: 14px;">
                        Enter this code in the app to continue
                    </p>
                </div>
                
                <div class="warning">
                    <p style="margin: 0;"><strong>⚠️ Important:</strong></p>
                    <ul style="margin: 10px 0 0 0;">
                        <li>This code will expire in <strong>10 minutes</strong></li>
                        <li>If you didn't request this code, please ignore this email</li>
                        <li>Never share this code with anyone</li>
                        <li>You have <strong>3 attempts</strong> to enter the correct code</li>
                    </ul>
                </div>
                
                <p style="color: #666; margin-top: 20px;">
                    If you didn't request this code, someone might be trying to access your account.
                </p>
                
                <p style="color: #666;">
                    Thanks,<br>
                    The NutriTracker Team
                </p>
            </div>
            <div class="footer">
                <p>© 2025 NutriTracker. All rights reserved.</p>
                <p>This is an automated email. Please do not reply.</p>
                <p>If you need help, contact support at pgdream18@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version
    text_content = f"""
    Hello {user_name},

    You requested to reset your password for your NutriTracker account.

    Your verification code is: {code}

    This code will expire in 10 minutes.
    You have 3 attempts to enter the correct code.

    If you didn't request this code, please ignore this email.

    Thanks,
    The NutriTracker Team
    """
    
    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"NutriTracker <{SMTP_EMAIL}>"
    message["To"] = to_email
    
    # Attach both text and HTML versions
    text_part = MIMEText(text_content, "plain")
    html_part = MIMEText(html_content, "html")
    message.attach(text_part)
    message.attach(html_part)
    
    # Send email
    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            username=SMTP_EMAIL,
            password=SMTP_PASSWORD,
            start_tls=True
        )
        print(f"✅ Password reset email sent to {to_email}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False
