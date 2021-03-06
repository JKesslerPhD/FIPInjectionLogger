from django.core.management.base import BaseCommand, CommandError
from cron_data import Database
from django.core.mail import EmailMessage

class Command(BaseCommand):
    help = 'Emails all users that need to update their cat\'s info'

    def handle(self, *args, **options):
        data = Database()
        email_list = data.get_email_list()

        all_emails = "; ".join(email_list["email"])
        email = EmailMessage('Please update your cat\'s profile', "CRON Job Executed.  Users should be entering cat updates. \n The email was sent to %s" % all_emails, to=["jeff.kessler@gmail.com"])
        email.content_subtype = "html"
        email.send()
        for index, row in email_list.iterrows():

            email_message = """
            <html>
            <head></head>
            <body>
            <p>Hello %s,</p>
            <p>
            <p>Thank you for recording data on the <a href="https://fiplog.com">FIPLog.com</a> website.  Our records indicate that %s should be past the 84 day observation period.
            <p>We hope that %s is doing well.  To help inform data on the treatment process, we request that you update your cat's info on the FIPLog.com website to indicate whether or not
            %s has been cured, or if they unfortunately did not make it.</p>
            <p>
            <p>Please complete the following steps:
                <ol>
                <li>Log in to FIPLog.com using your username: %s</li>
                <li>You should see a notice linking to your <a href="https://fiplog.com/catinfo/?CatID=%i&cured=True">cat's profile</a></li>
                <li>Indicate whether or not your cat has been cured</li>
                </ol>
            <p>Our system will send this message to you once a week until you update your cat's record.  If you experience any problems, please email the <a href="mailto:jeff.kessler@gmail.com">FIPLog.com admin</a>
            <p>
            <p>Thank you for using the FIPLog.com website,
            <p>Jeff
            </body>
            </html>
            
            """ % (row["username"],row["name"],row["name"],row["name"],row["username"],row["id"])

            send_to = row["email"]
            email = EmailMessage('FIPLog.com - Was your cat cured?', email_message, to=[send_to])
            email.content_subtype = "html"
            email.send()
