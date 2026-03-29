import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_pending_reminders, mark_reminder_sent, add_message, log_outreach
from utils.channels import send_outreach
from datetime import datetime

st.markdown('<div class="page-header">Reminders</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Pending follow-ups and scheduled outreach</div>', unsafe_allow_html=True)

try:
    reminders = get_pending_reminders()
except Exception as e:
    st.error(f"Could not load reminders: {e}")
    reminders = []

if not reminders:
    st.markdown("""
    <div style="text-align:center; padding:60px 20px; color:#55556a;">
        <div style="font-size:32px; margin-bottom:12px;">⏰</div>
        <div style="font-size:14px;">No pending reminders</div>
        <div style="font-size:12px; margin-top:6px;">Set reminders from the Conversations page</div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f'<div class="mono-label" style="margin-bottom:16px;">{len(reminders)} PENDING</div>', unsafe_allow_html=True)

    if st.button(f"🚀 SEND ALL {len(reminders)} REMINDERS", use_container_width=True, type="primary"):
        sent, failed = 0, 0
        progress = st.progress(0)

        for i, r in enumerate(reminders):
            candidate_data = r.get("candidates") or {}
            candidate = {
                "name": candidate_data.get("name", ""),
                "email": candidate_data.get("email", ""),
                "phone": candidate_data.get("phone", ""),
            }
            channel = r.get("channel", "email")
            message = r.get("message", "")

            result = send_outreach(candidate, message, "Follow-up", channel)
            any_ok = any(v.get("success") for v in result.values())

            if any_ok:
                mark_reminder_sent(r["id"])
                for ch, res in result.items():
                    if res.get("success"):
                        add_message(r["candidate_id"], ch, "outbound", message)
                        log_outreach(r["candidate_id"], ch, "sent")
                sent += 1
            else:
                for ch, res in result.items():
                    log_outreach(r["candidate_id"], ch, "failed", res.get("error"))
                failed += 1

            progress.progress((i + 1) / len(reminders))

        progress.empty()
        st.success(f"✅ Sent {sent} reminders." + (f" {failed} failed." if failed else ""))
        st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    for r in reminders:
        candidate_data = r.get("candidates") or {}
        scheduled = r.get("scheduled_at", "")
        if scheduled:
            try:
                scheduled = datetime.fromisoformat(scheduled).strftime("%d %b %Y, %H:%M UTC")
            except Exception:
                pass

        channel = r.get("channel", "email")
        channel_icon = {"whatsapp": "💬", "email": "📧"}.get(channel, "📨")

        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"""
            <div class="caller-card" style="padding:14px 16px; margin-bottom:0;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <div style="font-weight:600; font-size:13px; color:#f0f0f8;">
                            {channel_icon} {candidate_data.get('name','Unknown')}
                        </div>
                        <div style="font-size:12px; color:#55556a; margin-top:4px; line-height:1.5;">
                            {r.get('message','')[:120]}{'...' if len(r.get('message','')) > 120 else ''}
                        </div>
                    </div>
                </div>
                <div style="font-size:10px; color:#55556a; margin-top:8px;
                            font-family:'Space Mono',monospace; letter-spacing:0.05em;">
                    SCHEDULED: {scheduled}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            if st.button("SEND", key=f"send_r_{r['id']}", use_container_width=True):
                candidate_full = {
                    "name": candidate_data.get("name", ""),
                    "email": candidate_data.get("email", ""),
                    "phone": candidate_data.get("phone", ""),
                }
                result = send_outreach(candidate_full, r["message"], "Follow-up", channel)
                any_ok = any(v.get("success") for v in result.values())
                if any_ok:
                    mark_reminder_sent(r["id"])
                    add_message(r["candidate_id"], channel, "outbound", r["message"])
                    log_outreach(r["candidate_id"], channel, "sent")
                    st.success("Sent!")
                    st.rerun()
                else:
                    errors = " | ".join(v.get("error","") for v in result.values())
                    st.error(f"Failed: {errors}")

        with col3:
            if st.button("SKIP", key=f"skip_r_{r['id']}", use_container_width=True):
                mark_reminder_sent(r["id"])
                st.rerun()

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
