import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_stats, get_outreach_log, get_candidates

st.markdown('<div class="page-header">Reports</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Pipeline performance and outreach analytics</div>', unsafe_allow_html=True)

try:
    stats = get_stats()
    by_status = stats.get("by_status", {})
    by_channel = stats.get("by_channel", {})
    total = max(stats.get("total", 1), 1)

    # ─── TOP METRICS ──────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Candidates", stats.get("total", 0))
    c2.metric("Outreach Sent", stats.get("sent", 0))
    closed = stats.get("closed", 0)
    conversion = f"{int((closed / total) * 100)}%" if total > 0 else "0%"
    c3.metric("Closed", closed)
    c4.metric("Conversion Rate", conversion)

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # ─── PIPELINE FUNNEL ──────────────────────────────────────────────────────
    with col1:
        st.markdown('<div class="mono-label" style="margin-bottom:16px;">PIPELINE FUNNEL</div>', unsafe_allow_html=True)

        stages_ordered = ["new", "contacted", "responded", "screened", "negotiating", "closed", "rejected"]
        stage_colors = {
            "new": "#60a5fa", "contacted": "#e8c547", "responded": "#a855f7",
            "screened": "#fb923c", "negotiating": "#f59e0b",
            "closed": "#4ecb71", "rejected": "#ef4444"
        }

        for stage in stages_ordered:
            count = by_status.get(stage, 0)
            pct = int((count / total) * 100)
            color = stage_colors.get(stage, "#55556a")
            bar_width = max(pct, 2) if count > 0 else 0

            st.markdown(f"""
            <div style="margin-bottom:14px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
                    <span style="font-family:'Space Mono',monospace; font-size:11px;
                                 color:#8888aa; text-transform:uppercase; letter-spacing:0.06em;">{stage}</span>
                    <span style="font-family:'Space Mono',monospace; font-size:13px; color:{color};">
                        {count} <span style="font-size:10px; color:#55556a;">({pct}%)</span>
                    </span>
                </div>
                <div style="background:#1e1e2e; border-radius:3px; height:6px; overflow:hidden;">
                    <div style="width:{bar_width}%; background:{color}; height:6px; border-radius:3px;
                                transition:width 0.5s ease;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ─── CHANNEL BREAKDOWN ────────────────────────────────────────────────────
    with col2:
        st.markdown('<div class="mono-label" style="margin-bottom:16px;">OUTREACH BY CHANNEL</div>', unsafe_allow_html=True)

        total_sent = max(stats.get("sent", 1), 1)
        channel_colors = {"whatsapp": "#4ecb71", "email": "#60a5fa", "voice": "#e8c547", "manual": "#8888aa"}
        channel_icons = {"whatsapp": "💬", "email": "📧", "voice": "📞", "manual": "✍️"}

        if by_channel:
            for ch, count in by_channel.items():
                pct = int((count / total_sent) * 100)
                color = channel_colors.get(ch, "#55556a")
                icon = channel_icons.get(ch, "📨")
                st.markdown(f"""
                <div style="margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                        <span style="font-size:13px; color:#f0f0f8;">{icon} {ch.upper()}</span>
                        <span style="font-family:'Space Mono',monospace; font-size:13px; color:{color};">{count}</span>
                    </div>
                    <div style="background:#1e1e2e; border-radius:3px; height:6px;">
                        <div style="width:{pct}%; background:{color}; height:6px; border-radius:3px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#55556a; font-size:13px;">No outreach sent yet.</div>', unsafe_allow_html=True)

    # ─── OUTREACH LOG ─────────────────────────────────────────────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="mono-label" style="margin-bottom:12px;">RECENT OUTREACH LOG</div>', unsafe_allow_html=True)

    try:
        log = get_outreach_log()[:50]
        if log:
            table_rows = ""
            for entry in log:
                ts = entry.get("sent_at", "")
                try:
                    from datetime import datetime
                    ts = datetime.fromisoformat(ts).strftime("%d %b %H:%M")
                except Exception:
                    pass

                cname = (entry.get("candidates") or {}).get("name", "—")
                status_color = "#4ecb71" if entry.get("status") == "sent" else "#ef4444"
                ch = entry.get("channel", "—")
                ch_icon = {"whatsapp": "💬", "email": "📧", "voice": "📞"}.get(ch, "📨")

                table_rows += f"""
                <tr style="border-bottom:1px solid #1e1e2e;">
                    <td style="padding:10px 12px; font-size:13px; color:#f0f0f8;">{cname}</td>
                    <td style="padding:10px 12px; font-size:13px; color:#8888aa;">{ch_icon} {ch}</td>
                    <td style="padding:10px 12px;">
                        <span style="color:{status_color}; font-family:'Space Mono',monospace; font-size:11px;">
                            {entry.get('status','—').upper()}
                        </span>
                    </td>
                    <td style="padding:10px 12px; font-size:11px; color:#55556a; font-family:'Space Mono',monospace;">{ts}</td>
                </tr>
                """

            st.markdown(f"""
            <div style="background:#16161f; border:1px solid #2a2a3a; border-radius:6px; overflow:hidden;">
                <table style="width:100%; border-collapse:collapse;">
                    <thead>
                        <tr style="border-bottom:1px solid #2a2a3a;">
                            <th style="padding:10px 12px; text-align:left; font-family:'Space Mono',monospace;
                                       font-size:10px; color:#55556a; letter-spacing:0.08em;">CANDIDATE</th>
                            <th style="padding:10px 12px; text-align:left; font-family:'Space Mono',monospace;
                                       font-size:10px; color:#55556a; letter-spacing:0.08em;">CHANNEL</th>
                            <th style="padding:10px 12px; text-align:left; font-family:'Space Mono',monospace;
                                       font-size:10px; color:#55556a; letter-spacing:0.08em;">STATUS</th>
                            <th style="padding:10px 12px; text-align:left; font-family:'Space Mono',monospace;
                                       font-size:10px; color:#55556a; letter-spacing:0.08em;">TIME</th>
                        </tr>
                    </thead>
                    <tbody>{table_rows}</tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#55556a; font-size:13px;">No outreach logged yet.</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Could not load outreach log: {e}")

except Exception as e:
    st.error(f"Could not load report data: {e}")
    st.info("Ensure Supabase is configured in Settings.")
