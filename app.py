import streamlit as st
from fpdf import FPDF
import requests
import os
import tempfile
import PyPDF2
from io import BytesIO
from datetime import datetime, date
import json
import random

st.set_page_config(page_title="📊 Credit Report System", layout="wide")

# Demo Profiles Data
DEMO_PROFILES = {
    "john.doe@example.com": {
        "role": "client",
        "name": "John Michael Doe",
        "ssn": "123-45-6789",
        "dob": date(1985, 3, 15),
        "address": "1234 Maple Street, Apt 5B\nSpringfield, IL 62701",
        "phone": "(555) 123-4567",
        "employment": "Software Engineer at TechCorp Inc.",
        "annual_income": 85000,
        "credit_data": {
            "credit_score": 742,
            "payment_history": "Excellent payment history with 98% on-time payments over the last 7 years. Only 2 late payments recorded in 2019 (30 days late on credit card). No missed payments in the last 24 months. Consistent payment patterns across all accounts.",
            "credit_utilization": "Current utilization at 18% ($3,600 used of $20,000 total credit limit). Recommended to keep below 30%. Has maintained low utilization for past 3 years. Highest utilization was 45% in 2020 during pandemic.",
            "inquiries": "3 hard inquiries in the last 24 months: Auto loan (Jan 2023), Credit card application (Aug 2023), Mortgage pre-approval (Dec 2023). 12 soft inquiries from existing creditors for account reviews.",
            "public_records": "No bankruptcies, liens, or judgments on record. Clean public record history. No foreclosures or repossessions.",
            "collections": "No current collections accounts. One medical collection from 2018 for $150 was paid and removed from report in 2019.",
            "bankruptcies": "No bankruptcy filings on record. No Chapter 7 or Chapter 13 proceedings.",
            "account_age": "Average account age: 8 years 4 months. Oldest account opened in 2010 (credit card). Newest account opened in January 2023 (auto loan).",
            "open_accounts": "12 open accounts: 4 credit cards, 1 auto loan, 1 mortgage, 2 store cards, 3 utility accounts, 1 cell phone account. All accounts in good standing.",
            "closed_accounts": "8 closed accounts: 3 credit cards (closed by customer), 2 store cards (closed by customer), 1 personal loan (paid off), 1 student loan (paid off), 1 auto loan (paid off).",
            "derogatory_marks": "2 derogatory marks: 30-day late payment on Visa card (March 2019), 30-day late payment on store card (April 2019). No recent derogatory marks.",
            "total_debt": "$285,450 total debt breakdown: Mortgage $245,000, Auto loan $18,200, Credit cards $3,600, Personal loan $18,650. Debt-to-income ratio: 28%.",
            "monthly_payments": "$2,180 total monthly payments: Mortgage $1,650, Auto loan $385, Credit cards $145 (minimum payments). Payment-to-income ratio: 31%.",
            "high_balance": "Highest balance account: Primary mortgage with $245,000 remaining balance. Original loan amount $280,000 in 2020.",
            "recent_activity": "Last 90 days: Auto loan payment $385 (on time), Mortgage payment $1,650 (on time), 4 credit card payments totaling $890, Opened new rewards credit card with $5,000 limit.",
            "account_types": "Mix includes: Revolving credit (6 accounts), Installment loans (4 accounts), Mortgage (1 account), Open accounts (1 account). Good credit mix diversity.",
            "credit_limits": "$20,000 total revolving credit limit across 6 cards: Chase Sapphire $8,000, Discover $5,000, Capital One $3,000, Store Card 1 $2,000, Store Card 2 $1,500, Gas Card $500.",
            "charge_offs": "No charge-off accounts on record. All accounts maintained in good standing.",
            "late_payments": "2 total late payments in credit history: Both 30-day late payments in 2019. No 60-day, 90-day, or 120+ day late payments on record.",
            "loan_types": "Current loans: Conventional mortgage (30-year fixed at 3.25%), Auto loan (5-year term at 4.1%), Personal loan (3-year term at 8.9%).",
            "student_loans": "Student loans paid off in full in 2021. Original balance $35,000, paid over 8 years. No current student loan debt.",
            "auto_loans": "Current auto loan: 2023 Honda Accord, $18,200 remaining balance, $385/month payment, 4.1% APR, 48 months remaining. Previous auto loan paid off in 2022.",
            "mortgage_info": "Primary residence mortgage: $245,000 balance, $1,650/month payment (P&I), 3.25% fixed rate, 25 years remaining. Property value estimated at $320,000. LTV ratio: 76%.",
            "revolving_accounts": "6 revolving accounts with $20,000 total credit limit. Average age 6 years. All accounts current with no overlimit fees in past 24 months.",
            "installment_loans": "3 installment loans: Mortgage ($245,000), Auto loan ($18,200), Personal loan ($18,650). All payments current and on-time.",
            "hard_inquiries": "3 hard inquiries in 24 months: TransUnion (auto loan - Jan 2023), Experian (credit card - Aug 2023), Equifax (mortgage - Dec 2023). Average 1.5 inquiries per year.",
            "soft_inquiries": "12 soft inquiries in 12 months from existing creditors for account management and pre-approved offers. Does not impact credit score.",
            "credit_score_history": "Score trend: 2020: 698, 2021: 715, 2022: 728, 2023: 742. Steady improvement over 4 years. Peak score: 748 (Oct 2023).",
            "employment_status": "Full-time employed at TechCorp Inc. since 2018. Software Engineer, stable income $85,000/year. Previous employment: Junior Developer (2015-2018).",
            "income_info": "Annual income: $85,000 gross, $62,000 net. Monthly gross: $7,083. Income verified through pay stubs and tax returns. 3% annual increases.",
            "notes": "Overall excellent credit profile with strong payment history and low utilization. Recommended for prime lending rates. Consider paying down personal loan to improve DTI ratio."
        }
    },
    "sarah.johnson@example.com": {
        "role": "client", 
        "name": "Sarah Elizabeth Johnson",
        "ssn": "987-65-4321",
        "dob": date(1992, 8, 22),
        "address": "5678 Oak Avenue, Unit 12\nAustin, TX 78701",
        "phone": "(555) 987-6543",
        "employment": "Marketing Manager at Digital Solutions LLC",
        "annual_income": 72000,
        "credit_data": {
            "credit_score": 680,
            "payment_history": "Good payment history with 89% on-time payments. 8 late payments in the last 2 years, mostly 30-day lates. Recent improvement with no late payments in last 6 months. Working to rebuild payment consistency.",
            "credit_utilization": "High utilization at 68% ($10,200 used of $15,000 total credit limit). Major factor impacting score. Recommended to pay down balances below 30%. Utilization increased during job transition in 2022.",
            "inquiries": "7 hard inquiries in the last 24 months: 3 credit card applications, 2 personal loan applications, 1 auto loan, 1 apartment rental. Higher than recommended frequency.",
            "public_records": "No bankruptcies or liens. One small claims judgment for $800 from 2021 (medical bill dispute) - currently being paid through payment plan.",
            "collections": "2 collections accounts: Medical collection $450 (in payment plan), Utility collection $180 (paid in full last month). Working to resolve remaining collection.",
            "bankruptcies": "No bankruptcy filings. Considered Chapter 13 in 2021 but chose debt management plan instead.",
            "account_age": "Average account age: 4 years 8 months. Oldest account opened in 2016 (student credit card). Building credit history length.",
            "open_accounts": "9 open accounts: 5 credit cards, 1 auto loan, 2 store cards, 1 personal loan. Some accounts showing high balances.",
            "closed_accounts": "4 closed accounts: 2 credit cards (closed by creditor due to inactivity), 1 store card (closed by customer), 1 cell phone account (paid off).",
            "derogatory_marks": "8 derogatory marks: 6 late payments (30-day), 1 late payment (60-day), 1 collection account. Most recent late payment 6 months ago.",
            "total_debt": "$78,950 total debt: Auto loan $22,500, Credit cards $10,200, Personal loan $8,750, Student loans $37,500. Debt-to-income ratio: 44% (high).",
            "monthly_payments": "$1,890 total monthly payments: Auto loan $420, Credit cards $310 (minimum), Personal loan $285, Student loans $875. Payment-to-income ratio: 38%.",
            "high_balance": "Highest balance account: Federal student loans with $37,500 remaining balance. Currently in income-driven repayment plan.",
            "recent_activity": "Last 90 days: All payments made on time, Paid off utility collection $180, Applied for debt consolidation loan (denied), Reduced credit card balance by $500.",
            "account_types": "Mix includes: Revolving credit (7 accounts), Installment loans (2 accounts). Could benefit from more diverse credit mix.",
            "credit_limits": "$15,000 total revolving credit limit: Capital One $4,000, Chase $3,500, Discover $3,000, Store Card 1 $2,000, Store Card 2 $1,500, Gas Card $1,000.",
            "charge_offs": "No charge-off accounts. All accounts remain open and active despite high balances.",
            "late_payments": "8 late payments total: 6 payments 30-days late, 1 payment 60-days late, 1 payment 90-days late (2022). Improvement trend in recent months.",
            "loan_types": "Current loans: Auto loan (6-year term at 6.8%), Personal loan (5-year term at 12.9%), Federal student loans (various terms, 4.5% average).",
            "student_loans": "Federal student loans: $37,500 balance across 4 loans. Income-driven repayment plan, $875/month. Originally borrowed $45,000 for bachelor's degree.",
            "auto_loans": "Current auto loan: 2021 Toyota Camry, $22,500 remaining balance, $420/month payment, 6.8% APR, 54 months remaining. Higher rate due to credit score at time of purchase.",
            "mortgage_info": "No mortgage. Currently renting apartment at $1,200/month. Saving for down payment but high DTI ratio preventing mortgage approval currently.",
            "revolving_accounts": "7 revolving accounts with high utilization. Working on debt paydown strategy. Several accounts near credit limits.",
            "installment_loans": "3 installment loans: Auto loan ($22,500), Personal loan ($8,750), Student loans ($37,500). All payments current after recent improvements.",
            "hard_inquiries": "7 hard inquiries in 24 months - higher than recommended. Recent inquiries for debt consolidation and credit limit increases.",
            "soft_inquiries": "15 soft inquiries in 12 months from credit monitoring and pre-approved offers. Higher frequency due to credit rebuilding efforts.",
            "credit_score_history": "Score trend: 2020: 720, 2021: 650 (job loss impact), 2022: 635, 2023: 680. Recovery in progress after difficult period.",
            "employment_status": "Full-time Marketing Manager since January 2023. Previous unemployment period (6 months in 2021-2022) impacted credit. Income stabilizing.",
            "income_info": "Annual income: $72,000 gross, $52,000 net. Monthly gross: $6,000. Income increased 20% with new position. Building emergency fund.",
            "notes": "Credit rebuilding in progress. High utilization and recent late payments main concerns. Positive trend with recent payment improvements. Recommend debt consolidation and utilization reduction."
        }
    },
    "admin@creditreports.com": {
        "role": "admin",
        "name": "Michael Robert Chen",
        "ssn": "456-78-9123", 
        "dob": date(1978, 11, 8),
        "address": "9999 Executive Blvd, Suite 200\nRockville, MD 20852",
        "phone": "(555) 456-7890",
        "employment": "Senior Credit Analyst at Credit Solutions Corp",
        "annual_income": 125000,
        "credit_data": {
            "credit_score": 820,
            "payment_history": "Exceptional payment history with 100% on-time payments over 15+ years. Never missed a payment across all accounts. Exemplary payment discipline and financial management.",
            "credit_utilization": "Optimal utilization at 3% ($1,200 used of $40,000 total credit limit). Maintains low utilization through strategic balance management and high credit limits.",
            "inquiries": "1 hard inquiry in the last 24 months: Mortgage refinance (March 2023). Minimal inquiry activity demonstrates established credit profile.",
            "public_records": "Clean public record with no bankruptcies, liens, judgments, or foreclosures. Exemplary legal and financial standing.",
            "collections": "No collections accounts ever reported. No history of accounts sent to collections.",
            "bankruptcies": "No bankruptcy filings. Strong financial management throughout credit history.",
            "account_age": "Average account age: 12 years 8 months. Oldest account opened in 1995 (first credit card in college). Excellent credit history length.",
            "open_accounts": "15 open accounts: 8 credit cards, 1 mortgage, 2 investment accounts, 2 business credit cards, 1 HELOC, 1 auto loan. Diverse and well-managed portfolio.",
            "closed_accounts": "12 closed accounts: All closed in good standing by customer choice. Includes paid-off loans and consolidated accounts.",
            "derogatory_marks": "Zero derogatory marks on credit report. Perfect payment and account management history.",
            "total_debt": "$425,000 total debt: Mortgage $380,000, HELOC $25,000, Auto loan $15,000, Credit cards $1,200, Business cards $3,800. Strategic debt management.",
            "monthly_payments": "$3,200 total monthly payments: Mortgage $2,400, HELOC $300, Auto loan $450, Credit cards paid in full monthly. Excellent payment capacity.",
            "high_balance": "Highest balance account: Primary residence mortgage with $380,000 remaining balance. Property value $650,000, excellent equity position.",
            "recent_activity": "Last 90 days: All payments on time, Refinanced mortgage saving $400/month, Increased credit limit on rewards card to $15,000, Paid off business expenses in full.",
            "account_types": "Excellent credit mix: Revolving credit (10 accounts), Installment loans (3 accounts), Mortgage (1 account), HELOC (1 account). Optimal diversity.",
            "credit_limits": "$40,000 total revolving credit limit: Amex Platinum $15,000, Chase Sapphire Reserve $12,000, Citi Double Cash $8,000, Business cards $5,000 combined.",
            "charge_offs": "No charge-off accounts in credit history. All accounts maintained in excellent standing.",
            "late_payments": "Zero late payments in entire credit history. Perfect payment record across all accounts and time periods.",
            "loan_types": "Current loans: Conventional mortgage (30-year fixed at 2.75%), HELOC (variable at 4.25%), Auto loan (3-year term at 2.9%).",
            "student_loans": "Student loans paid off in 2005. Originally $28,000 for MBA, paid off early with no late payments.",
            "auto_loans": "Current auto loan: 2023 BMW X5, $15,000 remaining balance, $450/month payment, 2.9% APR, 33 months remaining. Excellent rate due to credit profile.",
            "mortgage_info": "Primary residence: $380,000 balance, $2,400/month payment, 2.75% fixed rate (refinanced 2023), 27 years remaining. Property value $650,000, LTV: 58%.",
            "revolving_accounts": "10 revolving accounts with excellent management. Average utilization 3%. All accounts aged 5+ years with perfect payment history.",
            "installment_loans": "3 installment loans: Mortgage ($380,000), HELOC ($25,000), Auto loan ($15,000). All payments automated and current.",
            "hard_inquiries": "1 hard inquiry in 24 months for mortgage refinance. Minimal inquiry activity reflects established credit needs.",
            "soft_inquiries": "8 soft inquiries in 12 months from existing creditors for account reviews and limit increases. Normal activity for high-credit profile.",
            "credit_score_history": "Score trend: 2020: 815, 2021: 818, 2022: 822, 2023: 820. Consistently excellent scores in 800+ range for over 10 years.",
            "employment_status": "Senior Credit Analyst with 15+ years experience. Stable employment with consistent income growth. Expert in credit analysis and risk assessment.",
            "income_info": "Annual income: $125,000 gross, $85,000 net. Monthly gross: $10,417. Additional investment income $15,000/year. Strong financial position.",
            "notes": "Exemplary credit profile representing ideal credit management. Perfect payment history, optimal utilization, excellent credit mix. Qualifies for best available rates and terms."
        }
    }
}

