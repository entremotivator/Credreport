import streamlit as st
from fpdf import FPDF
import requests
import os
import tempfile
import PyPDF2
from io import BytesIO, StringIO
from datetime import datetime, date, timedelta
import json
import pandas as pd
import csv
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import base64
import zipfile
import numpy as np

st.set_page_config(page_title="📊 Advanced Credit Report System", layout="wide")

# Google Services Configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]

# Enhanced Demo Profiles Data with more comprehensive information
DEMO_PROFILES = {
    "john.doe@example.com": {
        "role": "client",
        "profile_id": "PROF_001",
        "name": "John Michael Doe",
        "ssn": "123-45-6789",
        "dob": date(1985, 3, 15),
        "address": "1234 Maple Street, Apt 5B\nSpringfield, IL 62701",
        "phone": "(555) 123-4567",
        "employment": "Software Engineer at TechCorp Inc.",
        "annual_income": 85000,
        "employer_phone": "(555) 999-1234",
        "years_employed": 5.5,
        "previous_address": "789 Oak Street, Chicago, IL 60601",
        "marital_status": "Married",
        "dependents": 2,
        "housing_status": "Own",
        "monthly_rent_mortgage": 1650,
        "bank_name": "Chase Bank",
        "account_number": "****1234",
        "routing_number": "021000021",
        "credit_data": {
            "credit_score": 742,
            "credit_score_date": "2024-01-15",
            "previous_scores": "2023: 728, 2022: 715, 2021: 698",
            "score_source": "Experian",
            "payment_history": "Excellent payment history with 98% on-time payments over the last 7 years. Only 2 late payments recorded in 2019 (30 days late on credit card). No missed payments in the last 24 months. Consistent payment patterns across all accounts. Payment history accounts for 35% of credit score calculation.",
            "credit_utilization": "Current utilization at 18% ($3,600 used of $20,000 total credit limit). Recommended to keep below 30%. Has maintained low utilization for past 3 years. Highest utilization was 45% in 2020 during pandemic. Individual card utilization: Chase 15%, Discover 22%, Capital One 12%.",
            "inquiries": "3 hard inquiries in the last 24 months: Auto loan inquiry (Jan 15, 2023 - TransUnion), Credit card application (Aug 22, 2023 - Experian), Mortgage pre-approval (Dec 5, 2023 - Equifax). 12 soft inquiries from existing creditors for account reviews and promotional offers.",
            "public_records": "No bankruptcies, liens, tax liens, or judgments on record. Clean public record history spanning 15+ years. No foreclosures, repossessions, or wage garnishments. No civil suits or criminal financial violations.",
            "collections": "No current collections accounts. Historical: One medical collection from 2018 for $150 (disputed and removed from report in 2019). No utility, credit card, or loan collections ever reported.",
            "bankruptcies": "No bankruptcy filings on record. No Chapter 7, Chapter 11, or Chapter 13 proceedings. No debt discharge history. Strong financial management throughout economic downturns.",
            "account_age": "Average account age: 8 years 4 months. Oldest account opened in March 2010 (Chase Freedom credit card - still active). Newest account opened in January 2023 (Honda auto loan). Credit history length: 14 years total.",
            "open_accounts": "12 open accounts total: 4 credit cards (Chase Freedom $8000 limit, Discover It $5000, Capital One Venture $3000, Citi Double Cash $4000), 1 auto loan (Honda $18,200 balance), 1 mortgage (Primary residence $245,000), 2 store cards (Target $2000, Home Depot $1500), 3 utility accounts (Electric, Gas, Internet), 1 cell phone account (Verizon). All accounts in excellent standing.",
            "closed_accounts": "8 closed accounts in good standing: 3 credit cards (closed by customer for better rewards), 2 store cards (Macy's and Best Buy - closed by customer), 1 personal loan (paid off early in 2021), 1 student loan (paid off in 2021), 1 previous auto loan (2018 Toyota - paid off in 2022).",
            "derogatory_marks": "2 total derogatory marks: 30-day late payment on Chase Visa card (March 15, 2019 - $45 payment), 30-day late payment on Target store card (April 8, 2019 - $25 payment). No recent derogatory marks in past 48 months. Both incidents during temporary financial strain.",
            "total_debt": "$285,450 total debt breakdown: Primary mortgage $245,000 (3.25% APR, 25 years remaining), Auto loan $18,200 (4.1% APR, 48 months remaining), Credit cards $3,600 (average 18.9% APR), Personal loan $18,650 (8.9% APR, 18 months remaining). Current debt-to-income ratio: 28% (excellent).",
            "monthly_payments": "$2,180 total monthly debt payments: Mortgage $1,650 (P&I), Auto loan $385, Credit cards $145 (minimum payments, typically pays $400), Personal loan $520. Payment-to-income ratio: 31% (good). Never missed a payment in 24+ months.",
            "high_balance": "Highest balance account: Primary residence mortgage with $245,000 remaining balance. Original loan amount $280,000 in September 2020. Property current value estimated at $320,000. Loan-to-value ratio: 76%. Monthly payment includes taxes and insurance.",
            "recent_activity": "Last 90 days activity: Auto loan payment $385 (paid 3 days early), Mortgage payment $1,650 (autopay on 1st), 4 credit card payments totaling $890 (all paid in full), Opened new Chase Sapphire Reserve card with $12,000 limit (approved instantly), Increased Discover credit limit from $5,000 to $6,000.",
            "account_types": "Excellent credit mix diversity: Revolving credit (6 accounts - 40%), Installment loans (4 accounts - 27%), Mortgage (1 account - 7%), Open accounts (1 account - 7%). Mix includes retail cards, bank cards, auto loan, mortgage, and personal loan. Optimal variety for credit scoring.",
            "credit_limits": "$25,000 total revolving credit limit across 6 cards: Chase Sapphire Reserve $12,000, Chase Freedom $8,000, Discover It $6,000, Capital One Venture $3,000, Target RedCard $2,000, Home Depot $1,500, Citi Double Cash $4,000. Average limit per card: $4,167. Highest individual limit: $12,000.",
            "charge_offs": "No charge-off accounts on record throughout entire credit history. All accounts maintained in good standing even during financial difficulties. No accounts written off by creditors. Strong payment discipline maintained.",
            "late_payments": "2 total late payments in 14-year credit history: Both 30-day late payments in 2019 (Chase card and Target card). No 60-day, 90-day, or 120+ day late payments ever recorded. 98% on-time payment rate overall. Recent 24-month perfect payment history.",
            "loan_types": "Current loan portfolio: Conventional mortgage (30-year fixed at 3.25% - excellent rate), Auto loan (5-year term at 4.1% - good rate), Personal loan (3-year term at 8.9% - fair rate for unsecured). Previous loans: Student loan (paid off), Previous auto loan (paid off).",
            "student_loans": "Student loans completely paid off in June 2021. Original balance $35,000 for Computer Science degree. Paid over 8 years with accelerated payments. No current student loan debt. Payment history was perfect - never late. Helped establish early credit history.",
            "auto_loans": "Current auto loan: 2023 Honda Accord EX, $18,200 remaining balance, $385/month payment, 4.1% APR, 48 months remaining, purchased January 2023. Previous auto loan: 2018 Toyota Camry, fully paid off in December 2022, perfect payment history, helped build credit.",
            "mortgage_info": "Primary residence mortgage: $245,000 current balance, $1,650/month payment (P&I $1,200, taxes $300, insurance $150), 3.25% fixed rate, 25 years remaining, originated September 2020. Property value estimated at $320,000. LTV ratio: 76%. No late payments ever. Considering refinance for lower rate.",
            "revolving_accounts": "6 revolving accounts with $25,000 total credit limit. Current utilization 14.4% ($3,600 used). Average account age 6 years. All accounts current with no overlimit fees in past 36 months. Regular usage on all cards to maintain activity. Automatic payments set up on all accounts.",
            "installment_loans": "4 installment loans: Primary mortgage ($245,000 - excellent payment history), Auto loan ($18,200 - current), Personal loan ($18,650 - current), Previous student loan (paid off). All current loans have perfect payment history. Total monthly installment payments: $2,555.",
            "hard_inquiries": "3 hard inquiries in past 24 months: TransUnion inquiry for Honda auto loan (January 15, 2023), Experian inquiry for Chase Sapphire Reserve (August 22, 2023), Equifax inquiry for mortgage rate shopping (December 5, 2023). Average 1.5 inquiries per year - within normal range.",
            "soft_inquiries": "12 soft inquiries in past 12 months from existing creditors for account management, credit limit reviews, and pre-approved offers. Sources include Chase, Discover, Capital One, and credit monitoring services. Soft inquiries do not impact credit score.",
            "credit_score_history": "Credit score progression: 2020: 698 (good), 2021: 715 (good), 2022: 728 (excellent), 2023: 742 (excellent). Steady 44-point improvement over 4 years. Peak score: 748 (October 2023). Score factors: Payment history 35%, Utilization 30%, Length 15%, Mix 10%, Inquiries 10%.",
            "employment_status": "Full-time Software Engineer at TechCorp Inc. since March 2018 (5.5 years). Annual salary $85,000 with 3% annual increases. Stable employment with excellent performance reviews. Previous employment: Junior Developer at StartupXYZ (2015-2018). Total tech industry experience: 9 years.",
            "income_info": "Annual gross income: $85,000, Net income: $62,000 after taxes and deductions. Monthly gross: $7,083, Monthly net: $5,167. Income verified through recent pay stubs and 2023 tax returns. Additional income: $2,000/year from freelance projects. Stable income growth trajectory.",
            "notes": "Overall excellent credit profile with strong payment history and responsible credit management. Recommended for prime lending rates on all products. Minor areas for improvement: Consider paying down personal loan to improve DTI ratio below 25%. Excellent candidate for premium credit products and lowest available interest rates."
        }
    },
    "sarah.johnson@example.com": {
        "role": "client",
        "profile_id": "PROF_002", 
        "name": "Sarah Elizabeth Johnson",
        "ssn": "987-65-4321",
        "dob": date(1992, 8, 22),
        "address": "5678 Oak Avenue, Unit 12\nAustin, TX 78701",
        "phone": "(555) 987-6543",
        "employment": "Marketing Manager at Digital Solutions LLC",
        "annual_income": 72000,
        "employer_phone": "(555) 888-9999",
        "years_employed": 1.2,
        "previous_address": "321 Pine Street, Dallas, TX 75201",
        "marital_status": "Single",
        "dependents": 0,
        "housing_status": "Rent",
        "monthly_rent_mortgage": 1200,
        "bank_name": "Bank of America",
        "account_number": "****5678",
        "routing_number": "111000025",
        "credit_data": {
            "credit_score": 680,
            "credit_score_date": "2024-01-10",
            "previous_scores": "2023: 635, 2022: 650, 2021: 720",
            "score_source": "TransUnion",
            "payment_history": "Good payment history with 89% on-time payments over 7-year credit history. 8 late payments in the last 2 years, mostly 30-day lates during job transition period. Recent significant improvement with no late payments in last 6 months. Working diligently to rebuild payment consistency and credit standing.",
            "credit_utilization": "High utilization at 68% ($10,200 used of $15,000 total credit limit) - major factor negatively impacting score. Recommended to pay down balances below 30% immediately. Utilization increased significantly during 6-month unemployment period in 2022. Individual card utilization: Capital One 85%, Chase 72%, Discover 45%.",
            "inquiries": "7 hard inquiries in the last 24 months - higher than recommended frequency: 3 credit card applications (denied 2), 2 personal loan applications (1 approved), 1 auto loan inquiry (approved), 1 apartment rental credit check. Recent inquiry activity indicates credit seeking behavior.",
            "public_records": "No bankruptcies or tax liens on record. One small claims court judgment for $800 from 2021 (medical bill dispute with hospital) - currently being paid through $100/month payment plan. 4 payments remaining. No other legal or financial judgments.",
            "collections": "2 collections accounts currently active: Medical collection $450 from 2022 (in payment plan - $75/month), Utility collection $180 from previous address (paid in full last month and removed). Working with credit repair service to resolve remaining medical collection.",
            "bankruptcies": "No bankruptcy filings on record. Seriously considered Chapter 13 bankruptcy in late 2021 during unemployment but chose debt management plan instead. Currently working with non-profit credit counseling service for debt consolidation strategy.",
            "account_age": "Average account age: 4 years 8 months. Oldest account opened in January 2016 (student credit card from college - still active). Building credit history length. Newest account opened in September 2023 (personal loan). Total credit history: 8 years.",
            "open_accounts": "9 open accounts currently: 5 credit cards (Capital One Platinum $4000, Chase Freedom $3500, Discover Student $3000, Store Card Target $2000, Store Card Macy's $1500), 1 auto loan (Toyota Camry), 2 store cards, 1 personal loan (debt consolidation). Some accounts showing high balances near limits.",
            "closed_accounts": "4 closed accounts: 2 credit cards (closed by creditor due to 6+ months inactivity during unemployment), 1 store card (Nordstrom - closed by customer), 1 cell phone account (T-Mobile - paid off and closed when switching carriers).",
            "derogatory_marks": "8 derogatory marks in past 24 months: 6 late payments (30-day late), 1 late payment (60-day late on Chase card), 1 collection account (medical). Most recent late payment was 6 months ago. Significant improvement trend in recent payment behavior.",
            "total_debt": "$78,950 total debt across all accounts: Auto loan $22,500 (2021 Toyota Camry), Credit cards $10,200 (high utilization), Personal loan $8,750 (debt consolidation), Federal student loans $37,500 (4 separate loans). Current debt-to-income ratio: 44% (high - needs improvement).",
            "monthly_payments": "$1,890 total monthly debt payments: Auto loan $420 (60 months remaining), Credit cards $310 (minimum payments only), Personal loan $285 (48 months remaining), Student loans $875 (income-driven repayment plan). Payment-to-income ratio: 38% (high).",
            "high_balance": "Highest balance account: Federal student loans with $37,500 remaining balance across 4 loans. Currently enrolled in income-driven repayment plan due to previous financial hardship. Original loan amount was $45,000 for Bachelor's degree in Marketing.",
            "recent_activity": "Last 90 days positive activity: All payments made on time (6-month streak), Paid off utility collection $180 in full, Applied for debt consolidation loan (denied due to DTI ratio), Reduced total credit card balance by $500, Enrolled in credit monitoring service.",
            "account_types": "Limited credit mix diversity: Revolving credit (7 accounts - 78%), Installment loans (2 accounts - 22%). Could benefit from more diverse credit mix including mortgage or additional installment loans. Current mix weighted heavily toward revolving credit.",
            "credit_limits": "$15,000 total revolving credit limit across 7 cards: Capital One Platinum $4,000, Chase Freedom $3,500, Discover Student $3,000, Target RedCard $2,000, Macy's Card $1,500, Gas Card $1,000. Average limit per card: $2,143. Requesting limit increases on older accounts.",
            "charge_offs": "No charge-off accounts on record. All accounts remain open and active despite high balances and previous late payments. Creditors have been working with customer during financial hardship period. No accounts written off as bad debt.",
            "late_payments": "8 late payments total in past 24 months: 6 payments 30-days late (various cards), 1 payment 60-days late (Chase Freedom - $3500 balance), 1 payment 90-days late (Capital One - during unemployment in 2022). Clear improvement trend in recent 6 months.",
            "loan_types": "Current loan portfolio: Auto loan (6-year term at 6.8% - higher rate due to credit score at purchase), Personal loan (5-year term at 12.9% - high rate for debt consolidation), Federal student loans (various terms, 4.5% weighted average rate).",
            "student_loans": "Federal student loans: $37,500 current balance across 4 separate loans. Enrolled in Income-Driven Repayment plan with $875/month payments. Originally borrowed $45,000 for Bachelor's degree in Marketing from University of Texas. No private student loans.",
            "auto_loans": "Current auto loan: 2021 Toyota Camry LE, $22,500 remaining balance, $420/month payment, 6.8% APR (higher rate due to 650 credit score at time of purchase), 54 months remaining. Vehicle value approximately $18,000 - slightly underwater on loan.",
            "mortgage_info": "No mortgage currently. Renting 1-bedroom apartment in Austin, TX for $1,200/month. Saving for down payment but high DTI ratio (44%) preventing mortgage approval. Goal to purchase home within 3-5 years after debt reduction and credit improvement.",
            "revolving_accounts": "7 revolving accounts with concerning high utilization patterns. Working on aggressive debt paydown strategy with credit counselor. Several accounts near or at credit limits. Focus on paying down highest interest rate cards first (Capital One at 24.9% APR).",
            "installment_loans": "3 installment loans currently: Auto loan ($22,500 balance), Personal loan ($8,750 balance), Student loans ($37,500 balance). All payments current after recent 6-month improvement period. Total monthly installment payments: $1,580.",
            "hard_inquiries": "7 hard inquiries in past 24 months - significantly higher than recommended 2-3 per year. Recent inquiries indicate credit seeking behavior during financial stress. Recommendation: Avoid new credit applications for 12+ months to allow inquiries to age off report.",
            "soft_inquiries": "15 soft inquiries in past 12 months from credit monitoring services, existing creditors for account reviews, and pre-approved offers. Higher frequency due to active credit rebuilding efforts and monitoring services. Soft inquiries do not impact credit score.",
            "credit_score_history": "Credit score volatility: 2020: 720 (excellent), 2021: 650 (job loss impact), 2022: 635 (unemployment low point), 2023: 680 (recovery in progress). 40-point recovery from low point. Goal: Return to 720+ within 18 months through debt reduction.",
            "employment_status": "Full-time Marketing Manager at Digital Solutions LLC since January 2023 (current role 12 months). Previous 6-month unemployment period (July 2021 - January 2022) significantly impacted credit. Income stabilizing with new position and career growth potential.",
            "income_info": "Current annual income: $72,000 gross, $52,000 net after taxes and deductions. Monthly gross: $6,000, Monthly net: $4,333. Income increased 20% with new Marketing Manager position. Building emergency fund to prevent future credit issues. Previous income: $60,000.",
            "notes": "Credit rebuilding actively in progress with professional guidance. Primary concerns: High utilization (68%) and recent late payment history. Positive trends: 6-month perfect payment streak, reduced debt balances, stable employment. Recommendations: Focus on utilization reduction below 30%, continue perfect payment history, avoid new credit applications."
        }
    },
    "admin@creditreports.com": {
        "role": "admin",
        "profile_id": "PROF_003",
        "name": "Michael Robert Chen",
        "ssn": "456-78-9123", 
        "dob": date(1978, 11, 8),
        "address": "9999 Executive Blvd, Suite 200\nRockville, MD 20852",
        "phone": "(555) 456-7890",
        "employment": "Senior Credit Analyst at Credit Solutions Corp",
        "annual_income": 125000,
        "employer_phone": "(555) 777-8888",
        "years_employed": 15.5,
        "previous_address": "1111 Corporate Drive, Bethesda, MD 20814",
        "marital_status": "Married",
        "dependents": 3,
        "housing_status": "Own",
        "monthly_rent_mortgage": 2400,
        "bank_name": "Wells Fargo Private Bank",
        "account_number": "****9999",
        "routing_number": "121000248",
        "credit_data": {
            "credit_score": 820,
            "credit_score_date": "2024-01-20",
            "previous_scores": "2023: 822, 2022: 818, 2021: 815",
            "score_source": "FICO Score 8 (Equifax)",
            "payment_history": "Exceptional payment history with 100% on-time payments over 25+ years of credit history. Never missed a single payment across all accounts throughout entire credit lifetime. Exemplary payment discipline and financial management serving as model for credit excellence.",
            "credit_utilization": "Optimal utilization at 3% ($1,200 used of $40,000 total credit limit). Maintains consistently low utilization through strategic balance management, high credit limits, and disciplined spending. Never exceeded 10% utilization in past 10 years. Individual card utilization all below 5%.",
            "inquiries": "1 hard inquiry in the last 24 months: Mortgage refinance inquiry (March 15, 2023 - Equifax). Minimal inquiry activity demonstrates established credit profile with no need for new credit seeking. Previous inquiry was 18 months prior for investment property.",
            "public_records": "Completely clean public record with no bankruptcies, liens, tax liens, judgments, foreclosures, or any legal financial issues throughout entire adult life. Exemplary legal and financial standing with no government or court involvement in financial matters.",
            "collections": "No collections accounts ever reported in 25+ year credit history. No history of any accounts sent to collections agencies. Perfect account management with all creditors throughout economic cycles and market downturns.",
            "bankruptcies": "No bankruptcy filings of any type throughout entire financial history. No Chapter 7, Chapter 11, or Chapter 13 proceedings ever considered or filed. Strong financial management and emergency planning prevented need for bankruptcy protection even during 2008 financial crisis.",
            "account_age": "Average account age: 12 years 8 months. Oldest account opened in March 1995 (first credit card during college - still active after 29 years). Newest account opened in March 2023 (business credit card). Exceptional credit history length demonstrating long-term financial responsibility.",
            "open_accounts": "15 open accounts in perfect standing: 8 personal credit cards (Amex Platinum $15,000, Chase Sapphire Reserve $12,000, Citi Double Cash $8,000, Discover It $5,000, Capital One Venture $6,000, Bank of America Premium $7,000, Wells Fargo Propel $4,000, US Bank Altitude $3,000), 1 primary mortgage, 2 investment property mortgages, 2 business credit cards (Chase Ink $10,000, Amex Business Gold $8,000), 1 HELOC ($50,000 limit), 1 auto loan. All accounts managed with automatic payments and perfect payment history.",
            "closed_accounts": "12 closed accounts all in excellent standing: All accounts closed voluntarily by customer for account consolidation or better terms. Includes 5 paid-off auto loans, 3 paid-off personal loans, 2 closed credit cards (upgraded to better products), 1 paid-off student loan, 1 closed business line of credit. No accounts ever closed by creditors.",
            "derogatory_marks": "Zero derogatory marks on credit report throughout entire 25+ year credit history. Perfect payment and account management record with no late payments, overlimit fees, returned payments, or any negative reporting from any creditor ever.",
            "total_debt": "$625,000 total strategic debt: Primary residence mortgage $380,000 (2.75% APR), Investment property 1 mortgage $180,000 (3.1% APR), Investment property 2 mortgage $145,000 (3.25% APR), HELOC $25,000 (4.25% variable), Auto loan $15,000 (2.9% APR), Credit cards $1,200 (paid in full monthly), Business cards $3,800 (paid in full monthly). All debt strategically managed for tax advantages and wealth building.",
            "monthly_payments": "$4,200 total monthly debt payments: Primary mortgage $2,400 (P&I, taxes, insurance), Investment property 1 $1,100, Investment property 2 $950, HELOC $300 (interest only), Auto loan $450, Credit cards paid in full monthly (typically $2,000-3,000). Excellent payment capacity with 34% payment-to-income ratio.",
            "high_balance": "Highest balance account: Primary residence mortgage with $380,000 remaining balance. Original loan amount $420,000 refinanced in March 2023 from 3.75% to 2.75%. Property current value $650,000. Loan-to-value ratio: 58%. Considering additional principal payments for early payoff.",
            "recent_activity": "Last 90 days exemplary activity: All payments made on time and in full, Refinanced primary mortgage saving $400/month, Increased credit limit on Amex Platinum to $20,000 (requested and approved), Paid off all business expenses in full, Opened new high-yield savings account, Made additional $5,000 principal payment on primary mortgage.",
            "account_types": "Excellent and diverse credit mix: Revolving credit (10 accounts - 40%), Installment loans (3 accounts - 12%), Mortgages (3 accounts - 12%), HELOC (1 account - 4%), Business credit (2 accounts - 8%). Optimal diversity across all major credit categories demonstrating sophisticated financial management.",
            "credit_limits": "$65,000 total revolving credit limit across 10 cards: Amex Platinum $20,000, Chase Sapphire Reserve $12,000, Citi Double Cash $8,000, Bank of America Premium $7,000, Capital One Venture $6,000, Discover It $5,000, Wells Fargo Propel $4,000, US Bank Altitude $3,000, Chase Ink Business $10,000, Amex Business Gold $8,000. Average limit per card: $6,500.",
            "charge_offs": "No charge-off accounts in entire credit history spanning 25+ years. All accounts maintained in excellent standing even during economic downturns including 2001 dot-com crash, 2008 financial crisis, and 2020 pandemic. Perfect account management record.",
            "late_payments": "Zero late payments in entire 25+ year credit history across all account types. Perfect payment record maintained through automatic payments, calendar reminders, and disciplined financial management. Never incurred late fees or penalty interest rates on any account.",
            "loan_types": "Sophisticated loan portfolio: Primary residence conventional mortgage (30-year fixed at 2.75% - excellent rate), Investment property mortgages (30-year fixed at 3.1% and 3.25%), HELOC (variable rate at prime + 0.25%), Auto loan (3-year term at 2.9% - premium rate). All loans at best available rates due to excellent credit.",
            "student_loans": "Student loans completely paid off in December 2005. Original MBA loan balance $28,000 from Wharton Business School. Paid off 2 years early with no late payments throughout 5-year repayment period. Early payoff saved $3,200 in interest. Helped establish excellent early credit history.",
            "auto_loans": "Current auto loan: 2023 BMW X5 xDrive40i, $15,000 remaining balance, $450/month payment, 2.9% APR (premium rate due to excellent credit), 33 months remaining, purchased March 2023. Previous auto loans: 5 vehicles all paid off early with perfect payment history, rates ranging from 1.9% to 3.5%.",
            "mortgage_info": "Primary residence: $380,000 current balance, $2,400/month payment (P&I $1,800, taxes $400, insurance $200), 2.75% fixed rate (refinanced March 2023), 27 years remaining. Property value $650,000, LTV: 58%. Investment properties: Property 1 ($180,000 balance, $1,100/month), Property 2 ($145,000 balance, $950/month). Total real estate value: $1.2M.",
            "revolving_accounts": "10 revolving accounts with $65,000 total credit limit. Current utilization 1.8% ($1,200 used). Average account age 9 years. All accounts current with no overlimit fees in past 60 months. Regular usage on all cards to maintain activity. Automatic payments set up on all accounts.",
            "installment_loans": "5 installment loans: Primary mortgage ($380,000 - excellent payment history), Investment property 1 ($180,000 - current), Investment property 2 ($145,000 - current), Auto loan ($15,000 - current), HELOC ($25,000 - current). All current loans have perfect payment history. Total monthly installment payments: $5,250.",
            "hard_inquiries": "1 hard inquiry in past 24 months: Equifax inquiry for mortgage refinance (March 15, 2023). Minimal inquiry activity demonstrates established credit profile with no need for new credit seeking. Previous inquiry was 18 months prior for investment property.",
            "soft_inquiries": "8 soft inquiries in past 12 months from credit monitoring services and existing creditors for account reviews and pre-approved offers. Sources include Amex, Chase, Citi, and Wells Fargo. Soft inquiries do not impact credit score.",
            "credit_score_history": "Credit score stability: 2020: 815, 2021: 818, 2022: 822, 2023: 820. Consistently maintains excellent credit score above 800. Peak score: 825 (January 2023). Score factors: Payment history 35%, Utilization 30%, Length 15%, Mix 10%, Inquiries 10%.",
            "employment_status": "Full-time Senior Credit Analyst at Credit Solutions Corp since July 2008 (15.5 years). Highly stable employment with consistent promotions and salary increases. Previous employment: Credit Analyst at Regional Bank (2005-2008). Total credit industry experience: 18 years.",
            "income_info": "Annual gross income: $125,000, Net income: $90,000 after taxes and deductions. Monthly gross: $10,417, Monthly net: $7,500. Income verified through recent pay stubs and 2023 tax returns. Additional income: $15,000/year from rental properties. Strong and diversified income streams.",
            "notes": "Exceptional credit profile with perfect payment history, very low utilization, and extensive credit history. Demonstrates sophisticated financial management and responsible use of credit. Qualifies for best rates and terms on all financial products. No areas for improvement identified. Model credit consumer."
        }
    }
}

