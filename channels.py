import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client as TwilioClient


# ─── EMAIL (Gmail SMTP) ────────────────────────────────────────────────────────

def send_email(to_email: str, subject: str, body: str, candidate_name: str = "") -> dict:
    """Send email via Gmail SMTP. Returns {"success": bool, "error": str|None}"""
    try:
        gmail_user = st.secrets["GMAIL_USER"]
        gmail_pass = st.secrets["GMAIL_APP_PASSWORD"]
        from_name = st.secrets.get("RECRUITER_NAME", "The Caller")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{from_name} <{gmail_user}>"
        msg["To"] = to_email

        # Plain text version
        text_part = MIMEText(body, "plain")

        # HTML version with minimal styling
        html_body = f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                     color: #1a1a2e; max-width: 600px; margin: 0 auto; padding: 32px 24px;">
            <div style="border-left: 3px solid #e8c547; padding-left: 16px; margin-bottom: 24px;">
                <p style="margin:0; font-size:12px; color:#888; letter-spacing:0.05em; text-transform:uppercase;">
                    The Caller · AI Recruitment
                </p>
            </div>
            <div style="font-size:15px; line-height:1.8; color:#1a1a2e;">
                {body.replace(chr(10), '<br>')}
            </div>
            <div style="margin-top:32px; padding-top:16px; border-top:1px solid #eee;
                        font-size:11px; color:#aaa;">
                This message was sent by an AI recruitment agent on behalf of {from_name}.
            </div>
        </body>
        </html>
        """
        html_part = MIMEText(html_body, "html")

        msg.attach(text_part)
        msg.attach(html_part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, to_email, msg.as_string())

        return {"success": True, "error": None}

    except Exception as e:
        return {"success": False, "error": str(e)}


# ─── WHATSAPP (Twilio Sandbox) ─────────────────────────────────────────────────

def send_whatsapp(to_phone: str, message: str) -> dict:
    """Send WhatsApp via Twilio sandbox. Returns {"success": bool, "error": str|None, "sid": str|None}"""
    try:
        account_sid = st.secrets["TWILIO_ACCOUNT_SID"]
        auth_token = st.secrets["TWILIO_AUTH_TOKEN"]
        from_number = st.secrets.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

        client = TwilioClient(account_sid, auth_token)

        # Format phone number
        clean_phone = to_phone.strip().replace(" ", "").replace("-", "")
        if not clean_phone.startswith("+"):
            clean_phone = "+" + clean_phone

        msg = client.messages.create(
            body=message,
            from_=from_number,
            to=f"whatsapp:{clean_phone}"
        )

        return {"success": True, "error": None, "sid": msg.sid}

    except Exception as e:
        return {"success": False, "error": str(e), "sid": None}


# ─── SMART ROUTER ──────────────────────────────────────────────────────────────

def send_outreach(candidate: dict, message: str, subject: str = "Exciting Opportunity", channel: str = "auto") -> dict:
    """
    Route outreach to the right channel.
    channel: "auto" | "whatsapp" | "email" | "both"
    Returns summary dict with results per channel.
    """
    results = {}

    has_phone = bool(candidate.get("phone", "").strip())
    has_email = bool(candidate.get("email", "").strip())

    if channel == "whatsapp" or (channel == "auto" and has_phone):
        if has_phone:
            results["whatsapp"] = send_whatsapp(candidate["phone"], message)
        else:
            results["whatsapp"] = {"success": False, "error": "No phone number"}

    if channel == "email" or (channel == "auto" and not has_phone and has_email):
        if has_email:
            results["email"] = send_email(candidate["email"], subject, message, candidate.get("name", ""))
        else:
            results["email"] = {"success": False, "error": "No email address"}

    if channel == "both":
        if has_phone:
            results["whatsapp"] = send_whatsapp(candidate["phone"], message)
        if has_email:
            results["email"] = send_email(candidate["email"], subject, message, candidate.get("name", ""))

    return results


def check_credentials() -> dict:
    """Check which integrations are configured."""
    status = {}

    try:
        _ = st.secrets["GROQ_API_KEY"]
        status["groq"] = True
    except Exception:
        status["groq"] = False

    try:
        _ = st.secrets["SUPABASE_URL"]
        _ = st.secrets["SUPABASE_KEY"]
        status["supabase"] = True
    except Exception:
        status["supabase"] = False

    try:
        _ = st.secrets["GMAIL_USER"]
        _ = st.secrets["GMAIL_APP_PASSWORD"]
        status["email"] = True
    except Exception:
        status["email"] = False

    try:
        _ = st.secrets["TWILIO_ACCOUNT_SID"]
        _ = st.secrets["TWILIO_AUTH_TOKEN"]
        status["whatsapp"] = True
    except Exception:
        status["whatsapp"] = False

    try:
        _ = st.secrets["VAPI_API_KEY"]
        status["voice"] = True
    except Exception:
        status["voice"] = False

    return status
