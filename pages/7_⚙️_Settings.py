import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.channels import check_credentials

st.markdown('<div class="page-header">Settings</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Configure integrations, API keys, and view Supabase setup SQL</div>', unsafe_allow_html=True)

# ─── INTEGRATION STATUS ────────────────────────────────────────────────────────
creds = check_credentials()
status_map = {
    "groq": ("🧠 Groq AI", "Core AI engine — required"),
    "supabase": ("🗄 Supabase", "Database — required"),
    "email": ("📧 Gmail SMTP", "Email outreach"),
    "whatsapp": ("💬 Twilio WhatsApp", "WhatsApp outreach"),
    "voice": ("📞 VAPI Voice", "Voice calls (scaffold)"),
}

st.markdown('<div class="mono-label" style="margin-bottom:12px;">INTEGRATION STATUS</div>', unsafe_allow_html=True)

cols = st.columns(len(status_map))
for col, (key, (label, desc)) in zip(cols, status_map.items()):
    ok = creds.get(key, False)
    color = "#4ecb71" if ok else "#ef4444"
    status_text = "CONNECTED" if ok else "NOT SET"
    col.markdown(f"""
    <div style="background:#16161f; border:1px solid {'rgba(78,203,113,0.3)' if ok else '#2a2a3a'};
                border-radius:6px; padding:14px; text-align:center;">
        <div style="font-size:20px;">{label.split()[0]}</div>
        <div style="font-size:11px; color:#8888aa; margin-top:4px;">{label[2:]}</div>
        <div style="font-size:10px; color:#55556a; margin-top:2px;">{desc}</div>
        <div style="color:{color}; font-family:'Space Mono',monospace; font-size:10px;
                    margin-top:8px; letter-spacing:0.05em;">{status_text}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# ─── SECRETS GUIDE ────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["SECRETS SETUP", "SUPABASE SQL", "VOICE SCAFFOLD"])

with tab1:
    st.markdown("""
    <div class="caller-card">
        <div class="mono-label" style="margin-bottom:12px;">HOW TO CONFIGURE</div>
        <div style="font-size:13px; color:#8888aa; line-height:1.8;">
            On <strong style="color:#f0f0f8;">Streamlit Cloud</strong>: Go to your app → Settings → Secrets → paste the block below.<br>
            <strong style="color:#f0f0f8;">Locally</strong>: Create <code style="color:#e8c547;">.streamlit/secrets.toml</code> in the project root.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.code("""
# .streamlit/secrets.toml

# ── REQUIRED ──────────────────────────────────
SUPABASE_URL = "https://xxxx.supabase.co"
SUPABASE_KEY = "your-supabase-anon-key"
GROQ_API_KEY = "your-groq-api-key"

# ── EMAIL (Gmail SMTP) ────────────────────────
GMAIL_USER = "yourname@gmail.com"
GMAIL_APP_PASSWORD = "xxxx xxxx xxxx xxxx"   # 16-char App Password
RECRUITER_NAME = "Your Name / Company"

# ── WHATSAPP (Twilio Sandbox) ─────────────────
TWILIO_ACCOUNT_SID = "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN  = "your-twilio-auth-token"
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"  # Twilio sandbox number

# ── VOICE (VAPI — activate later) ────────────
VAPI_API_KEY = ""   # Leave blank to scaffold only
""", language="toml")

    st.markdown("""
    <div style="margin-top:20px;">
        <div class="mono-label" style="margin-bottom:10px;">HOW TO GET EACH KEY</div>
        <div style="font-size:13px; color:#8888aa; line-height:2;">
            🧠 <strong style="color:#f0f0f8;">Groq</strong>: console.groq.com → API Keys → Free tier ✅<br>
            🗄 <strong style="color:#f0f0f8;">Supabase</strong>: app.supabase.com → New project → Settings → API ✅<br>
            📧 <strong style="color:#f0f0f8;">Gmail App Password</strong>: Google Account → Security → 2FA on → App Passwords → Generate ✅<br>
            💬 <strong style="color:#f0f0f8;">Twilio WhatsApp</strong>: twilio.com → Sandbox → join with your phone number (free) ✅<br>
            📞 <strong style="color:#f0f0f8;">VAPI</strong>: vapi.ai → Dashboard → API Key (pay-per-use, activate later)
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    st.markdown("""
    <div class="caller-card" style="margin-bottom:16px;">
        <div class="mono-label" style="margin-bottom:8px;">SETUP INSTRUCTIONS</div>
        <div style="font-size:13px; color:#8888aa; line-height:1.7;">
            1. Create a new Supabase project at <code style="color:#e8c547;">app.supabase.com</code><br>
            2. Go to <strong style="color:#f0f0f8;">SQL Editor</strong><br>
            3. Paste the SQL below and run it<br>
            4. Copy your Project URL and anon key to secrets
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.code("""
-- THE CALLER — Supabase Schema
-- Run this in your Supabase SQL Editor

-- Job Descriptions
CREATE TABLE IF NOT EXISTS job_descriptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    skills TEXT,
    salary_range TEXT,
    screening_questions TEXT,
    calendly_link TEXT,
    additional_info TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Candidates
CREATE TABLE IF NOT EXISTS candidates (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    location TEXT,
    source TEXT DEFAULT 'manual',
    current_role TEXT,
    current_company TEXT,
    experience_years INTEGER DEFAULT 0,
    current_salary TEXT,
    expected_salary TEXT,
    notice_period TEXT,
    jd_id UUID REFERENCES job_descriptions(id) ON DELETE SET NULL,
    status TEXT DEFAULT 'new',
    last_channel TEXT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversations
CREATE TABLE IF NOT EXISTS conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    channel TEXT,
    direction TEXT,        -- 'outbound' | 'inbound'
    message TEXT,
    metadata TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Outreach Log
CREATE TABLE IF NOT EXISTS outreach_log (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    channel TEXT,
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT,           -- 'sent' | 'failed'
    error TEXT
);

-- Reminders
CREATE TABLE IF NOT EXISTS reminders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id UUID REFERENCES candidates(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMPTZ,
    channel TEXT DEFAULT 'email',
    message TEXT,
    sent BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMPTZ
);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE outreach_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE reminders ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;

-- Allow all for anon key (since this is a single-user app)
CREATE POLICY "Allow all" ON candidates FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON conversations FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON outreach_log FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON reminders FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all" ON job_descriptions FOR ALL USING (true) WITH CHECK (true);
""", language="sql")

with tab3:
    st.markdown("""
    <div class="caller-card">
        <div class="mono-label" style="margin-bottom:10px;">📞 VOICE CALLING — VAPI SCAFFOLD</div>
        <div style="font-size:13px; color:#8888aa; line-height:1.8;">
            Voice calling via VAPI is architected and ready. It's toggled OFF for the free-tier MVP.<br><br>
            <strong style="color:#f0f0f8;">To activate:</strong><br>
            1. Create a VAPI account at <code style="color:#e8c547;">vapi.ai</code><br>
            2. Get your API key and add it to secrets as <code style="color:#e8c547;">VAPI_API_KEY</code><br>
            3. The Conversations page will automatically detect it and show a 📞 Call button<br><br>
            <strong style="color:#f0f0f8;">What it will do:</strong><br>
            → Initiate an outbound call to the candidate's phone<br>
            → Use the generated pitch/screening script as the AI call script<br>
            → Transcribe the call and log it to the conversation thread<br>
            → Analyze the call and suggest next steps
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    vapi_active = creds.get("voice", False)
    if vapi_active:
        st.success("✅ VAPI key detected. Voice calling is ready.")
    else:
        st.info("VAPI key not set. Add `VAPI_API_KEY` to secrets to activate voice calls.")