# Initialize session state
if "reports" not in st.session_state:
    st.session_state.reports = {}
if "n8n_webhook_url" not in st.session_state:
    st.session_state.n8n_webhook_url = "https://your-n8n-webhook-url.com/webhook"
if "current_profile" not in st.session_state:
    st.session_state.current_profile = None

# Sidebar Configuration
st.sidebar.title("🔐 User Login")

# Demo Profile Selection
st.sidebar.subheader("👥 Demo Profiles")
profile_options = {
    "Select a demo profile...": None,
    "John Doe (Excellent Credit - 742)": "john.doe@example.com",
    "Sarah Johnson (Fair Credit - 680)": "sarah.johnson@example.com", 
    "Michael Chen (Admin - Exceptional Credit - 820)": "admin@creditreports.com"
}

selected_profile = st.sidebar.selectbox("Choose Demo Profile", list(profile_options.keys()))

if profile_options[selected_profile]:
    st.session_state.current_profile = DEMO_PROFILES[profile_options[selected_profile]]
    user_email = profile_options[selected_profile]
    user_role = st.session_state.current_profile["role"]
    
    # Display profile info
    with st.sidebar.expander("👤 Profile Details"):
        st.write(f"**Name:** {st.session_state.current_profile['name']}")
        st.write(f"**Role:** {st.session_state.current_profile['role'].title()}")
        st.write(f"**Email:** {user_email}")
        st.write(f"**Credit Score:** {st.session_state.current_profile['credit_data']['credit_score']}")
        st.write(f"**Employment:** {st.session_state.current_profile['employment']}")
        st.write(f"**Income:** ${st.session_state.current_profile['annual_income']:,}")
