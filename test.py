POSTMARK_API_TOKEN = '1fbd4b5e-1670-400b-b078-5b77a7c83a18'
POSTMARK_SENDER = 'lancelot@hardel.me'
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate


def send_mail(send_from, send_to, subject, text, files=None,
              server="127.0.0.1"):
    assert isinstance(send_to, list)
    print(server)

    msg = MIMEMultipart(
        From=send_from,
        To=COMMASPACE.join(send_to),
        Date=formatdate(localtime=True),
        Subject=subject
    )
    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            msg.attach(MIMEApplication(
                fil.read(),
                Content_Disposition='attachment; filename="%s"' % basename(f)
            ))

    smtp = smtplib.SMTP(server)
    smtp.login(POSTMARK_API_TOKEN, POSTMARK_API_TOKEN)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

send_mail(
    POSTMARK_SENDER,
    ['debetux@gmail.com'],
    'FacebookExportMessages', "Hello, {} messages for {} requests".format(1, 2),
    [],
    'smtp.postmarkapp.com:587'
)