# --- Utility Functions ---

def generate_pdf_report(profile_data, output_filename="credit_report.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Credit Report", 0, 1, "C")
    pdf.ln(10)

    pdf.set_font("Arial", "", 12)
    for key, value in profile_data.items():
        if isinstance(value, dict):
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, f"{key.replace('_', ' ').title()}:", 0, 1, "L")
            pdf.set_font("Arial", "", 12)
            for sub_key, sub_value in value.items():
                pdf.multi_cell(0, 7, f"  {sub_key.replace('_', ' ').title()}: {sub_value}")
        else:
            pdf.multi_cell(0, 7, f"{key.replace('_', ' ').title()}: {value}")
    
    pdf_output = pdf.output(dest='S').encode('latin1')
    return pdf_output

def get_google_credentials():
    # Placeholder for fetching Google service account credentials securely
    # In a real application, this would involve environment variables or Streamlit secrets
    # For demo purposes, we'll assume a 'google_credentials.json' file exists
    try:
        with open("google_credentials.json", "r") as f:
            info = json.load(f)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        return creds
    except FileNotFoundError:
        st.error("Google credentials file 'google_credentials.json' not found.")
        st.info("Please ensure your Google service account credentials are in 'google_credentials.json' in the root directory.")
        return None

def upload_to_drive(file_path, file_name, mime_type):
    creds = get_google_credentials()
    if not creds:
        return None

    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': file_name}
        media = MediaFileUpload(file_path, mimetype=mime_type)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        st.success(f"File '{file_name}' uploaded to Google Drive with ID: {file.get('id')}")
        return file.get('id')
    except Exception as e:
        st.error(f"Error uploading to Google Drive: {e}")
        return None