else:
    # Manual entry
    user_role = st.sidebar.selectbox("Select your role", ["client", "admin"])
    user_email = st.sidebar.text_input("Your Email", value="client@example.com")
    st.session_state.current_profile = None

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
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_file:
            if filename.endswith('.pdf'):
                tmp_file.write(file_content.getvalue())
            else:
                tmp_file.write(file_content.getvalue())
            tmp_file_path = tmp_file.name
        
        with open(tmp_file_path, "rb") as f:
            files = {"file": (filename, f, "application/octet-stream")}
            data = {
                "email": metadata.get("email", ""),
                "filename": filename,
                "file_type": "uploaded_report"
            }
            response = requests.post(webhook_url, files=files, data=data)
        
        os.unlink(tmp_file_path)
        return response.status_code
    except Exception as e:
        st.sidebar.error(f"Error sending to n8n: {str(e)}")
        return 500

# Handle file upload
if uploaded_file is not None:
    st.sidebar.write(f"📄 **File:** {uploaded_file.name}")
    st.sidebar.write(f"📏 **Size:** {uploaded_file.size} bytes")
    
    if uploaded_file.type == "application/pdf":
        extracted_text = extract_text_from_pdf(uploaded_file)
    else:
        extracted_text = extract_text_from_txt(uploaded_file)
    
    if extracted_text:
        with st.sidebar.expander("👁️ Preview Content"):
            st.text_area("File Content", extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text, height=150)
        
        if st.sidebar.button("🚀 Send to n8n"):
            uploaded_file.seek(0)
            
            status = send_uploaded_file_to_n8n(
                uploaded_file, 
                uploaded_file.name, 
                st.session_state.n8n_webhook_url,
                {"email": user_email}
            )
            
            if status == 200:
                st.sidebar.success("✅ File sent to n8n successfully!")
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

