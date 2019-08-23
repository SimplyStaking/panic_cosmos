from twilio.rest import Client


class TwilioApi:

    def __init__(self, account_sid: str, auth_token: str) -> None:
        self._client = Client(account_sid, auth_token)

    def dial_number(self, call_from: str, call_to: str,
                    twiml_instructions_url: str):
        self._client.calls.create(
            to=call_to, from_=call_from,
            url=twiml_instructions_url, method="GET")
