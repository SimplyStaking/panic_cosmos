# Twilio

- To create a free trial **Twilio account**, head to the [try-twilio page](https://www.twilio.com/try-twilio) and sign up using your details.
- Next, three important pieces of information have to be obtained:
    1. Navigate to the [account dashboard page](https://www.twilio.com/console).
    2. Click the 'Get a Trial Number' button in the dashboard to generate a unique number.
    3. Take a note of the (i) Twilio phone number.
    4. Take a note of the (ii) account SID and (iii) auth token.
- All that remains now is to add a number that Twilio is able to call:
    5. Navigate to the [Verified Caller IDs page](https://www.twilio.com/console/phone-numbers/verified).
    6. Press the red **+** to add a new personal number and follow the verification steps.
    7. One number is enough for now, but you can repeat these steps to verify more than one number.

**At the end, you should have:**
1. A Twilio phone number.
2. The account SID, available in the account dashboard.
3. The auth token, available in the account dashboard.
4. A verified personal phone number *(at least one)*

If you wish to explore more advanced features, PANIC also supports configurable [TwiML](https://www.twilio.com/docs/voice/twiml); instructions which can re-program Twilio to do more than just call numbers. By default, the TwiML is set to [reject calls](https://www.twilio.com/docs/voice/twiml/reject) as soon as the recipient picks up, without any charges. This can be re-configured from the twilio section of the internal config to either a URL or raw TwiML instructions.

---
[Back to main installation page](INSTALL_AND_RUN.md)