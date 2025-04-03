# ks.py - Script to test email sending functionality

import os
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Copied send_email_with_attachment function from advance_agent.py --- 
def send_email_with_attachment(recipient_email, subject, body, file_path):
    """Sends an email with the specified file attached."""
    # Use EMAIL_ADDRESS and EMAIL_PASSWORD as specified for .env
    sender_email = os.getenv("EMAIL_ADDRESS") 
    sender_password = os.getenv("EMAIL_PASSWORD")
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")

    # --- Add Debug Print --- 
    print(f"DEBUG: Read SMTP_PORT from environment: '{smtp_port}'") 
    # -----------------------

    # --- Input Validation ---
    if not all([sender_email, sender_password, smtp_server, smtp_port]):
        print("Error: Email credentials or SMTP server details not found in .env file.")
        print("Please ensure EMAIL_ADDRESS, EMAIL_PASSWORD, SMTP_SERVER, and SMTP_PORT are set.")
        return False
    if not recipient_email or '@' not in recipient_email:
        print(f"Error: Invalid recipient email address provided: {recipient_email}")
        return False
    if not os.path.exists(file_path):
        print(f"Error: Attachment file not found at: {file_path}")
        return False

    try:
        smtp_port = int(smtp_port)
    except ValueError:
        # Use the exact value read for the error message
        print(f"Error: Invalid SMTP_PORT defined in .env file: {os.getenv('SMTP_PORT')}. Must be a number.") 
        return False

    # --- Create the email message ---
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # --- Attach the file ---
    try:
        with open(file_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        filename = os.path.basename(file_path)
        part.add_header("Content-Disposition", f"attachment; filename= {filename}")
        message.attach(part)
    except IOError as e:
        print(f"Error reading attachment file '{file_path}': {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while processing the attachment: {e}")
        return False

    # --- Connect to SMTP server and send ---
    server = None
    try:
        # Use the exact value read for the error message if connection fails
        server_name_read = os.getenv("SMTP_SERVER") 
        # --- Add Debug Print for Server --- 
        print(f"DEBUG: Read SMTP_SERVER from environment: '{server_name_read}'")
        # -----------------------------------
        print(f"Connecting to SMTP server {server_name_read}:{smtp_port}...")
        if smtp_port == 465:
             print("Using SMTP_SSL.")
             server = smtplib.SMTP_SSL(server_name_read, smtp_port, timeout=20) # Use SSL for port 465
        else:
             print("Using SMTP with STARTTLS.")
             server = smtplib.SMTP(server_name_read, smtp_port, timeout=20) # Use standard SMTP for others (like 587)
             server.ehlo() # Greet server before TLS
             server.starttls() # Encrypt connection
             server.ehlo() # Re-greet server over TLS

        print("Logging in...")
        server.login(sender_email, sender_password)
        print("Sending email...")
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)
        print(f"Email sent successfully to {recipient_email}!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("Error: SMTP Authentication failed. Check EMAIL_ADDRESS and EMAIL_PASSWORD/app password in .env file.")
        print("       (If using Gmail with 2FA, ensure you are using an App Password).")
        return False
    except (smtplib.SMTPConnectError, socket.gaierror, socket.timeout, smtplib.SMTPServerDisconnected) as e:
        # Use the exact value read for the error message
        server_name_read = os.getenv("SMTP_SERVER") 
        port_read = os.getenv("SMTP_PORT")
        print(f"Error: Could not connect to or communicate with SMTP server {server_name_read}:{port_read}. Check server/port details, network connection, and firewall.")
        print(f"       Specific error: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"An SMTP error occurred: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during email sending: {e}")
        traceback.print_exc()
        return False
    finally:
        if server:
            try:
                print("Closing SMTP connection.")
                server.quit()
            except smtplib.SMTPException:
                pass # Ignore errors during quit
# --- End of copied function ---


if __name__ == "__main__":
    print("--- Email Sending Test --- ")

    # 1. Define Test Parameters
    test_subject = "CrewAI Email Test"
    test_body = "This is a test email sent from the ks.py script to verify SMTP settings."
    # Use an existing file as a dummy attachment
    dummy_attachment_path = "README.md" 

    # 2. Check if dummy attachment exists
    if not os.path.exists(dummy_attachment_path):
        print(f"Error: Dummy attachment file '{dummy_attachment_path}' not found in the current directory.")
        print("Please create a dummy file or change the path in ks.py.")
    else:
        # 3. Prompt for Recipient Email
        recipient = input(f"Enter the recipient email address to send a test email (with {dummy_attachment_path} attached): ").strip()

        # 4. Validate and Send
        if recipient and '@' in recipient:
            print(f"\nAttempting to send test email to {recipient}...")
            
            success = send_email_with_attachment(
                recipient_email=recipient,
                subject=test_subject,
                body=test_body,
                file_path=dummy_attachment_path
            )

            if success:
                print("\nTest email sent successfully!")
            else:
                print("\nTest email failed to send. Please check the errors above and your .env settings.")
        elif recipient:
            print(f"Invalid email address format entered ('{recipient}'). Aborting test.")
        else:
            print("No recipient email entered. Aborting test.")

    print("--- Test Script Finished ---")
