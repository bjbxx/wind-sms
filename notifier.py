""" Module used to send a message and png image to a cell phone """

import smtplib
import re
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

class SmtpNotifier(object):
    """Used to send a MIME message via carrier SMPT -> SMS"""
    def __init__(self):
        self.email_username = "" # username@gmail.com
        self.email_password = "" # password
        self.phone_number = "" # eg xxxxxxxxx@tmomail.net

    def send(self, message_text, filename):
        """Sends a MIME message via SMPT over TTLS"""

        # Format message to look like an email
        message = MIMEMultipart()
        message.attach(MIMEText(message_text))
        message["From"] = self.email_username
        message["To"] = self.phone_number
        message["Subject"] = "Wind Alert"

        # Make sure file is valid - currenly only support png files
        if filename and re.compile("\w+\.(png|PNG)$").search(filename):
            try:
                file = open(filename, 'rb')
                img = MIMEImage(file.read())
                file.close()
                message.attach(img)
            except IOError:
                print('Unable to attach MIME image')

        # Connect and send
        try:
            smtp = smtplib.SMTP('smtp.gmail.com:587')
            smtp.starttls()
            smtp.login(self.email_username, self.email_password)
            smtp.sendmail(self.email_username, \
                          self.phone_number, \
                          message.as_string())
            smtp.quit()
        except smtplib.SMTPConnectError:
            print("Oops!  Could not send alert...")
        except smtplib.SMTPAuthenticationError:
            print("Unable to login successfully...")
