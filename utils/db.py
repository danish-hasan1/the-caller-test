import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import json

@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# ─── CANDIDATES ────────────────────────────────────────────────────────────────

def get_candidates(status=None):
    db = get_supabase()
    q = db.table("candidates").select("*, job_descriptions(title)").order("created_at", desc=True)
    if status:
        q = q.eq("status", status)
    return q.execute().data or []

def get_candidate(candidate_id):
    db = get_supabase()
    res = db.table("candidates").select("*, job_descriptions(title, description, skills, salary_range)").eq("id", candidate_id).single().execute()
    return res.data

def upsert_candidate(data):
    db = get_supabase()
    if "id" in data and data["id"]:
        return db.table("candidates").update(data).eq("id", data["id"]).execute().data
    data.pop("id", None)
    data["created_at"] = datetime.utcnow().isoformat()
    return db.table("candidates").insert(data).execute().data

def update_candidate_status(candidate_id, status):
    db = get_supabase()
    db.table("candidates").update({"status": status, "updated_at": datetime.utcnow().isoformat()}).eq("id", candidate_id).execute()

def delete_candidate(candidate_id):
    db = get_supabase()
    db.table("candidates").delete().eq("id", candidate_id).execute()

# ─── JOB DESCRIPTIONS ──────────────────────────────────────────────────────────

def get_jds():
    db = get_supabase()
    return db.table("job_descriptions").select("*").order("created_at", desc=True).execute().data or []

def get_jd(jd_id):
    db = get_supabase()
    return db.table("job_descriptions").select("*").eq("id", jd_id).single().execute().data

def upsert_jd(data):
    db = get_supabase()
    if "id" in data and data["id"]:
        return db.table("job_descriptions").update(data).eq("id", data["id"]).execute().data
    data.pop("id", None)
    data["created_at"] = datetime.utcnow().isoformat()
    return db.table("job_descriptions").insert(data).execute().data

def delete_jd(jd_id):
    db = get_supabase()
    db.table("job_descriptions").delete().eq("id", jd_id).execute()

# ─── CONVERSATIONS ─────────────────────────────────────────────────────────────

def get_conversations(candidate_id):
    db = get_supabase()
    return db.table("conversations").select("*").eq("candidate_id", candidate_id).order("timestamp", desc=False).execute().data or []

def add_message(candidate_id, channel, direction, message, metadata=None):
    db = get_supabase()
    row = {
        "candidate_id": candidate_id,
        "channel": channel,
        "direction": direction,  # 'outbound' | 'inbound'
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
        "metadata": json.dumps(metadata) if metadata else None
    }
    return db.table("conversations").insert(row).execute().data

# ─── OUTREACH LOG ──────────────────────────────────────────────────────────────

def log_outreach(candidate_id, channel, status, error=None):
    db = get_supabase()
    db.table("outreach_log").insert({
        "candidate_id": candidate_id,
        "channel": channel,
        "sent_at": datetime.utcnow().isoformat(),
        "status": status,
        "error": error
    }).execute()

def get_outreach_log(candidate_id=None):
    db = get_supabase()
    q = db.table("outreach_log").select("*, candidates(name)").order("sent_at", desc=True)
    if candidate_id:
        q = q.eq("candidate_id", candidate_id)
    return q.execute().data or []

# ─── REMINDERS ─────────────────────────────────────────────────────────────────

def get_pending_reminders():
    db = get_supabase()
    now = datetime.utcnow().isoformat()
    return db.table("reminders").select("*, candidates(name, email, phone)").eq("sent", False).lte("scheduled_at", now).execute().data or []

def add_reminder(candidate_id, scheduled_at, message, channel="email"):
    db = get_supabase()
    db.table("reminders").insert({
        "candidate_id": candidate_id,
        "scheduled_at": scheduled_at,
        "message": message,
        "channel": channel,
        "sent": False
    }).execute()

def mark_reminder_sent(reminder_id):
    db = get_supabase()
    db.table("reminders").update({"sent": True, "sent_at": datetime.utcnow().isoformat()}).eq("id", reminder_id).execute()

# ─── STATS ─────────────────────────────────────────────────────────────────────

def get_stats():
    db = get_supabase()
    candidates = db.table("candidates").select("status").execute().data or []
    total = len(candidates)
    by_status = {}
    for c in candidates:
        s = c["status"]
        by_status[s] = by_status.get(s, 0) + 1

    outreach = db.table("outreach_log").select("status, channel").execute().data or []
    sent = len(outreach)
    by_channel = {}
    for o in outreach:
        ch = o["channel"]
        by_channel[ch] = by_channel.get(ch, 0) + 1

    return {
        "total": total,
        "by_status": by_status,
        "sent": sent,
        "by_channel": by_channel,
        "closed": by_status.get("closed", 0),
        "rejected": by_status.get("rejected", 0),
    }
