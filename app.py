import streamlit as st
from fpdf import FPDF
import requests
import os
import tempfile
import PyPDF2
from io import BytesIO

st.set_page_config(page_title="📊 Credit Report System", layout="wide")

# Initialize session state
if "reports" not in st.session_state:
    st.session_state.reports = {}
if "n8n_webhook_url" not in st.session_state:
    st.session_state.n8n_webhook_url = "https://your-n8n-webhook-url.com/webhook"

# Sidebar Configuration
st.sidebar.title("🔐 User Login")
user_role = st.sidebar.selectbox("Select your role", ["client", "admin"])
user_email = st.sidebar.text_input("Your Email", value="client@example.com")

st.sidebar.markdown("---")

# n8n Webhook Configuration
st.sidebar.subheader("🔗 n8n Webhook Configuration")
webhook_url = st.sidebar.text_input(
    "n8n Webhook URL", 
    value=st.session_state.n8n_webhook_url,
    help="Enter your n8n webhook URL"
)
if st.sidebar.button("💾 Save Webhook URL"):
    st.session_state.n8n_webhook_url = webhook_url
    st.sidebar.success("✅ Webhook URL saved!")

st.sidebar.markdown("---")

# File Upload Section
st.sidebar.subheader("📁 Upload Credit Report")
uploaded_file = st.sidebar.file_uploader(
    "Choose a file", 
    type=['pdf', 'txt'],
    help="Upload existing credit report (PDF or TXT format)"
)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.sidebar.error(f"Error reading PDF: {str(e)}")
        return None

def extract_text_from_txt(txt_file):
    """Extract text from uploaded TXT file"""
    try:
        return txt_file.read().decode('utf-8')
    except Exception as e:
        st.sidebar.error(f"Error reading TXT: {str(e)}")
        return None

