from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to, subject, text):
    message = Mail(
        from_email='tradetrackerbot123@gmail.com',
        to_emails= to,
        subject=subject,
        html_content=text)
    try:
        sg = SendGridAPIClient('XXXXXXXXXXXXXXXXXXXXXX')
        response = sg.send(message)
    except Exception as e:
        print(e.message)
