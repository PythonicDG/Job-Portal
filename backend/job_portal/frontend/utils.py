# utils/email_utils.py

import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list, from_email=None):
        self.subject = subject
        self.html_content = html_content
        self.recipient_list = recipient_list
        self.from_email = from_email or settings.DEFAULT_FROM_EMAIL
        threading.Thread.__init__(self)

    def run(self):
        msg = EmailMultiAlternatives(
            subject=self.subject,
            body="This is an HTML email. Please view in an HTML-compatible client.",
            from_email=self.from_email,
            to=self.recipient_list,
        )
        msg.attach_alternative(self.html_content, "text/html")
        msg.send()

def send_contact_email(name, email, message):
    subject = "New Contact Us Message"
    context = {
        'name': name,
        'email': email,
        'message': message,
    }
    html_content = render_to_string("emails/contact_us_email.html", context)
    recipient_list = [settings.DEFAULT_CONTACT_EMAIL]  # Set this in your settings.py to your desired recipient

    # Start the email thread
    EmailThread(subject, html_content, recipient_list).start()
