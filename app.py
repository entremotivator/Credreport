import streamlit as st
import requests
import tempfile
import os

st.set_page_config(page_title="📤 PDF to Webhook")

st.title("📄 Upload PDF and Send to n8n Webhook")

# Webhook URL input
webhook_url = st.text_input("🔗 Enter your n8n Webhook URL")

st.subheader("👤 Client Information")
client_name = st.text_input("Full Name")
client_email = st.text_input("Email")
client_phone = st.text_input("Phone Number")

# Upload file
uploaded_file = st.file_uploader("📁 Upload PDF", type=["pdf"])

if uploaded_file and webhook_url and client_name and client_email:
    if st.button("🚀 Send to Webhook"):
        try:
            # Save uploaded file to a temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            # Prepare form data and file
            with open(tmp_file_path, "rb") as f:
                files = {
                    "file": (uploaded_file.name, f, "application/pdf")
                }
                data = {
                    "name": client_name,
                    "email": client_email,
                    "phone": client_phone
                }

                response = requests.post(webhook_url.strip(), data=data, files=files)

            # Cleanup
            os.remove(tmp_file_path)

            # Response handling
            if response.status_code == 200:
                st.success("✅ File and client info sent successfully!")
                try:
                    st.json(response.json())
                except:
                    st.write(response.text)
            else:
                st.error(f"❌ Failed with status code: {response.status_code}")
                st.text(response.text)

        except Exception as e:
            st.error(f"Error: {str(e)}")
else:
    st.info("Please fill in all required fields and upload a PDF.")

