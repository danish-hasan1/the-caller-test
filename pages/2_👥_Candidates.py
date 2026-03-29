import streamlit as st
import sys, os, csv, io
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import get_candidates, upsert_candidate, delete_candidate, get_jds, update_candidate_status

st.markdown('<div class="page-header">Candidates</div>', unsafe_allow_html=True)
st.markdown('<div class="page-sub">Manage your candidate pipeline · Add manually or import from CSV</div>', unsafe_allow_html=True)

STATUS_OPTIONS = ["new", "contacted", "responded", "screened", "negotiating", "closed", "rejected"]

tab1, tab2, tab3 = st.tabs(["ALL CANDIDATES", "ADD CANDIDATE", "IMPORT CSV"])

# ─── TAB 1: ALL CANDIDATES ─────────────────────────────────────────────────────
with tab1:
    col_filter, col_search = st.columns([2, 3])
    with col_filter:
        status_filter = st.selectbox("Filter by status", ["all"] + STATUS_OPTIONS, key="status_filter")
    with col_search:
        search = st.text_input("Search name / role / company", placeholder="e.g. Rahul, Software Engineer...", key="search")

    try:
        candidates = get_candidates(None if status_filter == "all" else status_filter)

        if search:
            s = search.lower()
            candidates = [c for c in candidates if
                s in (c.get("name") or "").lower() or
                s in (c.get("current_role") or "").lower() or
                s in (c.get("current_company") or "").lower()
            ]

        st.markdown(f'<div class="mono-label" style="margin:16px 0 12px;">{len(candidates)} CANDIDATES</div>', unsafe_allow_html=True)

        if not candidates:
            st.info("No candidates found. Add one using the ADD CANDIDATE tab.")
        else:
            for c in candidates:
                status = c.get("status", "new")
                jd_title = (c.get("job_descriptions") or {}).get("title", "No JD")

                with st.expander(f"**{c.get('name','—')}** · {c.get('current_role','—')} · {jd_title}"):
                    col1, col2, col3 = st.columns([2, 2, 1])

                    with col1:
                        st.markdown(f"""
                        <div class="mono-label">CONTACT</div>
                        <div style="font-size:13px; color:#f0f0f8; margin-top:6px;">
                            📧 {c.get('email') or '—'}<br>
                            📱 {c.get('phone') or '—'}<br>
                            📍 {c.get('location') or '—'}
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        st.markdown(f"""
                        <div class="mono-label">PROFILE</div>
                        <div style="font-size:13px; color:#f0f0f8; margin-top:6px;">
                            🏢 {c.get('current_company') or '—'}<br>
                            📅 {c.get('experience_years') or '—'} yrs exp<br>
                            💰 {c.get('current_salary') or '—'} → {c.get('expected_salary') or '—'}
                        </div>
                        """, unsafe_allow_html=True)

                    with col3:
                        st.markdown(f'<span class="status-badge status-{status}">{status}</span>', unsafe_allow_html=True)
                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                        new_status = st.selectbox(
                            "Change status",
                            STATUS_OPTIONS,
                            index=STATUS_OPTIONS.index(status),
                            key=f"status_{c['id']}"
                        )
                        if new_status != status:
                            if st.button("Update", key=f"update_{c['id']}"):
                                update_candidate_status(c["id"], new_status)
                                st.rerun()

                    if c.get("notes"):
                        st.markdown(f'<div style="font-size:12px; color:#55556a; margin-top:8px; padding-top:8px; border-top:1px solid #2a2a3a;">📝 {c["notes"]}</div>', unsafe_allow_html=True)

                    btn_col1, btn_col2 = st.columns([1, 5])
                    with btn_col1:
                        if st.button("🗑 Delete", key=f"del_{c['id']}"):
                            delete_candidate(c["id"])
                            st.rerun()
                    with btn_col2:
                        st.markdown(
                            f'<a href="/Conversations?candidate_id={c["id"]}" target="_self">'
                            f'<button style="background:transparent; border:1px solid #2a2a3a; color:#8888aa; '
                            f'border-radius:6px; padding:4px 16px; cursor:pointer; font-size:12px; font-family:Space Mono,monospace;">'
                            f'💬 Open Conversation</button></a>',
                            unsafe_allow_html=True
                        )

    except Exception as e:
        st.error(f"Error loading candidates: {e}")

# ─── TAB 2: ADD CANDIDATE ─────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="mono-label" style="margin-bottom:16px;">CANDIDATE DETAILS</div>', unsafe_allow_html=True)

    try:
        jds = get_jds()
        jd_options = {j["title"]: j["id"] for j in jds}
    except Exception:
        jd_options = {}

    with st.form("add_candidate_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name *")
            email = st.text_input("Email")
            phone = st.text_input("Phone (with country code, e.g. +91...)")
            location = st.text_input("Location")
            source = st.selectbox("Source", ["manual", "sourcer_app", "linkedin", "referral", "other"])

        with col2:
            current_role = st.text_input("Current Role")
            current_company = st.text_input("Current Company")
            experience_years = st.number_input("Experience (years)", min_value=0, max_value=50, value=0)
            current_salary = st.text_input("Current Salary (e.g. ₹12 LPA)")
            expected_salary = st.text_input("Expected Salary")

        col3, col4 = st.columns(2)
        with col3:
            notice_period = st.text_input("Notice Period (e.g. 30 days)")
            jd_selected = st.selectbox("Assign to JD", ["— None —"] + list(jd_options.keys()))

        with col4:
            status = st.selectbox("Initial Status", STATUS_OPTIONS)
            notes = st.text_area("Notes", height=100)

        submitted = st.form_submit_button("ADD CANDIDATE", use_container_width=True)

        if submitted:
            if not name:
                st.error("Name is required.")
            else:
                data = {
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "location": location,
                    "source": source,
                    "current_role": current_role,
                    "current_company": current_company,
                    "experience_years": experience_years,
                    "current_salary": current_salary,
                    "expected_salary": expected_salary,
                    "notice_period": notice_period,
                    "jd_id": jd_options.get(jd_selected) if jd_selected != "— None —" else None,
                    "status": status,
                    "notes": notes,
                }
                try:
                    upsert_candidate(data)
                    st.success(f"✅ {name} added successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

# ─── TAB 3: IMPORT CSV ─────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="mono-label" style="margin-bottom:12px;">BULK IMPORT</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="caller-card">
        <div style="font-size:13px; color:#8888aa; line-height:1.8;">
            Upload a CSV with these columns:<br>
            <code style="color:#e8c547; font-size:12px;">
            name, email, phone, location, current_role, current_company, experience_years,
            current_salary, expected_salary, notice_period, notes
            </code><br><br>
            All columns except <strong>name</strong> are optional.
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        jds = get_jds()
        jd_options = {j["title"]: j["id"] for j in jds}
    except Exception:
        jd_options = {}

    jd_for_import = st.selectbox("Assign imported candidates to JD", ["— None —"] + list(jd_options.keys()), key="import_jd")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded:
        try:
            content = uploaded.read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(content))
            rows = list(reader)

            st.markdown(f'<div class="mono-label" style="margin:12px 0;">PREVIEW — {len(rows)} ROWS</div>', unsafe_allow_html=True)

            preview_data = []
            for r in rows[:5]:
                preview_data.append({
                    "Name": r.get("name", ""),
                    "Email": r.get("email", ""),
                    "Phone": r.get("phone", ""),
                    "Role": r.get("current_role", ""),
                })
            st.dataframe(preview_data, use_container_width=True)

            if st.button(f"IMPORT {len(rows)} CANDIDATES", use_container_width=True):
                jd_id = jd_options.get(jd_for_import) if jd_for_import != "— None —" else None
                success, fail = 0, 0
                for r in rows:
                    try:
                        upsert_candidate({
                            "name": r.get("name", "").strip(),
                            "email": r.get("email", "").strip(),
                            "phone": r.get("phone", "").strip(),
                            "location": r.get("location", "").strip(),
                            "current_role": r.get("current_role", "").strip(),
                            "current_company": r.get("current_company", "").strip(),
                            "experience_years": int(r.get("experience_years", 0) or 0),
                            "current_salary": r.get("current_salary", "").strip(),
                            "expected_salary": r.get("expected_salary", "").strip(),
                            "notice_period": r.get("notice_period", "").strip(),
                            "notes": r.get("notes", "").strip(),
                            "jd_id": jd_id,
                            "source": "csv_import",
                            "status": "new",
                        })
                        success += 1
                    except Exception:
                        fail += 1

                st.success(f"✅ Imported {success} candidates." + (f" {fail} failed." if fail else ""))
                st.rerun()

        except Exception as e:
            st.error(f"Error reading CSV: {e}")
