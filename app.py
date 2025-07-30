import streamlit as st
from fpdf import FPDF
import requests
import os

st.set_page_config(page_title="📊 Credit Report System", layout="wide")

# Simulated login
st.sidebar.title("🔐 User Login")
user_role = st.sidebar.selectbox("Select your role", ["client", "admin"])
user_email = st.sidebar.text_input("Your Email", value="client@example.com")

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
        "DOB": dob,
        "Address": address,
        "Credit Score": credit_score,
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
        pdf.multi_cell(0, 10, f"{key}: {value}")
        pdf.ln(1)

    filename = f"/tmp/{name.replace(' ', '_')}_credit_report.pdf"
    pdf.output(filename)
    return filename

# Webhook function
def send_to_n8n(filepath, webhook_url, metadata):
    with open(filepath, "rb") as f:
        files = {"file": f}
        response = requests.post(webhook_url, files=files, data=metadata)
    return response.status_code

# In-memory "CRM" database
if "reports" not in st.session_state:
    st.session_state.reports = {}

# Handle form submission
if submitted:
    file_path = generate_pdf()
    
    # Store for CRM view
    st.session_state.reports[user_email] = {
        "name": name,
        "file": file_path,
        "email": user_email
    }

    # Send to n8n
    n8n_webhook = "https://your-n8n-webhook-url.com/webhook"
    status = send_to_n8n(file_path, n8n_webhook, {"email": user_email})

    if status == 200:
        st.success("✅ Report generated and sent to n8n webhook.")
    else:
        st.error("❌ Failed to send report to webhook.")

# CRM Dashboard
st.markdown("---")
st.title("📁 Credit Report Dashboard")

if user_role == "admin":
    for user, report in st.session_state.reports.items():
        st.subheader(report["name"])
        st.write("Email:", user)
        st.download_button("📥 Download Report", open(report["file"], "rb"), file_name=os.path.basename(report["file"]))
else:
    report = st.session_state.reports.get(user_email)
    if report:
        st.subheader(report["name"])
        st.download_button("📥 Download Your Report", open(report["file"], "rb"), file_name=os.path.basename(report["file"]))
    else:
        st.info("No reports found for your email.")
