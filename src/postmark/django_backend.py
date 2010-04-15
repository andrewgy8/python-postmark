from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.exceptions import ImproperlyConfigured

from core import PMMail

class EmailBackend(BaseEmailBackend):
    
    def __init__(self, api_key=None, default_sender=None, **kwargs):
        """
        Initialize the backend.
        """
        super(EmailBackend, self).__init__(**kwargs)
        self.api_key = getattr(settings, 'POSTMARK_API_KEY', api_key)
        if not self.api_key:
            raise ImproperlyConfigured('POSTMARK API key must be set in Django settings file or passed to backend constructor.')            
        self.default_sender = getattr(settings, 'POSTMARK_SENDER', default_sender)
                                    
    def send_messages(self, email_messages):
        """
        Sends one or more EmailMessage objects and returns the number of email
        messages sent.
        """
        if not email_messages:
            return         
        num_sent = 0
        for message in email_messages:
            sent = self._send(message)
            if sent:
                num_sent += 1
        return num_sent
        
        
    def _send(self, message):
        """A helper method that does the actual sending."""
        if not message.recipients():
            return False            
        try:
            recipients = ','.join(message.to)
            if message.__class__.__name__ == 'EmailMultiAlternatives':
                html_body = None
                for alt in message.alternatives:
                    if alt[1] == "text/html":
                        html_body=alt[0]
                        break
                postmark_message = PMMail(api_key=self.api_key, 
                                      subject=message.subject,
                                      sender=message.from_email,
                                      to=recipients,
                                      text_body=message.body,
                                      html_body=html_body)

            else:
                postmark_message = PMMail(api_key=self.api_key, 
                                      subject=message.subject,
                                      sender=message.from_email,
                                      to=recipients,
                                      text_body=message.body)
            postmark_message.send()
        except:
            if self.fail_silently:
                return False
            raise
        return True

