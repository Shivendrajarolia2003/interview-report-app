import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
from config import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SENDER_NAME
from utils.database import log_email_attempt

def send_interview_report_email(
    recipient_email,
    student_name,
    report_id,
    pdf_path=None,
    report_markdown="",
    smtp_username=None,
    smtp_password=None,
    smtp_server=None,
    smtp_port=None,
    sender_name=None
):
    """
    Sends personalized interview report email to student via SMTP.
    Attaches PDF report if provided.
    Logs success or failure to database.
    """
    username = smtp_username or os.getenv("SMTP_USERNAME") or SMTP_USERNAME
    password = smtp_password or os.getenv("SMTP_PASSWORD") or SMTP_PASSWORD
    server_host = smtp_server or os.getenv("SMTP_SERVER") or SMTP_SERVER
    port_num = int(smtp_port or os.getenv("SMTP_PORT") or SMTP_PORT)
    from_name = sender_name or os.getenv("SENDER_NAME") or SENDER_NAME
    
    if not username or not password or username == "your_company_email@gmail.com":
        err_msg = "SMTP Credentials not configured. Please set SMTP Username & App Password in Sidebar or .env file."
        log_email_attempt(report_id, recipient_email, "Failed", err_msg)
        return False, err_msg
        
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{from_name} <{username}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"Your Interview Feedback Report — {student_name}"
        
        # HTML Email Body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
                <h2 style="color: #2563eb;">Interview Feedback Report</h2>
                <p>Hi <strong>{student_name}</strong>,</p>
                <p>Thank you for attending your recent interview session with our team.</p>
                <p>We have prepared your personalized interview feedback report to help you identify your technical strengths and key areas for growth.</p>
                <div style="background-color: #f8fafc; padding: 15px; border-left: 4px solid #2563eb; margin: 20px 0;">
                    <p style="margin: 0;"><strong>Attached document:</strong> Your complete PDF feedback report is attached to this email.</p>
                </div>
                <p>We encourage you to review the suggested practice recommendations and action plan.</p>
                <br>
                <p>Best regards,</p>
                <p><strong>{from_name}</strong></p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach PDF if exists
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as f:
                pdf_attachment = MIMEApplication(f.read(), _subtype="pdf")
                pdf_filename = Path(pdf_path).name
                pdf_attachment.add_header('Content-Disposition', 'attachment', filename=pdf_filename)
                msg.attach(pdf_attachment)
                
        # Send via SMTP with TLS
        server = smtplib.SMTP(server_host, port_num)
        server.starttls()
        server.login(username, password)
        server.sendmail(username, recipient_email, msg.as_string())
        server.quit()
        
        log_email_attempt(report_id, recipient_email, "Sent", "")
        return True, "Email sent successfully!"
        
    except Exception as e:
        error_msg = str(e)
        log_email_attempt(report_id, recipient_email, "Failed", error_msg)
        return False, error_msg