def send_uploaded_file_to_n8n(file_content, filename, webhook_url, metadata):
    """Send uploaded file to n8n webhook"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            if filename.endswith('.pdf'):
                tmp_file.write(file_content.getvalue())
            else:  # txt file
                tmp_file.write(file_content.getvalue())
            tmp_file_path = tmp_file.name
        
        # Send to n8n
        with open(tmp_file_path, "rb") as f:
            files = {"file": (filename, f, "application/octet-stream")}
            data = {
                "email": metadata.get("email", ""),
                "filename": filename,
                "file_type": "uploaded_report"
            }
            response = requests.post(webhook_url, files=files, data=data)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        return response.status_code
    except Exception as e:
        st.sidebar.error(f"Error sending to n8n: {str(e)}")
        return 500

# Handle file upload
if uploaded_file is not None:
    st.sidebar.write(f"📄 **File:** {uploaded_file.name}")
    st.sidebar.write(f"📏 **Size:** {uploaded_file.size} bytes")
    
    # Extract text content for preview
    if uploaded_file.type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    else:  # txt file
        extracted_text = extract_text_from_txt(uploaded_file)
    
    if extracted_text:
        # Show preview
        with st.sidebar.expander("👁️ Preview Content"):
            st.text_area("File Content", extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text, height=150)
        
        # Send to n8n button
        if st.sidebar.button("🚀 Send to n8n"):
            # Reset file pointer
            uploaded_file.seek(0)
            
            status = send_uploaded_file_to_n8n(
                uploaded_file, 
                uploaded_file.name, 
                st.session_state.n8n_webhook_url,
                {"email": user_email}
            )
            
            if status == 200:
                st.sidebar.success("✅ File sent to n8n successfully!")
                
                # Store in session state for CRM
                st.session_state.reports[f"{user_email}_uploaded_{uploaded_file.name}"] = {
                    "name": f"Uploaded: {uploaded_file.name}",
                    "file": "uploaded_file",
                    "email": user_email,
                    "type": "uploaded",
                    "content": extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text
                }
            else:
                st.sidebar.error(f"❌ Failed to send file. Status: {status}")

st.sidebar.markdown("---")

# Test webhook connection
if st.sidebar.button("🧪 Test Webhook Connection"):
    try:
        test_data = {"test": "connection", "email": user_email}
        response = requests.post(st.session_state.n8n_webhook_url, json=test_data, timeout=10)
        if response.status_code == 200:
            st.sidebar.success("✅ Webhook connection successful!")
        else:
            st.sidebar.warning(f"⚠️ Webhook responded with status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.sidebar.error(f"❌ Webhook connection failed: {str(e)}")

# Main Content
st.title("📄 Generate Full Credit Report")

# Input Form
with st.form("credit_report_form"):
    st.subheader("📝 Client Information")
    name = st.text_input("Full Name")
    ssn = st.text_input("SSN")
    dob = st.date_input("Date of Birth")
    address = st.text_area("Current Address")
    
    st.subheader("📊 Credit Report Sections")
    credit_score = st.number_input("Credit Score", 300, 850)
    payment_history = st.text_area("1. Payment History")
    credit_utilization = st.text_area("2. Credit Utilization")
    inquiries = st.text_area("3. Credit Inquiries")
    public_records = st.text_area("4. Public Records")
    collections = st.text_area("5. Collections")
    bankruptcies = st.text_area("6. Bankruptcies")
    account_age = st.text_area("7. Average Account Age")
    open_accounts = st.text_area("8. Number of Open Accounts")
    closed_accounts = st.text_area("9. Closed Accounts")
    derogatory_marks = st.text_area("10. Derogatory Marks")
    total_debt = st.text_area("11. Total Debt")
    monthly_payments = st.text_area("12. Monthly Payments")
    high_balance = st.text_area("13. Highest Balance Account")
    recent_activity = st.text_area("14. Recent Credit Activity")
    account_types = st.text_area("15. Credit Account Types")
    credit_limits = st.text_area("16. Total Credit Limit")
    charge_offs = st.text_area("17. Charge-Off Accounts")
    late_payments = st.text_area("18. Late Payments")
    loan_types = st.text_area("19. Loan Types Held")
    student_loans = st.text_area("20. Student Loans")
    auto_loans = st.text_area("21. Auto Loans")
    mortgage_info = st.text_area("22. Mortgage Info")
    revolving_accounts = st.text_area("23. Revolving Credit")
    installment_loans = st.text_area("24. Installment Loans")
    hard_inquiries = st.text_area("25. Hard Inquiries")
    soft_inquiries = st.text_area("26. Soft Inquiries")
    credit_score_history = st.text_area("27. Credit Score History")
    employment_status = st.text_area("28. Employment Status")
    income_info = st.text_area("29. Reported Income")
    notes = st.text_area("30. Additional Notes")
    
    submitted = st.form_submit_button("Generate Credit Report")

# Generate PDF
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, txt="Client Credit Report", ln=True, align='C')
    pdf.ln(10)
    
    fields = {
        "Name": name,
        "SSN": ssn,
        "DOB": str(dob),
        "Address": address,
        "Credit Score": str(credit_score),
        "1. Payment History": payment_history,
        "2. Credit Utilization": credit_utilization,
        "3. Credit Inquiries": inquiries,
        "4. Public Records": public_records,
        "5. Collections": collections,
        "6. Bankruptcies": bankruptcies,
        "7. Average Account Age": account_age,
        "8. Open Accounts": open_accounts,
        "9. Closed Accounts": closed_accounts,
        "10. Derogatory Marks": derogatory_marks,
        "11. Total Debt": total_debt,
        "12. Monthly Payments": monthly_payments,
        "13. Highest Balance": high_balance,
        "14. Recent Activity": recent_activity,
        "15. Account Types": account_types,
        "16. Credit Limits": credit_limits,
        "17. Charge-Offs": charge_offs,
        "18. Late Payments": late_payments,
        "19. Loan Types": loan_types,
        "20. Student Loans": student_loans,
        "21. Auto Loans": auto_loans,
        "22. Mortgage Info": mortgage_info,
        "23. Revolving Accounts": revolving_accounts,
        "24. Installment Loans": installment_loans,
        "25. Hard Inquiries": hard_inquiries,
        "26. Soft Inquiries": soft_inquiries,
        "27. Credit Score History": credit_score_history,
        "28. Employment Status": employment_status,
        "29. Reported Income": income_info,
        "30. Additional Notes": notes
    }
    
    for key, value in fields.items():
        pdf.multi_cell(0, 10, f"{key}: {str(value)}")
        pdf.ln(1)
    
    # Use tempfile for better cross-platform compatibility
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        filename = tmp_file.name
    
    pdf.output(filename)
    return filename

# Webhook function
def send_to_n8n(filepath, webhook_url, metadata):
    try:
        with open(filepath, "rb") as f:
            files = {"file": f}
            data = {
                "email": metadata.get("email", ""),
                "file_type": "generated_report"
            }
            response = requests.post(webhook_url, files=files, data=data)
        return response.status_code
    except Exception as e:
        st.error(f"Error sending to n8n: {str(e)}")
        return 500

# Handle form submission
if submitted and name:  # Ensure name is provided
    file_path = generate_pdf()
    
    # Store for CRM view
    st.session_state.reports[user_email] = {
        "name": name,
        "file": file_path,
        "email": user_email,
        "type": "generated"
    }
    
    # Send to n8n
    status = send_to_n8n(file_path, st.session_state.n8n_webhook_url, {"email": user_email})
    
    if status == 200:
        st.success("✅ Report generated and sent to n8n webhook.")
    else:
        st.error(f"❌ Failed to send report to webhook. Status: {status}")

# CRM Dashboard
st.markdown("---")
st.title("📁 Credit Report Dashboard")

if user_role == "admin":
    st.subheader("👨‍💼 Admin View - All Reports")
    if st.session_state.reports:
        for user, report in st.session_state.reports.items():
            with st.expander(f"📄 {report['name']} ({report.get('type', 'unknown')})"):
                st.write("**Email:**", report.get('email', 'N/A'))
                st.write("**Type:**", report.get('type', 'unknown'))
                
                if report.get('type') == 'uploaded' and 'content' in report:
                    st.text_area("Content Preview", report['content'], height=100, key=f"preview_{user}")
                
                if report.get('file') and report['file'] != "uploaded_file":
                    try:
                        with open(report["file"], "rb") as f:
                            st.download_button(
                                "📥 Download Report", 
                                f.read(), 
                                file_name=os.path.basename(report["file"]),
                                key=f"download_{user}"
                            )
                    except FileNotFoundError:
                        st.warning("File not found - may have been cleaned up")
    else:
        st.info("No reports available.")
else:
    st.subheader("👤 Client View - Your Reports")
    user_reports = {k: v for k, v in st.session_state.reports.items() 
                   if v.get('email') == user_email or k.startswith(user_email)}
    
    if user_reports:
        for user, report in user_reports.items():
            with st.expander(f"📄 {report['name']} ({report.get('type', 'unknown')})"):
                st.write("**Type:**", report.get('type', 'unknown'))
                
                if report.get('type') == 'uploaded' and 'content' in report:
                    st.text_area("Content Preview", report['content'], height=100, key=f"client_preview_{user}")
                
                if report.get('file') and report['file'] != "uploaded_file":
                    try:
                        with open(report["file"], "rb") as f:
                            st.download_button(
                                "📥 Download Your Report", 
                                f.read(), 
                                file_name=os.path.basename(report["file"]),
                                key=f"client_download_{user}"
                            )
                    except FileNotFoundError:
                        st.warning("File not found - may have been cleaned up")
    else:
        st.info("No reports found for your email.")

# Footer
st.markdown("---")
st.markdown("**💡 Tips:**")
st.markdown("- Upload existing credit reports (PDF/TXT) using the sidebar")
st.markdown("- Configure your n8n webhook URL in the sidebar")
st.markdown("- Test webhook connection before sending files")
st.markdown("- Generated and uploaded reports are stored in the dashboard")
