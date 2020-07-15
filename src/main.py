import logging

from broker.email_broker import EmailBroker

def main():
    logging.basicConfig(level=logging.INFO)

    broker = EmailBroker()
    broker.connect()
    broker.consume()
    broker.close()

if __name__ == "__main__":
    main()