# Show current profile info if demo selected
if st.session_state.current_profile:
    st.info(f"🎭 **Demo Mode Active** - Using profile: {st.session_state.current_profile['name']} (Credit Score: {st.session_state.current_profile['credit_data']['credit_score']})")

# Auto-populate form if demo profile selected
if st.session_state.current_profile:
    profile = st.session_state.current_profile
    default_name = profile["name"]
    default_ssn = profile["ssn"] 
    default_dob = profile["dob"]
    default_address = profile["address"]
    credit_data = profile["credit_data"]
else:
    default_name = ""
    default_ssn = ""
    default_dob = date.today()
    default_address = ""
    credit_data = {}

# Input Form
with st.form("credit_report_form"):
    st.subheader("📝 Client Information")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value=default_name)
        ssn = st.text_input("SSN", value=default_ssn)
        dob = st.date_input("Date of Birth", value=default_dob)
    with col2:
        if st.session_state.current_profile:
            st.text_input("Phone", value=st.session_state.current_profile["phone"], disabled=True)
            st.text_input("Employment", value=st.session_state.current_profile["employment"], disabled=True)
            st.number_input("Annual Income", value=st.session_state.current_profile["annual_income"], disabled=True)
    
    address = st.text_area("Current Address", value=default_address)
    
    st.subheader("📊 Credit Report Sections")
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Core Metrics", "💳 Account Details", "📋 Payment History", "📊 Additional Info"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            credit_score = st.number_input("Credit Score", 300, 850, value=credit_data.get("credit_score", 650))
            payment_history = st.text_area("1. Payment History", value=credit_data.get("payment_history", ""), height=100)
            credit_utilization = st.text_area("2. Credit Utilization", value=credit_data.get("credit_utilization", ""), height=100)
            inquiries = st.text_area("3. Credit Inquiries", value=credit_data.get("inquiries", ""), height=100)
        with col2:
            public_records = st.text_area("4. Public Records", value=credit_data.get("public_records", ""), height=100)
            collections = st.text_area("5. Collections", value=credit_data.get("collections", ""), height=100)
            bankruptcies = st.text_area("6. Bankruptcies", value=credit_data.get("bankruptcies", ""), height=100)
            account_age = st.text_area("7. Average Account Age", value=credit_data.get("account_age", ""), height=100)
    
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            open_accounts = st.text_area("8. Number of Open Accounts", value=credit_data.get("open_accounts", ""), height=100)
            closed_accounts = st.text_area("9. Closed Accounts", value=credit_data.get("closed_accounts", ""), height=100)
            derogatory_marks = st.text_area("10. Derogatory Marks", value=credit_data.get("derogatory_marks", ""), height=100)
            total_debt = st.text_area("11. Total Debt", value=credit_data.get("total_debt", ""), height=100)
            monthly_payments = st.text_area("12. Monthly Payments", value=credit_data.get("monthly_payments", ""), height=100)
        with col2:
            high_balance = st.text_area("13. Highest Balance Account", value=credit_data.get("high_balance", ""), height=100)
            recent_activity = st.text_area("14. Recent Credit Activity", value=credit_data.get("recent_activity", ""), height=100)
            account_types = st.text_area("15. Credit Account Types", value=credit_data.get("account_types", ""), height=100)
            credit_limits = st.text_area("16. Total Credit Limit", value=credit_data.get("credit_limits", ""), height=100)
            charge_offs = st.text_area("17. Charge-Off Accounts", value=credit_data.get("charge_offs", ""), height=100)
    
    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            late_payments = st.text_area("18. Late Payments", value=credit_data.get("late_payments", ""), height=100)
            loan_types = st.text_area("19. Loan Types Held", value=credit_data.get("loan_types", ""), height=100)
            student_loans = st.text_area("20. Student Loans", value=credit_data.get("student_loans", ""), height=100)
            auto_loans = st.text_area("21. Auto Loans", value=credit_data.get("auto_loans", ""), height=100)
            mortgage_info = st.text_area("22. Mortgage Info", value=credit_data.get("mortgage_info", ""), height=100)
        with col2:
            revolving_accounts = st.text_area("23. Revolving Credit", value=credit_data.get("revolving_accounts", ""), height=100)
            installment_loans = st.text_area("24. Installment Loans", value=credit_data.get("installment_loans", ""), height=100)
            hard_inquiries = st.text_area("25. Hard Inquiries", value=credit_data.get("hard_inquiries", ""), height=100)
            soft_inquiries = st.text_area("26. Soft Inquiries", value=credit_data.get("soft_inquiries", ""), height=100)
            credit_score_history = st.text_area("27. Credit Score History", value=credit_data.get("credit_score_history", ""), height=100)
    
    with tab4:
        col1, col2 = st.columns(2)
        with col1:
            employment_status = st.text_area("28. Employment Status", value=credit_data.get("employment_status", ""), height=100)
            income_info = st.text_area("29. Reported Income", value=credit_data.get("income_info", ""), height=100)
        with col2:
            notes = st.text_area("30. Additional Notes", value=credit_data.get("notes", ""), height=100)
    
    submitted = st.form_submit_button("🚀 Generate Credit Report", use_container_width=True)

