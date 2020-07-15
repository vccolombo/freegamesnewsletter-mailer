import os
import time
import logging
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class MailerException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Mailer:
    logger = logging.getLogger(__name__)

    MAX_ATTEMPTS = 3

    SENDER_EMAIL = "freegamesnewsletter@gmail.com"
    SENDER_PASSWORD = os.environ["EMAIL_PASS"]

    # smtp configs
    SMTP_DOMAIN = "smtp.gmail.com"
    SMTP_PORT = 465

    def __init__(self):
        self.smtp_client = None

    def send_email(self, email_message):
        try:
            self._create_smtp_connection()

            message = self._get_MIME_message(email_message)
            self._send_email(email_message.to, message)
        except MailerException as e:
            raise e
        finally:
            self._terminate_smtp_connection()

    def _create_smtp_connection(self):
        for _ in range(self.MAX_ATTEMPTS):
            try:
                context = ssl.create_default_context()
                self.smtp_client = smtplib.SMTP_SSL(
                    self.SMTP_DOMAIN, self.SMTP_PORT, context=context)
                self.smtp_client.login(self.SENDER_EMAIL, self.SENDER_PASSWORD)
            except smtplib.SMTPException as e:
                self.logger.exception(e)
                # try again after 10 seconds
                time.sleep(10)
            else:
                break # Don't retry if successfull
        else:
            raise MailerException("Failed to create SMTP connection")
    
    def _terminate_smtp_connection(self):
        try:
            self.smtp_client.quit()
        except smtplib.SMTPServerDisconnected:
            self.logger.info("SMTP already disconnected")

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
        for _ in range(self.MAX_ATTEMPTS):
            try:
                self.smtp_client.sendmail(
                    self.SENDER_EMAIL, to, message)
                self.logger.info(f"Email sent to {to}")
            except smtplib.SMTPServerDisconnected as e:
                self.logger.warn(e)
                # recreate connection and try again
                self._create_smtp_connection()
            except smtplib.SMTPResponseException as e:
                self.logger.exception(e)
                # try again after 10 seconds
                time.sleep(10)
            else:
                break # Don't retry if successfull
        else:
            raise MailerException(f"Failed to send email: {to} {message}")
            