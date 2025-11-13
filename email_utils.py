import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

def send_invoice_email(to_email, client_name, reference, pdf_bytes, sendgrid_api_key=None, sender_email=None):
    """
    Send an invoice email with PDF attachment via SendGrid.
    Allows custom API key and sender email for multi-client usage.
    """
    sendgrid_api_key = sendgrid_api_key or os.getenv("SENDGRID_API_KEY")
    sender_email = sender_email or os.getenv("SENDER_EMAIL", "no-reply@lacautomations.co.za")

    if not sendgrid_api_key:
        raise ValueError("❌ Missing SendGrid API key. Provide one in sidebar or in .env")
    if not sender_email:
        raise ValueError("❌ Missing sender email. Provide one in sidebar or in .env")

    subject = f"Invoice {reference} from {sender_email.split('@')[1].split('.')[0]}"
    content = f"""
    Dear {client_name},

    Please find attached your invoice ({reference}).

    Kind regards,  
    {sender_email.split('@')[1].split('.')[0]}
    """

    encoded_pdf = base64.b64encode(pdf_bytes).decode()
    attachment = Attachment(
        FileContent(encoded_pdf),
        FileName(f"{reference}.pdf"),
        FileType("application/pdf"),
        Disposition("attachment")
    )

    message = Mail(
        from_email=sender_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=content,
        html_content=content.replace("\n", "<br>")
    )
    message.attachment = attachment

    try:
        sg = SendGridAPIClient(sendgrid_api_key)
        response = sg.send(message)
        if response.status_code in [200, 202]:
            return True
        else:
            raise Exception(f"SendGrid responded with code {response.status_code}")
    except Exception as e:
        raise Exception(f"SendGrid error: {e}")