def download_from_drive(file_id, file_name):
    creds = get_google_credentials()
    if not creds:
        return None

    try:
        service = build('drive', 'v3', credentials=creds)
        request = service.files().get_media(fileId=file_id)
        fh = BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            st.write(f"Download progress: {int(status.progress() * 100)}%.")
        
        fh.seek(0)
        with open(file_name, 'wb') as f:
            f.write(fh.read())
        st.success(f"File '{file_name}' downloaded from Google Drive.")
        return file_name
    except Exception as e:
        st.error(f"Error downloading from Google Drive: {e}")
        return None

def get_sheet_data(spreadsheet_id, range_name):
    creds = get_google_credentials()
    if not creds:
        return None
    try:
        service = build('sheets', 'v4', credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        rows = result.get('values', [])
        return rows
    except Exception as e:
        st.error(f"Error reading Google Sheet: {e}")
        return None

def update_sheet_data(spreadsheet_id, range_name, values):
    creds = get_google_credentials()
    if not creds:
        return None
    try:
        service = build('sheets', 'v4', credentials=creds)
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name, valueInputOption='RAW',
            body=body).execute()
        st.success(f"Google Sheet updated: {result.get('updatedCells')} cells.")
        return True
    except Exception as e:
        st.error(f"Error updating Google Sheet: {e}")
        return False