# Generate PDF function
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "COMPREHENSIVE CREDIT REPORT", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 5, f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", ln=True, align='C')
    pdf.ln(10)
    
    # Client Information Section
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "CLIENT INFORMATION", ln=True)
    pdf.set_font("Arial", "", 10)
    
    client_info = [
        ("Name", name),
        ("SSN", ssn),
        ("Date of Birth", str(dob)),
        ("Address", address),
        ("Credit Score", str(credit_score))
    ]
    
    for label, value in client_info:
        pdf.cell(40, 6, f"{label}:", 0, 0)
        pdf.multi_cell(0, 6, str(value))
        pdf.ln(1)
    
    pdf.ln(5)
    
    # Credit Report Sections
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "DETAILED CREDIT ANALYSIS", ln=True)
    pdf.set_font("Arial", "", 9)
    
    fields = {
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
        if value.strip():  # Only include non-empty fields
            pdf.set_font("Arial", "B", 10)
            pdf.cell(0, 6, key, ln=True)
            pdf.set_font("Arial", "", 9)
            pdf.multi_cell(0, 5, str(value))
            pdf.ln(2)
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 5, "This report is generated for informational purposes only.", ln=True, align='C')
    pdf.cell(0, 5, "Credit Report System - Confidential Document", ln=True, align='C')
    
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
                "file_type": "generated_report",
                "client_name": metadata.get("name", ""),
                "credit_score": metadata.get("credit_score", "")
            }
            response = requests.post(webhook_url, files=files, data=data)
        return response.status_code
    except Exception as e:
        st.error(f"Error sending to n8n: {str(e)}")
        return 500

