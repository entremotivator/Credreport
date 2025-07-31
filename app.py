import streamlit as st
import requests
import tempfile
import os

st.set_page_config(page_title="📤 PDF to Webhook")

st.title("📄 Upload PDF and Send to n8n Webhook")

# Webhook URL input
webhook_url = st.text_input("🔗 Enter your n8n Webhook URL")

# Upload file
uploaded_file = st.file_uploader("📁 Upload PDF", type=["pdf"])

if uploaded_file and webhook_url:
    if st.button("🚀 Send to Webhook"):
        try:
            # Save uploaded file to a temp location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            # Prepare file for sending
            with open(tmp_file_path, "rb") as f:
                files = {"file": (uploaded_file.name, f, "application/pdf")}
                response = requests.post(webhook_url.strip(), files=files)

            # Cleanup
            os.remove(tmp_file_path)

            # Response
            if response.status_code == 200:
                st.success("✅ File sent successfully!")
                st.json(response.json())
            else:
                st.error(f"❌ Failed with status code: {response.status_code}")
                st.text(response.text)

        except Exception as e:
            st.error(f"Error: {str(e)}")

else:
    st.info("Please upload a PDF and enter a valid webhook URL.")