# --- Session State Management ---

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'current_user_email' not in st.session_state:
    st.session_state['current_user_email'] = None
if 'current_profile_data' not in st.session_state:
    st.session_state['current_profile_data'] = None

# --- Authentication ---

def authenticate_user(email, password):
    # In a real app, integrate with a secure authentication backend (e.g., OAuth, Firebase Auth)
    # For this demo, we use hardcoded demo profiles.
    if email in DEMO_PROFILES and password == "password":  # Simple password for demo
        st.session_state['logged_in'] = True
        st.session_state['user_role'] = DEMO_PROFILES[email]['role']
        st.session_state['current_user_email'] = email
        st.session_state['current_profile_data'] = DEMO_PROFILES[email]
        return True
    return False

def logout_user():
    st.session_state['logged_in'] = False
    st.session_state['user_role'] = None
    st.session_state['current_user_email'] = None
    st.session_state['current_profile_data'] = None
    st.experimental_rerun()

# --- UI Components ---

def display_login_page():
    st.title("Login to Advanced Credit Report System")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Login"):
                if authenticate_user(email, password):
                    st.success(f"Logged in as {st.session_state['user_role']}")
                    st.experimental_rerun()
                else:
                    st.error("Invalid email or password")
        with col2:
            st.markdown("""
            **Demo Accounts:**
            - Client: `john.doe@example.com` / `password`
            - Client: `sarah.johnson@example.com` / `password`
            - Admin: `admin@creditreports.com` / `password`
            """)

