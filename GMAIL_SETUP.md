# Gmail SMTP Setup Guide for NutriTracker.ai

## 🔐 How to Get Gmail App Password

Gmail App Passwords are special passwords that allow apps to access your Gmail account without using your regular password. This is more secure and required when 2-Step Verification is enabled.

### Step 1: Enable 2-Step Verification (if not already enabled)

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** in the left menu
3. Find **2-Step Verification** and turn it ON
4. Follow the setup process

### Step 2: Create App Password

1. Visit: https://myaccount.google.com/apppasswords
2. You might need to sign in again
3. In the "Select app" dropdown, choose **Mail**
4. In the "Select device" dropdown, choose **Other (Custom name)**
5. Type: **NutriTracker** (or any name you prefer)
6. Click **Generate**
7. Google will show you a 16-character password like: `abcd efgh ijkl mnop`
8. **Copy this password!** (You won't see it again)

### Step 3: Configure Your .env File

1. Open `backend/.env` file
2. Update these lines:

```env
# Replace with YOUR Gmail address
GMAIL_USER=your.email@gmail.com

# Replace with the 16-character App Password (remove spaces)
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

**Example:**
```env
GMAIL_USER=john.doe@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

### Step 4: Test Email Sending

1. Restart your backend server
2. Try the "Forgot Password" feature
3. You should receive a real email with the reset code!

## 📧 Email Preview

Users will receive a beautiful HTML email with:
- 🍱 NutriTracker.ai branding
- Large, clear 6-digit code
- 15-minute expiration warning
- Professional design matching your app theme

## 🔒 Security Notes

1. **Never commit `.env` file to Git** - It's already in `.gitignore`
2. **Never share your App Password** - Keep it secret!
3. **App Passwords are safer** than using your regular password
4. **You can revoke anytime** - Just delete it from Google Account settings

## ⚠️ Troubleshooting

### "Username and Password not accepted"
- Make sure you're using App Password, not regular Gmail password
- Remove all spaces from the 16-character code
- Make sure 2-Step Verification is enabled

### "Less secure app access"
- You don't need this with App Passwords
- App Passwords work with the latest security

### Email not sending
- Check console output for error messages
- Verify `.env` file is in `backend/` folder
- Make sure python-dotenv is installed: `pip install python-dotenv`

### Fallback Mode
If Gmail SMTP is not configured, the app will:
- Still work normally
- Show reset codes in console/terminal
- Display a warning message

## 🎯 Production Recommendations

For production deployment, consider:
1. Using a dedicated email service (SendGrid, AWS SES, Mailgun)
2. Storing credentials in environment variables (not .env file)
3. Adding email templates
4. Implementing rate limiting on email sends
5. Adding email verification on signup

## 🔗 Useful Links

- Create App Password: https://myaccount.google.com/apppasswords
- Google Account Security: https://myaccount.google.com/security
- Gmail SMTP Settings: https://support.google.com/mail/answer/7126229

## ✅ Setup Complete!

Once configured, your NutriTracker.ai app will send professional password reset emails automatically! 🎉
