# 📞 The Caller — AI Recruitment Agent

Sits between your **Sourcer** and **Validator** apps. Handles all candidate communication: pitch, screen, negotiate, close.

## Stack
- **UI**: Streamlit Cloud (free)
- **DB**: Supabase (free tier, fresh project)
- **AI**: Groq llama-3.3-70b (free tier)
- **WhatsApp**: Twilio Sandbox (free)
- **Email**: Gmail SMTP (free)
- **Voice**: VAPI scaffold (pay-per-use, off by default)

## Deploy to Streamlit Cloud

1. Push this folder to a GitHub repo
2. Go to share.streamlit.io → New app → select your repo
3. Set main file: `app.py`
4. Add secrets (Settings → Secrets):

```toml
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "your-anon-key"
GROQ_API_KEY = "your-groq-key"
GMAIL_USER = "you@gmail.com"
GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"
RECRUITER_NAME = "Your Name"
TWILIO_ACCOUNT_SID = "ACxxx"
TWILIO_AUTH_TOKEN = "xxx"
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
```

## Supabase Setup
Run the SQL in **Settings → Supabase SQL tab** inside the app.

## Pages
- **Dashboard** — pipeline overview, integration health
- **Candidates** — add manually, import CSV
- **Conversations** — AI message generator, send, track, analyze responses
- **JD Manager** — store job descriptions with screening Qs + Calendly link
- **Reminders** — batch-send pending follow-ups
- **Reports** — funnel analytics, channel breakdown, outreach log
- **Settings** — secrets guide, SQL schema, VAPI setup

## Workflow
1. Add a JD
2. Add/import candidates, assign to JD
3. Open Conversations → Generate → Review → Send
4. Log candidate replies, Analyze, move to next stage
5. Set reminders for follow-ups
6. On close → Generate Summary → hand to Validator