def display_sidebar():
    st.sidebar.image("https://www.credit.org/wp-content/uploads/2021/04/credit-org-logo.png", use_column_width=True)
    st.sidebar.title(f"Welcome, {st.session_state['current_profile_data']['name'].split(' ')[0]}!")
    st.sidebar.write(f"Role: {st.session_state['user_role'].title()}")
    
    if st.session_state['user_role'] == 'admin':
        st.sidebar.header("Admin Actions")
        selected_client_email = st.sidebar.selectbox(
            "Select Client Profile", 
            [email for email, data in DEMO_PROFILES.items() if data['role'] == 'client']
        )
        if selected_client_email:
            st.session_state['current_profile_data'] = DEMO_PROFILES[selected_client_email]
            st.session_state['current_user_email'] = selected_client_email
            st.sidebar.write(f"Viewing {st.session_state['current_profile_data']['name']}'s profile.")

    st.sidebar.markdown("--- ")
    if st.sidebar.button("Logout"):
        logout_user()

def display_credit_report_tab():
    st.header("Comprehensive Credit Report")
    profile = st.session_state['current_profile_data']
    credit_data = profile.get('credit_data', {})

    st.subheader(f"Client: {profile['name']} (ID: {profile['profile_id']})")
    st.markdown(f"**SSN:** {profile['ssn']} | **DOB:** {profile['dob']} | **Phone:** {profile['phone']}")
    st.markdown(f"**Address:** {profile['address'].replace('\n', ', ')}")
    st.markdown(f"**Employment:** {profile['employment']} | **Annual Income:** ${profile['annual_income']:,}")
    st.markdown(f"**Credit Score:** {credit_data.get('credit_score', 'N/A')} (as of {credit_data.get('credit_score_date', 'N/A')}) from {credit_data.get('score_source', 'N/A')}")

    st.markdown("--- ")
    st.subheader("Detailed Credit Information")

    # Display credit data in an organized manner
    sections = [
        "payment_history", "credit_utilization", "inquiries", "public_records",
        "collections", "bankruptcies", "account_age", "open_accounts",
        "closed_accounts", "derogatory_marks", "total_debt", "monthly_payments",
        "high_balance", "recent_activity", "account_types", "credit_limits",
        "charge_offs", "late_payments", "loan_types", "student_loans",
        "auto_loans", "mortgage_info", "revolving_accounts", "installment_loans",
        "hard_inquiries", "soft_inquiries", "credit_score_history",
        "employment_status", "income_info", "notes"
    ]

    for section in sections:
        if credit_data.get(section):
            with st.expander(f"**{section.replace('_', ' ').title()}**"):
                st.write(credit_data[section])

    st.markdown("--- ")
    st.subheader("Report Actions")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Generate PDF Report"):
            pdf_output = generate_pdf_report(profile)
            st.download_button(
                label="Download PDF Report",
                data=pdf_output,
                file_name=f"credit_report_{profile['profile_id']}.pdf",
                mime="application/pdf"
            )
    with col2:
        if st.button("Export Profile to CSV"):
            # Flatten the profile data for CSV export
            flat_profile = {}
            for k, v in profile.items():
                if isinstance(v, dict):
                    for sub_k, sub_v in v.items():
                        flat_profile[f"{k}_{sub_k}"] = sub_v
                else:
                    flat_profile[k] = v
            
            df = pd.DataFrame([flat_profile])
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download CSV Profile",
                data=csv_buffer.getvalue(),
                file_name=f"profile_{profile['profile_id']}.csv",
                mime="text/csv"
            )
    with col3:
        # Google Drive Upload/Download
        st.subheader("Google Drive Integration")
        uploaded_file_drive = st.file_uploader("Upload to Drive", type=["pdf", "csv"], key="drive_upload")
        if uploaded_file_drive is not None:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file_drive.getvalue())
                temp_path = tmp_file.name
            
            file_name_to_upload = uploaded_file_drive.name
            mime_type_to_upload = uploaded_file_drive.type
            
            if st.button(f"Upload {file_name_to_upload} to Drive"):
                upload_to_drive(temp_path, file_name_to_upload, mime_type_to_upload)
                os.unlink(temp_path) # Clean up temp file

        drive_file_id = st.text_input("Enter Drive File ID to Download")
        drive_file_name = st.text_input("Enter Desired Download File Name")
        if st.button("Download from Drive"):
            if drive_file_id and drive_file_name:
                downloaded_file_path = download_from_drive(drive_file_id, drive_file_name)
                if downloaded_file_path:
                    with open(downloaded_file_path, "rb") as f:
                        st.download_button(
                            label=f"Download {drive_file_name}",
                            data=f.read(),
                            file_name=drive_file_name,
                            mime="application/octet-stream"
                        )
                    os.unlink(downloaded_file_path) # Clean up temp file
            else:
                st.error("Please provide both File ID and desired File Name for download.")

