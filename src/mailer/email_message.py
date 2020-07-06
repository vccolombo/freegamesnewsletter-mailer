from bs4 import BeautifulSoup

class EmailMessage:
    def __init__(self, receiver_email, subject, html):
        self.to = receiver_email
        self.subject = subject
        self.html = html
        self.plain = self._get_plain_text_from_html(self.html)

    def _get_plain_text_from_html(self, html):
        soup = BeautifulSoup(html, "lxml")
        text = soup.get_text()
        return text