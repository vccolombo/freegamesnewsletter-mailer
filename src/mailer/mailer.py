import os
import time
import logging
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Mailer:
    logger = logging.getLogger(__name__)

    SENDER_EMAIL = "freegamesnewsletter@gmail.com"
    SENDER_PASSWORD = os.environ["EMAIL_PASS"]

    # smtp configs
    SMTP_DOMAIN = "smtp.gmail.com"
    SMTP_PORT = 465

    def __init__(self):
        self._create_smtp_connection()

    def _create_smtp_connection(self):
        try:
            context = ssl.create_default_context()
            self.smtp_client = smtplib.SMTP_SSL(
                self.SMTP_DOMAIN, self.SMTP_PORT, context=context)
            self.smtp_client.login(self.SENDER_EMAIL, self.SENDER_PASSWORD)
        except smtplib.SMTPException as e:
            Mailer.logger.exception(e)
            # try again after 10 seconds
            time.sleep(10)
            self._create_smtp_connection()
    
    def send_email(self, email_message):
        message = self._get_MIME_message(email_message)
        self._send_email(email_message.to, message)

    def _get_MIME_message(self, email_message):
        message = MIMEMultipart("alternative")
        message["From"] = self.SENDER_EMAIL
        message["To"] = email_message.to
        message["Subject"] = email_message.subject
        message["X-Priority"] = "3"

        message.attach(MIMEText(email_message.plain, "plain"))
        message.attach(MIMEText(email_message.html, "html"))

        return message.as_string()

    def _send_email(self, to, message):
        try:
            self.smtp_client.sendmail(
                self.SENDER_EMAIL, to, message)
            Mailer.logger.info(f"Email sent to {to}")
        except smtplib.SMTPException as e:
            Mailer.logger.exception(e)
            # recreate connection and try again
            self._create_smtp_connection()
            self._send_email(to, message)