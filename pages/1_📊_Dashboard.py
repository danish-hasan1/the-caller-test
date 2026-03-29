import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_stats, get_candidates, get_pending_reminders
from utils.channels import check_credentials
from datetime import datetime

st.markdown('<div class="page-header">Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Overview of your recruitment pipeline</div>', unsafe_allow_html=True)

# ─── INTEGRATION STATUS ────────────────────────────────────────────────────────
creds = check_credentials()
cols = st.columns(5)
integrations = [
    ("GROQ AI", "groq", "🧠"),
    ("SUPABASE", "supabase", "🗄"),
    ("EMAIL", "email", "📧"),
    ("WHATSAPP", "whatsapp", "💬"),
    ("VOICE", "voice", "📞"),
]
for col, (label, key, icon) in zip(cols, integrations):
    ok = creds.get(key, False)
    color = "#4ecb71" if ok else "#ef4444"
    dot = "●" if ok else "○"
    col.markdown(f"""
    <div style="background:#16161f; border:1px solid #2a2a3a; border-radius:6px;
                padding:10px 12px; text-align:center;">
        <div style="font-size:18px; margin-bottom:4px;">{icon}</div>
        <div style="font-family:'Space Mono',monospace; font-size:9px;
                    color:#55556a; letter-spacing:0.1em;">{label}</div>
        <div style="color:{color}; font-size:14px; margin-top:4px;">{dot}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ─── PIPELINE STATS ────────────────────────────────────────────────────────────
try:
    stats = get_stats()
    by_status = stats.get("by_status", {})

    m1, m2, m3, m4, m5, m6 = st.columns(6)
    metrics = [
        (m1, "TOTAL", stats.get("total", 0), None),
        (m2, "CONTACTED", by_status.get("contacted", 0), None),
        (m3, "SCREENED", by_status.get("screened", 0), None),
        (m4, "NEGOTIATING", by_status.get("negotiating", 0), None),
        (m5, "CLOSED", by_status.get("closed", 0), "+"),
        (m6, "REJECTED", by_status.get("rejected", 0), "-"),
    ]
    for col, label, value, delta in metrics:
        col.metric(label, value, delta)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # ─── RECENT CANDIDATES ─────────────────────────────────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="mono-label" style="margin-bottom:12px;">RECENT CANDIDATES</div>', unsafe_allow_html=True)

        candidates = get_candidates()[:8]
        if candidates:
            for c in candidates:
                status = c.get("status", "new")
                jd_title = (c.get("job_descriptions") or {}).get("title", "—")
                channel_icon = {"whatsapp": "💬", "email": "📧", "voice": "📞"}.get(c.get("last_channel", ""), "—")

                st.markdown(f"""
                <div class="caller-card" style="padding:14px 18px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <div style="font-weight:600; font-size:14px; color:#f0f0f8;">{c.get('name','—')}</div>
                            <div style="font-size:12px; color:#55556a; margin-top:2px;">
                                {c.get('current_role','—')} · {jd_title}
                            </div>
                        </div>
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:16px;">{channel_icon}</span>
                            <span class="status-badge status-{status}">{status}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; padding:40px; color:#55556a; font-size:13px;">
                No candidates yet. Add candidates in the Candidates page.
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="mono-label" style="margin-bottom:12px;">PIPELINE BREAKDOWN</div>', unsafe_allow_html=True)

        pipeline_stages = ["new", "contacted", "responded", "screened", "negotiating", "closed", "rejected"]
        stage_colors = {
            "new": "#60a5fa", "contacted": "#e8c547", "responded": "#a855f7",
            "screened": "#fb923c", "negotiating": "#f59e0b",
            "closed": "#4ecb71", "rejected": "#ef4444"
        }
        total = max(stats.get("total", 1), 1)

        for stage in pipeline_stages:
            count = by_status.get(stage, 0)
            pct = int((count / total) * 100)
            color = stage_colors.get(stage, "#55556a")
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                    <span style="font-family:'Space Mono',monospace; font-size:10px;
                                 color:#8888aa; text-transform:uppercase;">{stage}</span>
                    <span style="font-family:'Space Mono',monospace; font-size:10px; color:#55556a;">{count}</span>
                </div>
                <div style="background:#2a2a3a; border-radius:2px; height:4px;">
                    <div style="width:{pct}%; background:{color}; height:4px; border-radius:2px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Pending reminders
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="mono-label" style="margin-bottom:12px;">PENDING REMINDERS</div>', unsafe_allow_html=True)

        try:
            reminders = get_pending_reminders()
            if reminders:
                for r in reminders[:5]:
                    cname = (r.get("candidates") or {}).get("name", "Unknown")
                    st.markdown(f"""
                    <div style="background:#16161f; border:1px solid #f59e0b33;
                                border-radius:6px; padding:10px 12px; margin-bottom:8px;">
                        <div style="font-size:12px; color:#f59e0b; font-family:'Space Mono',monospace;">⏰ {cname}</div>
                        <div style="font-size:11px; color:#55556a; margin-top:2px;">{r.get('message','')[:60]}...</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-size:12px; color:#55556a;">No pending reminders</div>', unsafe_allow_html=True)
        except Exception:
            st.markdown('<div style="font-size:12px; color:#55556a;">—</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Could not load dashboard data. Check your Supabase connection in Settings.\n\n{e}")
    st.info("👉 Go to **Settings** to configure your API keys first.")
