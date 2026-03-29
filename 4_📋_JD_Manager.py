import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_jds, upsert_jd, delete_jd

st.markdown('<div class="page-header">JD Manager</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Store and manage job descriptions used by the AI engine</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["ALL JDs", "ADD / EDIT JD"])

# ─── TAB 1: ALL JDs ───────────────────────────────────────────────────────────
with tab1:
    try:
        jds = get_jds()

        if not jds:
            st.info("No job descriptions yet. Add one in the ADD/EDIT JD tab.")
        else:
            st.markdown(f'<div class="mono-label" style="margin-bottom:16px;">{len(jds)} JOBs</div>', unsafe_allow_html=True)

            for jd in jds:
                with st.expander(f"**{jd.get('title','Untitled')}** · {jd.get('salary_range','Salary TBD')}"):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"""
                        <div class="mono-label" style="margin-bottom:6px;">DESCRIPTION</div>
                        <div style="font-size:13px; color:#f0f0f8; line-height:1.7; white-space:pre-wrap;">{jd.get('description','—')}</div>
                        """, unsafe_allow_html=True)

                        if jd.get("skills"):
                            st.markdown(f"""
                            <div class="mono-label" style="margin-top:12px; margin-bottom:6px;">SKILLS</div>
                            <div style="font-size:13px; color:#e8c547;">{jd.get('skills','')}</div>
                            """, unsafe_allow_html=True)

                        if jd.get("screening_questions"):
                            st.markdown(f"""
                            <div class="mono-label" style="margin-top:12px; margin-bottom:6px;">SCREENING QUESTIONS</div>
                            <div style="font-size:13px; color:#8888aa; white-space:pre-wrap;">{jd.get('screening_questions','')}</div>
                            """, unsafe_allow_html=True)

                        if jd.get("calendly_link"):
                            st.markdown(f"""
                            <div class="mono-label" style="margin-top:12px; margin-bottom:6px;">CALENDLY</div>
                            <div style="font-size:13px; color:#60a5fa;">🔗 {jd.get('calendly_link','')}</div>
                            """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                        <div style="background:#16161f; border:1px solid #2a2a3a; border-radius:6px;
                                    padding:12px; text-align:center;">
                            <div class="mono-label">SALARY</div>
                            <div style="font-size:14px; color:#e8c547; margin-top:6px; font-family:'Space Mono',monospace;">
                                {jd.get('salary_range','—')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                        if st.button("✏️ Edit", key=f"edit_{jd['id']}"):
                            st.session_state["editing_jd"] = jd
                            st.rerun()

                        if st.button("🗑 Delete", key=f"del_jd_{jd['id']}"):
                            delete_jd(jd["id"])
                            st.rerun()

    except Exception as e:
        st.error(f"Error loading JDs: {e}")

# ─── TAB 2: ADD / EDIT JD ─────────────────────────────────────────────────────
with tab2:
    editing = st.session_state.get("editing_jd", {})
    mode = "EDIT" if editing else "ADD"

    st.markdown(f'<div class="mono-label" style="margin-bottom:16px;">{mode} JOB DESCRIPTION</div>', unsafe_allow_html=True)

    if editing:
        if st.button("✕ Cancel Edit", key="cancel_edit"):
            del st.session_state["editing_jd"]
            st.rerun()

    with st.form("jd_form"):
        title = st.text_input("Job Title *", value=editing.get("title", ""))
        salary_range = st.text_input("Salary Range (e.g. ₹15-20 LPA)", value=editing.get("salary_range", ""))
        skills = st.text_input("Required Skills (comma-separated)", value=editing.get("skills", ""))
        description = st.text_area("Full JD / Role Description", value=editing.get("description", ""), height=200)
        screening_questions = st.text_area(
            "Screening Questions (one per line — AI will use these)",
            value=editing.get("screening_questions", ""),
            height=120,
            placeholder="What is your current CTC?\nAre you open to relocating?\nWhat is your notice period?"
        )
        calendly_link = st.text_input("Calendly / Interview Scheduling Link", value=editing.get("calendly_link", ""))
        additional_info = st.text_area("Additional Info for AI (perks, culture, WFH policy, etc.)",
                                        value=editing.get("additional_info", ""), height=80)

        submitted = st.form_submit_button(f"{mode} JD", use_container_width=True)

        if submitted:
            if not title:
                st.error("Title is required.")
            else:
                data = {
                    "title": title,
                    "salary_range": salary_range,
                    "skills": skills,
                    "description": description,
                    "screening_questions": screening_questions,
                    "calendly_link": calendly_link,
                    "additional_info": additional_info,
                }
                if editing:
                    data["id"] = editing["id"]

                try:
                    upsert_jd(data)
                    st.success(f"✅ JD '{title}' {'updated' if editing else 'added'} successfully!")
                    if editing:
                        del st.session_state["editing_jd"]
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
