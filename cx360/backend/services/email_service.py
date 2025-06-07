from pydantic import EmailStr
import os
import logging
from typing import List # Ensure List is imported for type hinting

# Attempt to import the FastMail instance 'fm' from main.py
# This creates a dependency on main.py being initialized.
# For services, it's sometimes cleaner if 'fm' is passed as an argument or if email sending
# is a method of a class that gets 'fm' injected.
# However, for this subtask, direct import is simpler if it works with Python's module system.
try:
    from cx360.backend.main import fm # Assuming main.py is in cx360.backend
    from fastapi_mail import MessageSchema, MessageType # These are needed if actually sending
except ImportError:
    # Fallback or error if fm cannot be imported (e.g. circular dependency, or structure issue)
    # For this subtask, we'll assume import works.
    # In a more complex app, consider a shared config module for 'fm'.
    fm = None # Define fm as None if import fails to avoid NameError later, though usage will fail.
    MessageSchema = None
    MessageType = None
    logging.getLogger(__name__).error("Failed to import 'fm' from cx360.backend.main. Email sending will not work.")


logger = logging.getLogger(__name__)

def log_email_intent(subject: str, recipient_to: List[EmailStr], body: str):
    """
    Logs the intent to send an email.
    In a real scenario with SUPPRESS_SEND=0, this function would be async
    and use `await fm.send_message(...)`.
    """
    if not fm or not MessageSchema or not MessageType:
        logger.error(f"FastMail not configured. Cannot log email intent to: {recipient_to}, Subject: '{subject}'")
        return

    # Construct the message as if we were going to send it
    # This helps verify that MessageSchema is correctly used, even if not sending.
    message = MessageSchema(
        subject=subject,
        recipients=recipient_to,
        body=body,
        subtype="html" # Or "plain" as needed
    )

    if fm.config.SUPPRESS_SEND == 1:
        logger.info(
            f"EMAIL INTENT (Sending Suppressed): To: {message.recipients}, Subject: '{message.subject}', "
            f"Body: '{message.body[:200]}...'" # Log a snippet of the body
        )
    else:
        # This block would ideally not be reached if we are only logging intent.
        # If SUPPRESS_SEND is 0, actual sending should be async and handled differently.
        logger.warning(
            f"Email sending is NOT suppressed. Actual email sending logic should be async "
            f"and is not implemented in this synchronous 'log_email_intent' function. "
            f"Intended for: To: {message.recipients}, Subject: '{message.subject}'"
        )

# Example of how it might look if it were async and actually sending:
# async def send_alert_email_actual(subject: str, recipient_to: List[EmailStr], body: str):
#     if not fm:
#         logger.error("FastMail 'fm' instance not available.")
#         return
#
#     message = MessageSchema(
#         subject=subject,
#         recipients=recipient_to,
#         body=body,
#         subtype=MessageType.html
#     )
#     try:
#         await fm.send_message(message)
#         logger.info(f"Alert email sent to: {recipient_to}, Subject: '{subject}'")
#     except Exception as e:
#         logger.error(f"Failed to send alert email to {recipient_to}. Error: {e}", exc_info=True)
```
