import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile
from pdf_generator import generate_pdf
from normalizer import normalize_columns
from email_utils import send_invoice_email
import time

st.set_page_config(page_title="LAC Invoice Pro", layout="centered")

st.title("📧 LAC Invoice Generator (Pro Edition)")
st.caption("Generate and email professional invoices directly to your clients.")

# Sidebar settings
st.sidebar.header("Settings")
business_name = st.sidebar.text_input("Business Name", "LAC Invoice Generator")
tax_rate = st.sidebar.number_input("VAT Percentage (%)", 0.0, 100.0, 15.0, step=1.0)

# ✅ Client SendGrid info inputs
st.sidebar.subheader("Email Settings (Optional, use for sending emails)")
sendgrid_api_key_input = st.sidebar.text_input("SendGrid API Key", "", type="password")
sender_email_input = st.sidebar.text_input("Sender Email Address", "")

uploaded = st.file_uploader(
    "📂 Upload Sales File (CSV/XLSX)",
    type=["csv", "xlsx"],
    key="invoice_file_upload"
)

if uploaded:
    try:
        if uploaded.name.lower().endswith(".xlsx"):
            df = pd.read_excel(uploaded)
        else:
            df = pd.read_csv(uploaded)

        df = normalize_columns(df)
        st.success("✅ File uploaded and normalized successfully!")
        st.dataframe(df.head())

        required_columns = ["clientname", "email", "amount"]
        missing = [col for col in required_columns if col not in [c.lower() for c in df.columns]]
        if missing:
            st.error(f"❌ Missing columns: {', '.join(missing)}. Please include {required_columns} in your file.")
        else:
            send_email = st.checkbox("📤 Email each invoice automatically", value=True)

            if st.button("🧾 Generate All Invoices"):
                try:
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zipf:
                        for idx, row in df.iterrows():
                            client_name = str(row.get("clientname", f"Client {idx+1}"))
                            client_email = str(row.get("email", "")).strip()
                            reference = str(row.get("referenceno", f"INV-{idx+1}"))
                            amount = float(row.get("amount", 0))

                            tax = amount * (tax_rate / 100)
                            total_with_tax = amount + tax

                            items = [{
                                "description": "Professional Services Rendered",
                                "quantity": 1,
                                "unit_price": amount,
                                "total": total_with_tax
                            }]

                            data = {
                                "business_name": business_name,
                                "client_name": client_name,
                                "reference": reference,
                                "items": items,
                                "tax": tax
                            }

                            buffer = BytesIO()
                            generate_pdf(data, mode="invoice", output_path=buffer)
                            pdf_bytes = buffer.getvalue()

                            filename = f"{reference}_{client_name.replace(' ', '_')}.pdf"
                            zipf.writestr(filename, pdf_bytes)

                            if send_email and client_email:
                                with st.spinner(f"📤 Sending invoice to {client_name} ({client_email})..."):
                                    try:
                                        send_invoice_email(
                                            to_email=client_email,
                                            client_name=client_name,
                                            reference=reference,
                                            pdf_bytes=pdf_bytes,
                                            sendgrid_api_key=sendgrid_api_key_input or None,
                                            sender_email=sender_email_input or None
                                        )
                                        st.success(f"✅ Sent to {client_name} ({client_email})")
                                    except Exception as e:
                                        st.error(f"❌ Failed to send {client_name}'s invoice: {e}")
                                    time.sleep(1)

                    zip_buffer.seek(0)
                    st.success("🎉 All invoices generated successfully!")
                    st.download_button(
                        label="⬇️ Download All Invoices (ZIP)",
                        data=zip_buffer,
                        file_name="All_Invoices.zip",
                        mime="application/zip"
                    )

                except Exception as e:
                    st.error(f"❌ Error generating or emailing invoices: {e}")

    except Exception as e:
        st.error(f"❌ Error reading uploaded file: {e}")
else:
    st.info("👆 Upload a CSV or Excel file containing client info to start.")
