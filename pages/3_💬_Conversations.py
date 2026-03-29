import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import (
    get_candidates, get_candidate, get_conversations, add_message,
    get_jd, update_candidate_status, log_outreach, add_reminder
)
from utils.ai_engine import generate_message, analyze_candidate_response, summarize_conversation
from utils.channels import send_outreach
from datetime import datetime, timedelta

st.markdown('<div class="page-header">Conversations</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">AI-powered outreach · Generate, review, send, track</div>', unsafe_allow_html=True)

STAGES = ["pitch", "screening", "negotiation", "interview_slot", "followup", "rejection"]
STAGE_LABELS = {
    "pitch": "🎯 Pitch",
    "screening": "🔍 Screening",
    "negotiation": "💰 Negotiation",
    "interview_slot": "📅 Interview Slot",
    "followup": "🔔 Follow-up",
    "rejection": "❌ Rejection"
}

# ─── CANDIDATE SELECTOR ────────────────────────────────────────────────────────
try:
    candidates = get_candidates()
except Exception:
    candidates = []

if not candidates:
    st.info("No candidates found. Add candidates first from the Candidates page.")
    st.stop()

candidate_options = {f"{c['name']} · {c.get('current_role','—')} · {c.get('status','new')}": c["id"] for c in candidates}

# Support pre-selection via query params
params = st.query_params
preselect_id = params.get("candidate_id", None)

preselect_key = None
if preselect_id:
    for k, v in candidate_options.items():
        if str(v) == str(preselect_id):
            preselect_key = k
            break

selected_label = st.selectbox(
    "Select Candidate",
    list(candidate_options.keys()),
    index=list(candidate_options.keys()).index(preselect_key) if preselect_key else 0
)
candidate_id = candidate_options[selected_label]

# ─── LOAD DATA ─────────────────────────────────────────────────────────────────
try:
    candidate = get_candidate(candidate_id)
    jd_data = candidate.get("job_descriptions") or {}
    conversations = get_conversations(candidate_id)
except Exception as e:
    st.error(f"Could not load candidate data: {e}")
    st.stop()

# ─── TWO-COLUMN LAYOUT ─────────────────────────────────────────────────────────
col_thread, col_compose = st.columns([3, 2])

