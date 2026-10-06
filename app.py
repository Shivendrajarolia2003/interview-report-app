import streamlit as st
import pandas as pd
import json
import os
from config import (
    ADMIN_PASSWORD, STANDARD_FIELDS, STATUS_PENDING, STATUS_GENERATING,
    STATUS_GENERATED, STATUS_NEEDS_REVIEW, STATUS_APPROVED, STATUS_SENT, STATUS_FAILED
)
from utils.database import (
    init_db, create_batch, save_students, get_batches, get_students_by_batch,
    update_report, update_report_status, update_batch_report_statuses, get_email_logs,
    delete_batch, reset_all_data
)
from utils.excel_reader import read_excel_file
from utils.validation import auto_detect_columns, validate_and_parse_excel
from utils.report_generator import generate_ai_report, generate_batch_ai_insights
from utils.pdf_generator import create_pdf_report
from utils.email_sender import send_interview_report_email
from utils.vision_extractor import extract_students_from_image

# Initialize Database on app start
init_db()

st.set_page_config(
    page_title="AI Interview Report & Auto Email System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 700; color: #1E293B; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1rem; color: #64748B; margin-bottom: 2rem; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; padding: 15px; border-radius: 8px; text-align: center; }
    .status-badge { font-weight: 600; padding: 4px 8px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎓 AI Interview Report & Auto Email System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Internal Company Platform for Student Feedback Generation & Email Dispatch</div>', unsafe_allow_html=True)

# Sidebar - Settings & Active Batch Selector
st.sidebar.title("⚡ Control Panel")

# Gemini API Key Override in UI
user_api_key = st.sidebar.text_input("Google Gemini API Key", type="password", help="Enter key to generate AI reports")
if user_api_key:
    os.environ["GEMINI_API_KEY"] = user_api_key

# SMTP Settings in Sidebar
with st.sidebar.expander("📧 Email Server Settings (SMTP)", expanded=False):
    smtp_server = st.text_input("SMTP Host", value=os.getenv("SMTP_SERVER", "smtp.gmail.com"))
    smtp_port = st.number_input("SMTP Port", value=int(os.getenv("SMTP_PORT", 587)))
    smtp_username = st.text_input("Sender Email (Gmail)", value=os.getenv("SMTP_USERNAME", ""))
    smtp_password = st.text_input("App Password", type="password", help="For Gmail: Use 16-digit App Password from Google Account Security")
    sender_name = st.text_input("Sender Display Name", value=os.getenv("SENDER_NAME", "Company Recruitment Team"))
    
    if smtp_username:
        os.environ["SMTP_USERNAME"] = smtp_username
    if smtp_password:
        os.environ["SMTP_PASSWORD"] = smtp_password

# Select Active Batch
batches = get_batches()
batch_options = {f"Batch #{b['id']} — {b['batch_name']} ({b['uploaded_at'][:10]})": b['id'] for b in batches}

selected_batch_id = None
if batch_options:
    selected_batch_label = st.sidebar.selectbox("Select Active Batch", list(batch_options.keys()))
    selected_batch_id = batch_options[selected_batch_label]

# Data Management Section in Sidebar
with st.sidebar.expander("🗑️ Manage & Reset Data History", expanded=False):
    if selected_batch_id:
        if st.button("❌ Delete Currently Selected Batch"):
            delete_batch(selected_batch_id)
            st.success("Selected batch deleted!")
            st.rerun()
            
    if st.button("🧹 Clear ALL Batches & History (Fresh Start)"):
        reset_all_data()
        st.session_state.clear()
        st.success("All data cleared! Starting with a clean slate.")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.info("💡 **Workflow Steps:**\n1. Upload Excel / Sheet Photo\n2. AI Extract & Validate Data\n3. Generate AI Reports\n4. Review & Approve\n5. Send Emails\n6. Track Status")

# Navigation Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 1. Upload Excel / Photo Notes",
    "🤖 2. AI Report Generator",
    "📝 3. Review & Approve Reports",
    "📧 4. Auto Email Delivery",
    "📊 5. Batch Analytics & HR Insights"
])

