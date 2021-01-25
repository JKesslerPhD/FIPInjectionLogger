from cron_data import Database
from django.core.mail import send_mail
from django.conf import settings

settings.configure()
data = Database()

email_list = data.get_email_list()

from django.core.mail import EmailMessage
email = EmailMessage('Hello', 'World', to=['user@gmail.com'])
email.send()