def display_letter_sending_tracking_tab():
    st.header("📮 Letter Sending Tracking System")
    st.write("Comprehensive tracking system for all letters sent to clients with advanced filtering and reporting capabilities.")

    # Define columns for the tracking table
    tracking_columns = [
        "Letter ID", "Client ID", "Client Name", "Letter Type", 
        "Date Sent", "Delivery Status", "Tracking Number", "Carrier", 
        "Expected Delivery", "Actual Delivery", "Cost", "Priority", 
        "Response Required", "Response Received", "Follow-up Date", "Notes"
    ]

    # Initialize session state for tracking data if not present
    if 'letter_tracking_data' not in st.session_state:
        # Create sample data for demonstration
        sample_data = pd.DataFrame([
            {
                "Letter ID": "L0001",
                "Client ID": "PROF_001",
                "Client Name": "John Michael Doe",
                "Letter Type": "Dispute Letter",
                "Date Sent": date(2024, 1, 15),
                "Delivery Status": "Delivered",
                "Tracking Number": "1Z999AA1234567890",
                "Carrier": "UPS",
                "Expected Delivery": date(2024, 1, 17),
                "Actual Delivery": date(2024, 1, 17),
                "Cost": 12.50,
                "Priority": "High",
                "Response Required": "Yes",
                "Response Received": "No",
                "Follow-up Date": date(2024, 2, 15),
                "Notes": "Dispute letter for Experian credit report errors"
            },
            {
                "Letter ID": "L0002",
                "Client ID": "PROF_002",
                "Client Name": "Sarah Elizabeth Johnson",
                "Letter Type": "Validation Letter",
                "Date Sent": date(2024, 1, 20),
                "Delivery Status": "Pending",
                "Tracking Number": "9405511206213123456789",
                "Carrier": "USPS",
                "Expected Delivery": date(2024, 1, 22),
                "Actual Delivery": None,
                "Cost": 8.75,
                "Priority": "Medium",
                "Response Required": "Yes",
                "Response Received": "No",
                "Follow-up Date": date(2024, 2, 20),
                "Notes": "Debt validation request for medical collection"
            }
        ])
        st.session_state['letter_tracking_data'] = sample_data

    # Search and Filter Section
    st.subheader("🔍 Search & Filter")
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        search_client = st.text_input("Search by Client Name", placeholder="Enter client name...")
        filter_status = st.multiselect("Filter by Status", 
                                     ["Sent", "Delivered", "Returned", "Pending", "Failed"],
                                     default=[])
    
    with col_filter2:
        filter_type = st.multiselect("Filter by Letter Type", 
                                   ["Dispute Letter", "Validation Letter", "Goodwill Letter", "Settlement Offer", "Other"],
                                   default=[])
        filter_priority = st.multiselect("Filter by Priority", 
                                       ["High", "Medium", "Low"],
                                       default=[])
    
    with col_filter3:
        date_from = st.date_input("Date From", value=None)
        date_to = st.date_input("Date To", value=None)

    # Apply filters
    filtered_data = st.session_state['letter_tracking_data'].copy()
    
    if search_client:
        filtered_data = filtered_data[filtered_data['Client Name'].str.contains(search_client, case=False, na=False)]
    
    if filter_status:
        filtered_data = filtered_data[filtered_data['Delivery Status'].isin(filter_status)]
    
    if filter_type:
        filtered_data = filtered_data[filtered_data['Letter Type'].isin(filter_type)]
    
    if filter_priority:
        filtered_data = filtered_data[filtered_data['Priority'].isin(filter_priority)]
    
    if date_from:
        filtered_data = filtered_data[pd.to_datetime(filtered_data['Date Sent']) >= pd.to_datetime(date_from)]
    
    if date_to:
        filtered_data = filtered_data[pd.to_datetime(filtered_data['Date Sent']) <= pd.to_datetime(date_to)]

    st.subheader("➕ Add New Letter Entry")
    with st.form("new_letter_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            letter_id = st.text_input("Letter ID", value=f"L{len(st.session_state['letter_tracking_data']) + 1:04d}")
            client_id = st.selectbox("Client ID", 
                                   options=[""] + [f"{data['profile_id']} - {data['name']}" for email, data in DEMO_PROFILES.items() if data['role'] == 'client'],
                                   index=0)
            letter_type = st.selectbox("Letter Type", ["Dispute Letter", "Validation Letter", "Goodwill Letter", "Settlement Offer", "Other"])
            priority = st.selectbox("Priority", ["High", "Medium", "Low"], index=1)
        
        with col2:
            client_name = st.text_input("Client Name")
            date_sent = st.date_input("Date Sent", value=datetime.now().date())
            delivery_status = st.selectbox("Delivery Status", ["Sent", "Delivered", "Returned", "Pending", "Failed"])
            carrier = st.selectbox("Carrier", ["USPS", "UPS", "FedEx", "DHL", "Other"])
        
        with col3:
            tracking_number = st.text_input("Tracking Number")
            expected_delivery = st.date_input("Expected Delivery", value=datetime.now().date() + timedelta(days=3))
            actual_delivery = st.date_input("Actual Delivery", value=None)
            cost = st.number_input("Shipping Cost ($)", min_value=0.0, value=0.0, step=0.01)
        
        with col4:
            response_required = st.selectbox("Response Required", ["Yes", "No"])
            response_received = st.selectbox("Response Received", ["Yes", "No", "Partial"])
            follow_up_date = st.date_input("Follow-up Date", value=datetime.now().date() + timedelta(days=30))
            notes = st.text_area("Notes", height=100)
        
        if st.form_submit_button("Add Letter Entry"):
            new_entry = pd.DataFrame([{
                "Letter ID": letter_id,
                "Client ID": client_id.split(" - ")[0] if client_id else "",
                "Client Name": client_name,
                "Letter Type": letter_type,
                "Date Sent": date_sent,
                "Delivery Status": delivery_status,
                "Tracking Number": tracking_number,
                "Carrier": carrier,
                "Expected Delivery": expected_delivery,
                "Actual Delivery": actual_delivery if actual_delivery != datetime.now().date() else None,
                "Cost": cost,
                "Priority": priority,
                "Response Required": response_required,
                "Response Received": response_received,
                "Follow-up Date": follow_up_date,
                "Notes": notes
            }])
            st.session_state['letter_tracking_data'] = pd.concat([st.session_state['letter_tracking_data'], new_entry], ignore_index=True)
            st.success("Letter entry added successfully!")
            st.experimental_rerun()

    # Statistics Dashboard
    st.subheader("📊 Tracking Statistics")
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    
    total_letters = len(st.session_state['letter_tracking_data'])
    delivered_letters = len(st.session_state['letter_tracking_data'][st.session_state['letter_tracking_data']['Delivery Status'] == 'Delivered'])
    pending_letters = len(st.session_state['letter_tracking_data'][st.session_state['letter_tracking_data']['Delivery Status'] == 'Pending'])
    total_cost = st.session_state['letter_tracking_data']['Cost'].sum()
    
    with col_stat1:
        st.metric("Total Letters", total_letters)
    with col_stat2:
        st.metric("Delivered", delivered_letters, f"{(delivered_letters/total_letters*100):.1f}%" if total_letters > 0 else "0%")
    with col_stat3:
        st.metric("Pending", pending_letters)
    with col_stat4:
        st.metric("Total Cost", f"${total_cost:.2f}")

    st.subheader("📋 Current Letter Tracking Data")
    
    # Edit functionality
    if not filtered_data.empty:
        st.write(f"Showing {len(filtered_data)} of {len(st.session_state['letter_tracking_data'])} letters")
        
        # Display editable dataframe
        edited_df = st.data_editor(
            filtered_data,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "Date Sent": st.column_config.DateColumn("Date Sent"),
                "Expected Delivery": st.column_config.DateColumn("Expected Delivery"),
                "Actual Delivery": st.column_config.DateColumn("Actual Delivery"),
                "Follow-up Date": st.column_config.DateColumn("Follow-up Date"),
                "Cost": st.column_config.NumberColumn("Cost ($)", format="$%.2f"),
                "Delivery Status": st.column_config.SelectboxColumn(
                    "Delivery Status",
                    options=["Sent", "Delivered", "Returned", "Pending", "Failed"]
                ),
                "Priority": st.column_config.SelectboxColumn(
                    "Priority",
                    options=["High", "Medium", "Low"]
                ),
                "Response Required": st.column_config.SelectboxColumn(
                    "Response Required",
                    options=["Yes", "No"]
                ),
                "Response Received": st.column_config.SelectboxColumn(
                    "Response Received",
                    options=["Yes", "No", "Partial"]
                )
            }
        )
        
        # Update session state with edited data
        if st.button("Save Changes"):
            # Update the original dataframe with edited values
            for index, row in edited_df.iterrows():
                original_index = st.session_state['letter_tracking_data'][
                    st.session_state['letter_tracking_data']['Letter ID'] == row['Letter ID']
                ].index
                if not original_index.empty:
                    st.session_state['letter_tracking_data'].loc[original_index[0]] = row
            st.success("Changes saved successfully!")
            st.experimental_rerun()
    else:
        st.info("No letters match the current filter criteria.")

    st.subheader("📥📤 Import/Export Letter Tracking Data")
    col_imp_exp1, col_imp_exp2, col_imp_exp3 = st.columns(3)
    
    with col_imp_exp1:
        st.write("**Import Data**")
        uploaded_file = st.file_uploader("Import CSV File", type=["csv"], key="letter_import")
        if uploaded_file is not None:
            try:
                imported_df = pd.read_csv(uploaded_file)
                
                # Show preview of imported data
                st.write("Preview of imported data:")
                st.dataframe(imported_df.head())
                
                # Validate columns
                missing_cols = [col for col in tracking_columns if col not in imported_df.columns]
                if missing_cols:
                    st.warning(f"Missing columns: {', '.join(missing_cols)}")
                    st.info("The system will add missing columns with default values.")
                    
                    # Add missing columns with default values
                    for col in missing_cols:
                        if 'Date' in col:
                            imported_df[col] = None
                        elif col == 'Cost':
                            imported_df[col] = 0.0
                        else:
                            imported_df[col] = ""
                
                if st.button("Confirm Import"):
                    st.session_state['letter_tracking_data'] = pd.concat([st.session_state['letter_tracking_data'], imported_df], ignore_index=True)
                    st.success(f"Successfully imported {len(imported_df)} records!")
                    st.experimental_rerun()
                    
            except Exception as e:
                st.error(f"Error importing CSV: {e}")
    
    with col_imp_exp2:
        st.write("**Export Data**")
        export_format = st.selectbox("Export Format", ["CSV", "Excel"])
        
        if st.button("Export All Data"):
            if export_format == "CSV":
                csv_buffer = StringIO()
                st.session_state['letter_tracking_data'].to_csv(csv_buffer, index=False)
                st.download_button(
                    label="Download Full Tracking CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"letter_tracking_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:  # Excel
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    st.session_state['letter_tracking_data'].to_excel(writer, sheet_name='Letter Tracking', index=False)
                    
                    # Add summary sheet
                    summary_data = {
                        'Metric': ['Total Letters', 'Delivered', 'Pending', 'Failed', 'Total Cost'],
                        'Value': [
                            total_letters,
                            delivered_letters,
                            pending_letters,
                            len(st.session_state['letter_tracking_data'][st.session_state['letter_tracking_data']['Delivery Status'] == 'Failed']),
                            f"${total_cost:.2f}"
                        ]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                st.download_button(
                    label="Download Full Tracking Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"letter_tracking_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        if st.button("Export Filtered Data"):
            if export_format == "CSV":
                csv_buffer = StringIO()
                filtered_data.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="Download Filtered CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"letter_tracking_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:  # Excel
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    filtered_data.to_excel(writer, sheet_name='Filtered Data', index=False)
                
                st.download_button(
                    label="Download Filtered Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"letter_tracking_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    with col_imp_exp3:
        st.write("**Template & Backup**")
        
        if st.button("Download CSV Template"):
            template_df = pd.DataFrame(columns=tracking_columns)
            csv_buffer = StringIO()
            template_df.to_csv(csv_buffer, index=False)
            st.download_button(
                label="Download Template CSV",
                data=csv_buffer.getvalue(),
                file_name="letter_tracking_template.csv",
                mime="text/csv"
            )
        
        if st.button("Create Backup"):
            backup_data = {
                'backup_date': datetime.now().isoformat(),
                'total_records': len(st.session_state['letter_tracking_data']),
                'data': st.session_state['letter_tracking_data'].to_dict('records')
            }
            
            backup_json = json.dumps(backup_data, indent=2, default=str)
            st.download_button(
                label="Download Backup JSON",
                data=backup_json,
                file_name=f"letter_tracking_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

    # Bulk Operations
    st.subheader("🔧 Bulk Operations")
    col_bulk1, col_bulk2 = st.columns(2)
    
    with col_bulk1:
        st.write("**Update Multiple Records**")
        bulk_status = st.selectbox("Set Status for Selected Letters", 
                                 ["", "Sent", "Delivered", "Returned", "Pending", "Failed"])
        selected_letters = st.multiselect("Select Letters to Update", 
                                        options=st.session_state['letter_tracking_data']['Letter ID'].tolist())
        
        if st.button("Apply Bulk Status Update") and bulk_status and selected_letters:
            for letter_id in selected_letters:
                mask = st.session_state['letter_tracking_data']['Letter ID'] == letter_id
                st.session_state['letter_tracking_data'].loc[mask, 'Delivery Status'] = bulk_status
            st.success(f"Updated {len(selected_letters)} letters to status: {bulk_status}")
            st.experimental_rerun()
    
    with col_bulk2:
        st.write("**Delete Records**")
        delete_letters = st.multiselect("Select Letters to Delete", 
                                      options=st.session_state['letter_tracking_data']['Letter ID'].tolist(),
                                      key="delete_selection")
        
        if st.button("Delete Selected Letters", type="secondary") and delete_letters:
            if st.checkbox("I confirm I want to delete these records"):
                st.session_state['letter_tracking_data'] = st.session_state['letter_tracking_data'][
                    ~st.session_state['letter_tracking_data']['Letter ID'].isin(delete_letters)
                ]
                st.success(f"Deleted {len(delete_letters)} letters")
                st.experimental_rerun()
            else:
                st.warning("Please confirm deletion by checking the checkbox above.")

def display_onboarding_forms_tab():
    st.header("🚀 Onboarding & Workflow Automation (n8n Integration)")
    st.write("This section provides interactive forms to streamline client onboarding and document collection processes, leveraging n8n webhooks for automation.")

    st.subheader("📝 Client Onboarding Form")
    st.info("Use this form to collect initial client information. Submitting this form will trigger an automated onboarding workflow via n8n, which can include CRM updates, welcome emails, and task assignments.")
    
    # Make webhook URL configurable and persistent
    if 'n8n_webhook_url_client' not in st.session_state:
        st.session_state.n8n_webhook_url_client = "https://your-n8n-instance.com/webhook/client-onboarding"
    n8n_webhook_url_client = st.text_input("n8n Webhook URL for Client Onboarding", st.session_state.n8n_webhook_url_client, key="client_webhook_url")
    st.session_state.n8n_webhook_url_client = n8n_webhook_url_client

    with st.form("client_onboarding_form"):
        st.write("**Please fill out the client details for onboarding:**")
        col_onboard1, col_onboard2 = st.columns(2)
        with col_onboard1:
            client_onboard_name = st.text_input("Full Name", help="Client's full legal name.")
            client_onboard_email = st.text_input("Email Address", help="Client's primary email for communication.")
            client_onboard_phone = st.text_input("Phone Number", help="Client's primary contact number.")
            client_onboard_dob = st.date_input("Date of Birth", help="Client's date of birth.")
        with col_onboard2:
            client_onboard_address = st.text_area("Full Address (Street, City, State, Zip)", height=100, help="Client's current residential address.")
            client_onboard_ssn = st.text_input("Last 4 Digits of SSN (Optional)", max_chars=4, help="For identification purposes, if required.")
            client_onboard_notes = st.text_area("Additional Onboarding Notes (Optional)", height=50, help="Any specific instructions or details for this client.")
        
        client_onboard_consent = st.checkbox("I confirm that the client has provided consent for their data to be processed for onboarding purposes and shared with necessary automation tools (e.g., n8n).", value=False)

        submit_onboard_form = st.form_submit_button("Submit Client Onboarding Form")
        if submit_onboard_form:
            if not client_onboard_consent:
                st.error("Please obtain and confirm client consent before submitting.")
            elif not all([client_onboard_name, client_onboard_email, client_onboard_phone, client_onboard_dob, client_onboard_address]):
                st.error("Please fill in all required fields (Name, Email, Phone, DOB, Address).")
            else:
                payload = {
                    "name": client_onboard_name,
                    "email": client_onboard_email,
                    "phone": client_onboard_phone,
                    "dob": str(client_onboard_dob),
                    "address": client_onboard_address,
                    "ssn_last_4": client_onboard_ssn,
                    "notes": client_onboard_notes,
                    "timestamp": datetime.now().isoformat()
                }
                try:
                    with st.spinner("Sending data to n8n webhook..."):
                        response = requests.post(n8n_webhook_url_client, json=payload, timeout=10)
                    
                    if response.status_code == 200 or response.status_code == 201:
                        st.success("Client onboarding form submitted successfully to n8n webhook!")
                        st.json(response.json()) # Display n8n response for debugging/confirmation
                    else:
                        st.error(f"Failed to submit form. Status code: {response.status_code}. Response: {response.text}")
                        st.warning("Please check the n8n webhook URL and your n8n workflow configuration.")
                except requests.exceptions.Timeout:
                    st.error("The request to n8n webhook timed out. Please check your n8n instance and network connection.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Network error or invalid webhook URL: {e}")
                    st.warning("Ensure the n8n webhook URL is correct and accessible.")

    st.markdown("--- ")
    st.subheader("📄 Document Request Form")
    st.info("Use this form to request specific documents from clients. Submitting this will trigger a document collection workflow via n8n, which can send automated reminders, create secure upload links, or update document tracking systems.")
    
    # Make webhook URL configurable and persistent
    if 'n8n_webhook_url_docs' not in st.session_state:
        st.session_state.n8n_webhook_url_docs = "https://your-n8n-instance.com/webhook/document-request"
    n8n_webhook_url_docs = st.text_input("n8n Webhook URL for Document Request", st.session_state.n8n_webhook_url_docs, key="docs_webhook_url")
    st.session_state.n8n_webhook_url_docs = n8n_webhook_url_docs

    with st.form("document_request_form"):
        st.write("**Request documents from a client:**")
        col_docreq1, col_docreq2 = st.columns(2)
        with col_docreq1:
            doc_req_client_id = st.text_input("Client ID for Document Request", help="The ID of the client for whom documents are being requested.")
            doc_req_client_email = st.text_input("Client Email (for notifications)", help="Email address to send document request notifications.")
            doc_req_type = st.multiselect("Documents Required", 
                                        ["Proof of ID (Driver's License/Passport)", 
                                         "Proof of Address (Utility Bill/Lease)", 
                                         "Income Verification (Pay Stubs/Tax Returns)", 
                                         "Bank Statements (Last 3 Months)", 
                                         "Credit Report Authorization Form", 
                                         "Debt Validation Request",
                                         "Other (Specify in Notes)"],
                                        help="Select all documents required from the client.")        
        with col_docreq2:
            doc_req_deadline = st.date_input("Submission Deadline", value=datetime.now().date() + timedelta(days=7), help="Date by which documents are expected.")
            doc_req_priority = st.selectbox("Request Priority", ["Normal", "Urgent", "Low"], index=0, help="Priority level for this document request.")
            doc_req_notes = st.text_area("Additional Instructions/Notes for Client", height=100, help="Provide any specific instructions or context for the client regarding the documents.")

        submit_doc_req_form = st.form_submit_button("Send Document Request")
        if submit_doc_req_form:
            if not doc_req_type:
                st.error("Please select at least one document type to request.")
            elif not all([doc_req_client_id, doc_req_client_email]):
                st.error("Please provide Client ID and Client Email.")
            else:
                payload = {
                    "client_id": doc_req_client_id,
                    "client_email": doc_req_client_email,
                    "documents_required": doc_req_type,
                    "submission_deadline": str(doc_req_deadline),
                    "priority": doc_req_priority,
                    "notes": doc_req_notes,
                    "timestamp": datetime.now().isoformat()
                }
                try:
                    with st.spinner("Sending document request to n8n webhook..."):
                        response = requests.post(n8n_webhook_url_docs, json=payload, timeout=10)
                    
                    if response.status_code == 200 or response.status_code == 201:
                        st.success("Document request sent successfully to n8n webhook!")
                        st.json(response.json()) # Display n8n response for debugging/confirmation
                    else:
                        st.error(f"Failed to send request. Status code: {response.status_code}. Response: {response.text}")
                        st.warning("Please check the n8n webhook URL and your n8n workflow configuration.")
                except requests.exceptions.Timeout:
                    st.error("The request to n8n webhook timed out. Please check your n8n instance and network connection.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Network error or invalid webhook URL: {e}")
                    st.warning("Ensure the n8n webhook URL is correct and accessible.")

    st.markdown("--- ")
    st.subheader("💡 n8n Webhook Configuration Tips")
    st.markdown("""
    To integrate with n8n, you'll need to set up a 'Webhook' node in your n8n workflow. 
    
    1.  **Create a new workflow** in your n8n instance.
    2.  Add a **'Webhook' node** as the starting point.
    3.  Set the 'Webhook URL' to **'POST'** method.
    4.  Copy the generated **'Webhook URL'** from n8n and paste it into the respective input fields above.
    5.  In your n8n workflow, you can then process the incoming JSON data (e.g., save to Google Sheets, send emails, create tasks in a project management tool).
    6.  **Important:** For production use, consider using n8n's production webhooks and securing your n8n instance.
    """)

# --- Main Application Logic ---

def main():
    if not st.session_state['logged_in']:
        display_login_page()
    else:
        display_sidebar()
        
        # Admin users can switch between tabs, clients only see their report
        if st.session_state['user_role'] == 'admin':
            tab_titles = ["Credit Report", "Letter Tracking", "Onboarding Forms"]
            selected_tab = st.sidebar.radio("Navigation", tab_titles)

            if selected_tab == "Credit Report":
                display_credit_report_tab()
            elif selected_tab == "Letter Tracking":
                display_letter_sending_tracking_tab()
            elif selected_tab == "Onboarding Forms":
                display_onboarding_forms_tab()
        else: # Client role
            display_credit_report_tab()

if __name__ == "__main__":
    main()



