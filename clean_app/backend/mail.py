import os.path
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
from clean_app.backend.backend import get_config

def add_message_to_email_template(message):
    fullhtml = get_config()["EMAIL"]["TEMPLATE"].replace(
        "[!MESSAGE!]",
        message
    )
    return fullhtml


def send_default_mail():
    c = get_config()["EMAIL"]
    send_mail(
        send_from = c["FROM"],
        send_to = c["TO"],
        subject = c["SUBJECT"],
        message=add_message_to_email_template(c["MESSAGE"]),
        files=[os.path.join("../../tmp", "putzplan.pdf")],
        server=c["SERVER"],
        port=c["PORT"],
        username=c["USERNAME"],
        password=c["PASSWORD"],
        carbon_copy=c["CC"],
    )


def send_mail(send_from, send_to, subject, message, files=[],
              server="localhost", port=587, username='', password='',
              use_tls=True, carbon_copy=None):
    """Compose and send email with provided info and attachments.

    Args:
        send_from (str): from name
        send_to (list[str]): to name(s)
        subject (str): message title
        message (str): message body
        files (list[str]): list of file paths to be attached to email
        server (str): mail server host name
        port (int): port number
        username (str): server auth username
        password (str): server auth password
        use_tls (bool): use TLS mode
        carbon_copy (list[str]): list of adresses to CC to

    """
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = ",".join(send_to)
    if carbon_copy:
        msg['Cc'] = ",".join(carbon_copy)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject


    # Record the MIME types of both parts - text/plain and text/html.
    msg.attach(MIMEText(message,"html"))

    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename={}'.format(Path(path).name))
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    if use_tls:
        smtp.starttls()
    smtp.login(username, password)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.quit()