# ─── LEFT: CONVERSATION THREAD ────────────────────────────────────────────────
with col_thread:
    # Candidate summary strip
    status = candidate.get("status", "new")
    st.markdown(f"""
    <div class="caller-card" style="padding:14px 18px; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div>
                <div style="font-weight:700; font-size:15px; color:#f0f0f8;">{candidate.get('name','—')}</div>
                <div style="font-size:12px; color:#55556a; margin-top:3px;">
                    {candidate.get('current_role','—')} @ {candidate.get('current_company','—')}
                    · {candidate.get('experience_years','?')}y exp
                    · 💰 {candidate.get('expected_salary','?')}
                    · ⏱ {candidate.get('notice_period','?')}
                </div>
                <div style="font-size:12px; color:#55556a; margin-top:2px;">
                    📧 {candidate.get('email','—')} · 📱 {candidate.get('phone','—')}
                </div>
            </div>
            <span class="status-badge status-{status}">{status}</span>
        </div>
        {'<div style="font-size:12px; color:#8888aa; margin-top:10px; padding-top:8px; border-top:1px solid #2a2a3a;">🎯 JD: ' + jd_data.get("title","No JD assigned") + '</div>' if jd_data else ''}
    </div>
    """, unsafe_allow_html=True)

    # Thread
    st.markdown('<div class="mono-label" style="margin-bottom:12px;">CONVERSATION THREAD</div>', unsafe_allow_html=True)

    if not conversations:
        st.markdown("""
        <div style="text-align:center; padding:40px 20px; color:#55556a; font-size:13px;
                    border:1px dashed #2a2a3a; border-radius:6px;">
            No messages yet.<br>Generate your first outreach message on the right.
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in conversations:
            direction = msg.get("direction", "outbound")
            channel = msg.get("channel", "")
            ts = msg.get("timestamp", "")
            if ts:
                try:
                    ts = datetime.fromisoformat(ts).strftime("%d %b %H:%M")
                except Exception:
                    pass

            channel_icon = {"whatsapp": "💬", "email": "📧", "voice": "📞", "manual": "✍️"}.get(channel, "📨")

            if direction == "outbound":
                st.markdown(f"""
                <div style="margin-bottom:12px; display:flex; justify-content:flex-end;">
                    <div style="max-width:85%; background:#1e1e2e; border:1px solid #2a2a3a;
                                border-radius:10px 10px 2px 10px; padding:12px 16px;">
                        <div style="font-size:10px; color:#55556a; margin-bottom:6px; font-family:'Space Mono',monospace;">
                            {channel_icon} {channel.upper()} · SENT · {ts}
                        </div>
                        <div style="font-size:13px; color:#f0f0f8; line-height:1.6; white-space:pre-wrap;">{msg.get('message','')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="margin-bottom:12px; display:flex; justify-content:flex-start;">
                    <div style="max-width:85%; background:#16161f; border:1px solid rgba(232,197,71,0.2);
                                border-radius:10px 10px 10px 2px; padding:12px 16px;">
                        <div style="font-size:10px; color:#55556a; margin-bottom:6px; font-family:'Space Mono',monospace;">
                            👤 CANDIDATE · {ts}
                        </div>
                        <div style="font-size:13px; color:#f0f0f8; line-height:1.6; white-space:pre-wrap;">{msg.get('message','')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Log inbound response
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="mono-label" style="margin-bottom:8px;">LOG CANDIDATE RESPONSE</div>', unsafe_allow_html=True)

    inbound_text = st.text_area("Paste candidate reply here", height=100, placeholder="Copy the candidate's WhatsApp/email response here...", key="inbound")

    analyze_col, log_col = st.columns(2)

    with log_col:
        if st.button("LOG RESPONSE", use_container_width=True):
            if inbound_text.strip():
                add_message(candidate_id, "manual", "inbound", inbound_text.strip())
                st.success("Logged.")
                st.rerun()
            else:
                st.warning("Paste a response first.")

    with analyze_col:
        if st.button("🧠 ANALYZE", use_container_width=True):
            if inbound_text.strip():
                with st.spinner("Analyzing..."):
                    analysis = analyze_candidate_response(inbound_text.strip(), jd_data)
                interest = analysis.get("interest_level", "unknown")
                interest_color = {"high": "#4ecb71", "medium": "#f59e0b", "low": "#ef4444", "unknown": "#55556a"}.get(interest, "#55556a")

                st.markdown(f"""
                <div class="caller-card" style="margin-top:8px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <span class="mono-label">ANALYSIS</span>
                        <span style="color:{interest_color}; font-family:'Space Mono',monospace; font-size:11px;">
                            {interest.upper()} INTEREST
                        </span>
                    </div>
                    <div style="font-size:12px; color:#8888aa; line-height:1.6;">
                        {analysis.get('summary','')}
                    </div>
                    {'<div style="margin-top:8px; font-size:12px; color:#ef4444;">⚠️ ' + ' · '.join(analysis.get('blockers',[])) + '</div>' if analysis.get('blockers') else ''}
                    <div style="margin-top:8px; font-size:11px; color:#55556a; font-family:Space Mono,monospace;">
                        SUGGESTED NEXT → {analysis.get('recommended_next_stage','').upper()}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Paste a response to analyze.")

# ─── RIGHT: COMPOSE ────────────────────────────────────────────────────────────
with col_compose:
    st.markdown('<div class="mono-label" style="margin-bottom:12px;">COMPOSE OUTREACH</div>', unsafe_allow_html=True)

    stage = st.selectbox("Message Stage", STAGES, format_func=lambda x: STAGE_LABELS.get(x, x))
    channel = st.selectbox("Send Via", ["auto", "whatsapp", "email", "both"],
                           format_func=lambda x: {"auto": "🤖 Auto (smart)", "whatsapp": "💬 WhatsApp", "email": "📧 Email", "both": "📡 Both"}.get(x, x))
    extra_context = st.text_area("Extra Context for AI (optional)", height=70,
                                  placeholder="e.g. candidate asked about remote work, mention it's hybrid...")

    if not jd_data:
        st.warning("⚠️ No JD assigned to this candidate. Assign one in the Candidates page for better messages.")

    if st.button("✨ GENERATE MESSAGE", use_container_width=True):
        with st.spinner("Generating..."):
            try:
                msg = generate_message(
                    stage=stage,
                    candidate=candidate,
                    jd=jd_data,
                    conversation_history=conversations,
                    extra_context=extra_context
                )
                st.session_state[f"generated_msg_{candidate_id}"] = msg
            except Exception as e:
                st.error(f"AI generation failed: {e}")

    # Show generated message
    generated = st.session_state.get(f"generated_msg_{candidate_id}", "")

    msg_to_send = st.text_area(
        "Message (edit before sending)",
        value=generated,
        height=280,
        key=f"msg_area_{candidate_id}",
        placeholder="Generated message will appear here. You can edit before sending."
    )

    email_subject = ""
    if channel in ["email", "both"]:
        email_subject = st.text_input("Email Subject", value=f"Exciting Opportunity: {jd_data.get('title','New Role')}")

    send_col1, send_col2 = st.columns(2)

    with send_col1:
        if st.button("📤 SEND", use_container_width=True, type="primary"):
            if not msg_to_send.strip():
                st.error("Generate or write a message first.")
            else:
                with st.spinner("Sending..."):
                    results = send_outreach(
                        candidate=candidate,
                        message=msg_to_send.strip(),
                        subject=email_subject or f"Opportunity: {jd_data.get('title','')}",
                        channel=channel
                    )

                any_success = any(r.get("success") for r in results.values())
                channels_used = list(results.keys())

                for ch, result in results.items():
                    if result.get("success"):
                        add_message(candidate_id, ch, "outbound", msg_to_send.strip())
                        log_outreach(candidate_id, ch, "sent")
                        st.success(f"✅ Sent via {ch}")
                    else:
                        log_outreach(candidate_id, ch, "failed", result.get("error"))
                        st.error(f"❌ {ch} failed: {result.get('error')}")

                if any_success and candidate.get("status") == "new":
                    update_candidate_status(candidate_id, "contacted")

                st.session_state.pop(f"generated_msg_{candidate_id}", None)
                st.rerun()

    with send_col2:
        if st.button("💾 LOG ONLY", use_container_width=True):
            if msg_to_send.strip():
                add_message(candidate_id, "manual", "outbound", msg_to_send.strip())
                st.success("Logged without sending.")
                st.session_state.pop(f"generated_msg_{candidate_id}", None)
                st.rerun()

    # ─── REMINDERS ─────────────────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="mono-label" style="margin-bottom:8px;">SCHEDULE REMINDER</div>', unsafe_allow_html=True)

    with st.expander("Set follow-up reminder"):
        r_days = st.number_input("Remind in (days)", min_value=1, max_value=30, value=2)
        r_channel = st.selectbox("Reminder channel", ["email", "whatsapp"], key="r_chan")
        r_msg = st.text_area("Reminder message", height=80,
                              value=f"Hi {candidate.get('name','').split()[0]}, just following up on our conversation about the {jd_data.get('title','role')}. Would love to connect.")

        if st.button("SET REMINDER", use_container_width=True):
            scheduled = (datetime.utcnow() + timedelta(days=r_days)).isoformat()
            add_reminder(candidate_id, scheduled, r_msg, r_channel)
            st.success(f"✅ Reminder set for {r_days} day(s) from now.")

    # ─── STATUS UPDATE ─────────────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="mono-label" style="margin-bottom:8px;">UPDATE STATUS</div>', unsafe_allow_html=True)

    STATUS_OPTIONS = ["new", "contacted", "responded", "screened", "negotiating", "closed", "rejected"]
    new_status = st.selectbox("Status", STATUS_OPTIONS,
                               index=STATUS_OPTIONS.index(candidate.get("status", "new")),
                               key="status_override")
    if st.button("UPDATE STATUS", use_container_width=True):
        update_candidate_status(candidate_id, new_status)
        st.success(f"Status → {new_status}")
        st.rerun()

    # ─── CONVERSATION SUMMARY ──────────────────────────────────────────────────
    if conversations:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        if st.button("📋 GENERATE SUMMARY FOR VALIDATOR", use_container_width=True):
            with st.spinner("Summarizing..."):
                try:
                    summary = summarize_conversation(conversations, candidate, jd_data)
                    st.text_area("Summary (copy to Validator)", summary, height=200)
                except Exception as e:
                    st.error(f"Summary failed: {e}")
