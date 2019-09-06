import smtplib
from datetime import datetime
from email.message import EmailMessage


class EmailSender:

    def __init__(self, smtp: str, sender: str, username: str, password: str) \
            -> None:
        super().__init__()

        self._smtp = smtp
        self._sender = sender
        self._username = username
        self._password = password

    def send_email(self, subject: str, message: str, to: str) -> None:
        msg = EmailMessage()
        msg.set_content('{}\nDate - {}'.format(message, datetime.now()))

        msg['Subject'] = subject
        msg['From'] = self._sender
        msg['To'] = to

        # Send the message via the specified SMTP server.
        s = smtplib.SMTP(self._smtp)
        if len(self._username) != 0:
            s.login(self._username, self._password)
        s.send_message(msg)
        s.quit()
