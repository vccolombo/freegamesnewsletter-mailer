import logging

from mailer.mailer import Mailer
from mailer.email_message import EmailMessage

logging.basicConfig(level=logging.INFO)

email_message = EmailMessage("victorcora98@gmail.com", "test", "test")
Mailer().send_email(email_message)