# ==========================================
# TAB 1: Upload Excel / Photo Notes
# ==========================================
with tab1:
    st.subheader("Step 1: Upload Interview Data (Excel File OR Photo of Interview Sheet)")
    
    upload_type = st.radio("Choose Input Type:", ["📊 Excel / CSV File", "📸 Photo of Handwritten/Printed Assessment Notes"], horizontal=True)
    
    df = None
    
    if upload_type == "📊 Excel / CSV File":
        col_upload, col_sample, col_real, col_multi = st.columns([2, 1, 1, 1])
        with col_upload:
            uploaded_file = st.file_uploader("Choose an Excel (.xlsx) or CSV file", type=["xlsx", "xls", "csv"])
        with col_sample:
            st.write("")
            st.write("")
            if st.button("📄 Sample Data (5 Students)"):
                sample_path = os.path.join(os.path.dirname(__file__), "data", "sample_input.xlsx")
                if os.path.exists(sample_path):
                    with open(sample_path, "rb") as f:
                        uploaded_file = f
        with col_real:
            st.write("")
            st.write("")
            if st.button("🔥 Real Email Test"):
                real_path = os.path.join(os.path.dirname(__file__), "data", "real_test.xlsx")
                if os.path.exists(real_path):
                    with open(real_path, "rb") as f:
                        uploaded_file = f
        with col_multi:
            st.write("")
            st.write("")
            if st.button("🎓 Multi-Field 10 Students"):
                multi_path = os.path.join(os.path.dirname(__file__), "data", "multi_field_students.xlsx")
                if os.path.exists(multi_path):
                    with open(multi_path, "rb") as f:
                        uploaded_file = f

        if uploaded_file:
            try:
                df = read_excel_file(uploaded_file)
            except Exception as e:
                st.error(f"Error reading file: {e}")
                
    else:
        # Photo Upload Section
        st.info("💡 Supports single or multi-candidate sheets across any professional field (Doctor, Lawyer, Software Engineer, Teacher, Designer, Data Analyst, etc.).")
        image_file = st.file_uploader("Upload Photo of Interview Sheet (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])
        if image_file:
            st.image(image_file, caption="Uploaded Assessment Sheet", width=450)
            if st.button("👁️ Extract Candidate Data from Photo with AI Vision", type="primary"):
                with st.spinner("Gemini AI Vision is scanning candidate evaluation matrix..."):
                    success, msg, extracted_df = extract_students_from_image(image_file)
                    if success:
                        st.session_state["extracted_df"] = extracted_df
                        st.success(msg)
                    else:
                        st.error(msg)
                        
            if "extracted_df" in st.session_state:
                df = st.session_state["extracted_df"]

    if df is not None and not df.empty:
        st.success(f"Data Loaded Successfully! Found **{len(df)}** candidate record(s).")
        st.dataframe(df, use_container_width=True)
        
        st.markdown("### Step 2: Map Fields & Validate Data")
        auto_mapped = auto_detect_columns(df.columns)
        mapping_cols = st.columns(3)
        
        user_mapping = {}
        for idx, (field_key, field_info) in enumerate(STANDARD_FIELDS.items()):
            col_target = mapping_cols[idx % 3]
            options = ["-- Skip / Not Present --"] + list(df.columns)
            default_idx = 0
            if auto_mapped.get(field_key) and auto_mapped[field_key] in df.columns:
                default_idx = list(df.columns).index(auto_mapped[field_key]) + 1
                
            selected = col_target.selectbox(
                f"{field_info['label']} {'*' if field_info['required'] else ''}",
                options=options,
                index=default_idx,
                key=f"map_{field_key}"
            )
            if selected != "-- Skip / Not Present --":
                user_mapping[field_key] = selected
            else:
                user_mapping[field_key] = None

        st.markdown("---")
        batch_title = st.text_input("Batch Name / Description", value=f"Batch {len(batches) + 1} - {pd.Timestamp.now().strftime('%b %d %H:%M')}")
        
        if st.button("🔍 Validate Data & Save Batch", type="primary"):
            if not user_mapping.get("student_name") or not user_mapping.get("student_email"):
                st.error("Please map required fields: 'Student Name' and 'Student Email'.")
            else:
                parsed_result = validate_and_parse_excel(df, user_mapping)
                st.session_state["parsed_result"] = parsed_result
                
                # Save to DB
                new_batch_id = create_batch(
                    batch_title,
                    parsed_result["total_students"],
                    parsed_result["valid_count"],
                    parsed_result["problem_count"]
                )
                save_students(new_batch_id, parsed_result["students"])
                st.success(f"Batch saved successfully! Batch ID: #{new_batch_id}")
                st.rerun()

    # Display Current Batch Validation Summary if batch selected
    if selected_batch_id:
        st.markdown("---")
        st.markdown("### Active Batch Preview & Data Validation")
        students = get_students_by_batch(selected_batch_id)
        
        tot = len(students)
        val = sum(1 for s in students if s['is_valid'])
        prob = tot - val
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Students Found", tot)
        m2.metric("Valid Records", val, delta="Ready for AI", delta_color="normal")
        m3.metric("Problematic Records", prob, delta="- Needs Attention" if prob > 0 else "Clean", delta_color="inverse")
        
        valid_df = []
        problem_df = []
        for s in students:
            row_dict = {
                "ID": s['id'],
                "Name": s['name'],
                "Email": s['email'],
                "Scores": ", ".join([f"{k}: {v}" for k, v in s['scores'].items()]),
                "Comments": s['interviewer_comments'][:60] + "..." if len(s['interviewer_comments']) > 60 else s['interviewer_comments'],
                "Status": "Valid" if s['is_valid'] else "Invalid"
            }
            if s['is_valid']:
                valid_df.append(row_dict)
            else:
                row_dict["Validation Errors"] = ", ".join(s['validation_errors'])
                problem_df.append(row_dict)
                
        if problem_df:
            st.warning("⚠️ Problematic Records Found (Will be skipped in AI generation):")
            st.dataframe(pd.DataFrame(problem_df), use_container_width=True)
            
        if valid_df:
            st.subheader("Valid Student Records")
            st.dataframe(pd.DataFrame(valid_df), use_container_width=True)

# ==========================================
# TAB 2: AI Report Generator
# ==========================================
with tab2:
    st.subheader("Step 3: Generate AI Feedback Reports")
    
    if not selected_batch_id:
        st.info("Please select or upload a batch first in Tab 1.")
    else:
        students = get_students_by_batch(selected_batch_id)
        valid_students = [s for s in students if s['is_valid']]
        
        st.write(f"Active Batch: **#{selected_batch_id}** | Valid Students: **{len(valid_students)}**")
        
        c1, c2 = st.columns([2, 1])
        with c1:
            if st.button("🚀 Generate AI Reports for All Valid Students", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, s in enumerate(valid_students):
                    status_text.text(f"Generating report for {s['name']} ({i+1}/{len(valid_students)})...")
                    
                    # Generate report
                    report_md = generate_ai_report(s)
                    pdf_path = create_pdf_report(s['name'], report_md)
                    
                    update_report(
                        s['report_id'],
                        report_markdown=report_md,
                        overall_assessment=f"AI Generated Feedback for {s['name']}",
                        pdf_path=pdf_path,
                        status=STATUS_GENERATED
                    )
                    progress_bar.progress((i + 1) / len(valid_students))
                    
                status_text.text("✨ All reports generated successfully!")
                st.success("Reports generated! Proceed to Tab 3 for Admin Review & Approval.")
                st.rerun()

        # Display current generation status table
        report_data = []
        for s in students:
            report_data.append({
                "Student Name": s['name'],
                "Email": s['email'],
                "Data Valid": "Yes" if s['is_valid'] else "No",
                "Report Status": s['report_status'],
                "PDF Generated": "Yes" if s['pdf_path'] and os.path.exists(s['pdf_path']) else "No",
                "Last Updated": s['report_updated_at'] or "N/A"
            })
        st.table(pd.DataFrame(report_data))

# ==========================================
# TAB 3: Review & Approve Reports
# ==========================================
with tab3:
    st.subheader("Step 4: Admin Report Review, Edit & Approval")
    
    if not selected_batch_id:
        st.info("Please select a batch from the sidebar.")
    else:
        students = get_students_by_batch(selected_batch_id)
        
        col_actions, col_space = st.columns([2, 2])
        with col_actions:
            if st.button("✅ Approve ALL Generated Reports in Batch"):
                update_batch_report_statuses(selected_batch_id, STATUS_GENERATED, STATUS_APPROVED)
                st.success("All generated reports approved! Ready for email sending.")
                st.rerun()
                
        st.markdown("---")
        
        # Student Selector for inspection
        student_dict = {f"{s['name']} ({s['email']}) — [{s['report_status']}]": s for s in students if s['report_markdown']}
        
        if not student_dict:
            st.info("No AI reports generated yet for this batch. Go to Tab 2 to generate reports.")
        else:
            selected_student_key = st.selectbox("Select Student Report to Inspect / Edit", list(student_dict.keys()))
            student_obj = student_dict[selected_student_key]
            
            st.markdown(f"### Inspecting Report: **{student_obj['name']}**")
            st.caption(f"Current Status: **{student_obj['report_status']}**")
            
            # Inline Editor
            report_text = st.text_area("Report Markdown Content (Editable)", value=student_obj['report_markdown'], height=400)
            
            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
            
            with btn_col1:
                if st.button("💾 Save Changes"):
                    new_pdf = create_pdf_report(student_obj['name'], report_text)
                    update_report(student_obj['report_id'], report_text, pdf_path=new_pdf, status=STATUS_GENERATED)
                    st.success("Report updated and PDF regenerated!")
                    st.rerun()
                    
            with btn_col2:
                if st.button("✅ Approve This Report"):
                    update_report_status(student_obj['report_id'], STATUS_APPROVED)
                    st.success(f"Report for {student_obj['name']} APPROVED!")
                    st.rerun()
                    
            with btn_col3:
                if st.button("🔄 Regenerate with AI"):
                    new_md = generate_ai_report(student_obj)
                    new_pdf = create_pdf_report(student_obj['name'], new_md)
                    update_report(student_obj['report_id'], new_md, pdf_path=new_pdf, status=STATUS_GENERATED)
                    st.success("Report regenerated!")
                    st.rerun()
                    
            with btn_col4:
                if student_obj['pdf_path'] and os.path.exists(student_obj['pdf_path']):
                    with open(student_obj['pdf_path'], "rb") as pdf_file:
                        st.download_button("📥 Download PDF", data=pdf_file, file_name=os.path.basename(student_obj['pdf_path']), mime="application/pdf")

# ==========================================
# TAB 4: Auto Email Delivery
# ==========================================
with tab4:
    st.subheader("Step 5: Automated Email Dispatch")
    st.caption("Human Approval Protection: Emails will strictly ONLY send for Approved reports.")
    
    if not os.getenv("SMTP_USERNAME") or not os.getenv("SMTP_PASSWORD"):
        st.warning("⚠️ **Email Server Credentials Not Configured**: Please open **Control Panel -> 📧 Email Server Settings (SMTP)** in sidebar to enter your Sender Email & Password, or edit `.env` file.")
    
    if not selected_batch_id:
        st.info("Select a batch from sidebar.")
    else:
        students = get_students_by_batch(selected_batch_id)
        approved_students = [s for s in students if s['report_status'] in [STATUS_APPROVED, STATUS_FAILED]]
        
        st.metric("Approved Reports Ready for Sending / Retrying", len(approved_students))
        
        if st.button("📨 Send / Retry Emails for Approved Students", type="primary", disabled=len(approved_students) == 0):
            progress = st.progress(0)
            email_status = st.empty()
            
            sent_count = 0
            fail_count = 0
            
            for i, s in enumerate(approved_students):
                email_status.text(f"Sending email to {s['name']} ({s['email']})...")
                
                success, msg = send_interview_report_email(
                    recipient_email=s['email'],
                    student_name=s['name'],
                    report_id=s['report_id'],
                    pdf_path=s['pdf_path'],
                    report_markdown=s['report_markdown'],
                    smtp_username=smtp_username,
                    smtp_password=smtp_password,
                    smtp_server=smtp_server,
                    smtp_port=smtp_port,
                    sender_name=sender_name
                )
                if success:
                    sent_count += 1
                else:
                    fail_count += 1
                    st.error(f"Failed sending to {s['email']}: {msg}")
                    
                progress.progress((i + 1) / len(approved_students))
                
            st.success(f"Finished sending! Successfully Sent: {sent_count} | Failed: {fail_count}")
            st.rerun()

        # Email Status Table
        st.markdown("### Email Status Log for Active Batch")
        logs = get_email_logs(selected_batch_id)
        if logs:
            st.table(pd.DataFrame(logs)[['student_name', 'recipient_email', 'status', 'sent_at', 'error_message']])
        else:
            st.info("No email attempts recorded yet for this batch.")

# ==========================================
# TAB 5: Batch Analytics & HR Insights
# ==========================================
with tab5:
    st.subheader("Step 6: Batch Dashboard & AI HR Insights")
    
    if selected_batch_id:
        students = get_students_by_batch(selected_batch_id)
        
        tot = len(students)
        generated = sum(1 for s in students if s['report_status'] in [STATUS_GENERATED, STATUS_APPROVED, STATUS_SENT])
        approved = sum(1 for s in students if s['report_status'] in [STATUS_APPROVED, STATUS_SENT])
        sent = sum(1 for s in students if s['report_status'] == STATUS_SENT)
        failed = sum(1 for s in students if s['report_status'] == STATUS_FAILED)
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Students", tot)
        c2.metric("Reports Generated", generated)
        c3.metric("Approved Reports", approved)
        c4.metric("Emails Sent", sent, delta=f"Failed: {failed}" if failed else "100% Success")
        
        st.markdown("---")
        st.subheader("📊 Structured Score Averages")
        
        all_scores = {}
        for s in students:
            for k, v in s['scores'].items():
                if isinstance(v, (int, float)):
                    all_scores.setdefault(k, []).append(v)
                    
        if all_scores:
            avg_scores = {k: round(sum(v)/len(v), 1) for k, v in all_scores.items()}
            st.bar_chart(pd.Series(avg_scores))
            
            st.markdown("##### Category Score Averages:")
            score_cols = st.columns(len(avg_scores))
            for i, (k, v) in enumerate(avg_scores.items()):
                score_cols[i % len(avg_scores)].metric(k, f"{v} / 10")
        else:
            st.info("No numerical score fields found in batch to compute averages.")
            
        st.markdown("---")
        st.subheader("🧠 Batch-Level AI Insights & HR Training Plan")
        st.caption("Gemini AI analyzes the entire batch's scores, comments, strengths, and weaknesses to generate an executive summary & 30-day curriculum.")
        
        if st.button("⚡ Generate AI Batch Insights & Training Plan", type="primary"):
            with st.spinner("AI is analyzing batch data and generating executive insights..."):
                batch_insights_md = generate_batch_ai_insights(students)
                st.session_state[f"batch_insights_{selected_batch_id}"] = batch_insights_md
                st.success("Batch AI Insights Generated!")
                
        # Display Batch Insights if generated
        insights_key = f"batch_insights_{selected_batch_id}"
        if insights_key in st.session_state:
            st.markdown(st.session_state[insights_key])
        else:
            # Generate default mock/analysis on load
            default_insights = generate_batch_ai_insights(students)
            st.markdown(default_insights)
