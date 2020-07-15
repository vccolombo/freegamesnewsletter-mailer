import logging
import pika
import json
import os

from mailer.mailer import Mailer, MailerException
from mailer.email_message import EmailMessage

class EmailBroker:
    RABBITMQ_USER = os.environ["RABBITMQ_USER"]
    RABBITMQ_PASS = os.environ["RABBITMQ_PASS"]
    QUEUE = "emails"

    logger = logging.getLogger(__name__)

    def __init__(self):
        credentials = pika.PlainCredentials(
            self.RABBITMQ_USER, self.RABBITMQ_PASS)
        self._params = pika.ConnectionParameters(
            "rabbitmq", 5672, '/', credentials)
        self._conn = None
        self._channel = None

    def connect(self):
        if not self._conn or self._conn.is_closed:
            self._conn = pika.BlockingConnection(self._params)
            self._channel = self._conn.channel()
            self._channel.queue_declare(queue=self.QUEUE, durable=True)

    def close(self):
        if self._conn and self._conn.is_open:
            self.logger.info('closing queue connection')
            self._conn.close()

    def consume(self):
        while True:
            try:
                self._channel.basic_consume(
                    queue=self.QUEUE, on_message_callback=self._callback)
                self._channel.start_consuming()
            except pika.exceptions.ConnectionClosedByBroker:
                self.logger.exception(f"Connection closed by RabbitMQ")
                break
            # Do not recover on channel errors
            except pika.exceptions.AMQPChannelError as err:
                self.logger.exception(f"Caught a channel error: {err}, stopping...")
                break
            # Recover on all other connection errors
            except pika.exceptions.AMQPConnectionError:
                self.logger.warn("Connection was closed, retrying...")
                continue   

    def _callback(self, ch, method, properties, body):
        try:
            data = json.loads(body)

            email_message = EmailMessage(
                data["email"], data["subject"], data["html"])
            Mailer().send_email(email_message)

            ch.basic_ack(delivery_tag = method.delivery_tag)
        except MailerException as e:
            self.logger.exception(e)
            ch.basic_nack(delivery_tag = method.delivery_tag)
        except Exception as e:
            self.logger.exception(e)
            ch.basic_reject(
                delivery_tag=method.delivery_tag, requeue=False)
