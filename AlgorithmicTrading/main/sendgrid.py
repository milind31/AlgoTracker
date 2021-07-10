from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(to, subject, text):
    message = Mail(
        from_email='tradetrackerbot123@gmail.com',
        to_emails= to,
        subject=subject,
        html_content=text)
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
    except Exception as e:
        print(e.message)