# Handle form submission
if submitted and name:
    with st.spinner("🔄 Generating comprehensive credit report..."):
        file_path = generate_pdf()
        
        # Store for CRM view
        st.session_state.reports[user_email] = {
            "name": name,
            "file": file_path,
            "email": user_email,
            "type": "generated",
            "credit_score": credit_score,
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Send to n8n
        status = send_to_n8n(
            file_path, 
            st.session_state.n8n_webhook_url, 
            {"email": user_email, "name": name, "credit_score": credit_score}
        )
        
        if status == 200:
            st.success("✅ Comprehensive credit report generated and sent to n8n webhook successfully!")
            st.balloons()
        else:
            st.error(f"❌ Failed to send report to webhook. Status: {status}")
            st.warning("Report was generated but not sent to n8n. Check webhook configuration.")

# CRM Dashboard
st.markdown("---")
st.title("📁 Credit Report Dashboard")

if user_role == "admin":
    st.subheader("👨‍💼 Admin View - All Reports")
    
    # Summary metrics
    if st.session_state.reports:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Reports", len(st.session_state.reports))
        with col2:
            generated_count = sum(1 for r in st.session_state.reports.values() if r.get('type') == 'generated')
            st.metric("Generated Reports", generated_count)
        with col3:
            uploaded_count = sum(1 for r in st.session_state.reports.values() if r.get('type') == 'uploaded')
            st.metric("Uploaded Reports", uploaded_count)
        with col4:
            avg_score = sum(r.get('credit_score', 0) for r in st.session_state.reports.values() if r.get('credit_score')) / max(1, len([r for r in st.session_state.reports.values() if r.get('credit_score')]))
            st.metric("Avg Credit Score", f"{avg_score:.0f}")
    
    st.markdown("---")
    
    if st.session_state.reports:
        for user, report in st.session_state.reports.items():
            with st.expander(f"📄 {report['name']} ({report.get('type', 'unknown').title()}) - Score: {report.get('credit_score', 'N/A')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Email:**", report.get('email', 'N/A'))
                    st.write("**Type:**", report.get('type', 'unknown').title())
                    if report.get('credit_score'):
                        st.write("**Credit Score:**", report['credit_score'])
                with col2:
                    if report.get('generated_date'):
                        st.write("**Generated:**", report['generated_date'])
                
                if report.get('type') == 'uploaded' and 'content' in report:
                    st.text_area("Content Preview", report['content'], height=100, key=f"admin_preview_{user}")
                
                if report.get('file') and report['file'] != "uploaded_file":
                    try:
                        with open(report["file"], "rb") as f:
                            st.download_button(
                                "📥 Download Report", 
                                f.read(), 
                                file_name=f"{report['name'].replace(' ', '_')}_credit_report.pdf",
                                key=f"admin_download_{user}",
                                mime="application/pdf"
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
            with st.expander(f"📄 {report['name']} ({report.get('type', 'unknown').title()}) - Score: {report.get('credit_score', 'N/A')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Type:**", report.get('type', 'unknown').title())
                    if report.get('credit_score'):
                        st.write("**Credit Score:**", report['credit_score'])
                with col2:
                    if report.get('generated_date'):
                        st.write("**Generated:**", report['generated_date'])
                
                if report.get('type') == 'uploaded' and 'content' in report:
                    st.text_area("Content Preview", report['content'], height=100, key=f"client_preview_{user}")
                
                if report.get('file') and report['file'] != "uploaded_file":
                    try:
                        with open(report["file"], "rb") as f:
                            st.download_button(
                                "📥 Download Your Report", 
                                f.read(), 
                                file_name=f"{report['name'].replace(' ', '_')}_credit_report.pdf",
                                key=f"client_download_{user}",
                                mime="application/pdf"
                            )
                    except FileNotFoundError:
                        st.warning("File not found - may have been cleaned up")
    else:
        st.info("No reports found for your email.")

# Footer with enhanced information
st.markdown("---")
st.markdown("### 💡 System Features & Tips")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**📁 File Management**")
    st.markdown("- Upload existing credit reports (PDF/TXT)")
    st.markdown("- Generate comprehensive new reports")
    st.markdown("- Download reports in PDF format")
    st.markdown("- Automatic file organization")

with col2:
    st.markdown("**🔗 n8n Integration**")
    st.markdown("- Configure webhook URL in sidebar")
    st.markdown("- Test connection before sending")
    st.markdown("- Automatic file transmission")
    st.markdown("- Status monitoring and feedback")

with col3:
    st.markdown("**👥 Demo Profiles**")
    st.markdown("- **John Doe**: Excellent credit (742)")
    st.markdown("- **Sarah Johnson**: Fair credit (680)")
    st.markdown("- **Michael Chen**: Exceptional credit (820)")
    st.markdown("- Complete credit histories included")

st.markdown("---")
st.markdown("**🔒 Credit Report System v2.0** - Comprehensive credit analysis and reporting platform")
