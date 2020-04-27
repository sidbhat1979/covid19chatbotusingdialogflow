import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from config_reader import ConfigReader
from email import encoders


def send_email_to_botuser_local(recepient_email, message,id):
    try:
            config_reader=ConfigReader()
            configuration=config_reader.read_config()

            # instance of MIMEMultipart
            msg = MIMEMultipart()

            # storing the senders email address
            msg['From'] = configuration['SENDER_EMAIL']

            # storing the receivers email address
            msg['To'] = ",".join(recepient_email)


            # storing the subject
            msg['Subject'] = configuration['EMAIL_SUBJECT']

            # string to store the body of the mail
            body=message

            # attach the body with the msg instance
            msg.attach(MIMEText(body, 'text'))
            filename = "report" + str(id) + ".jpg"
            attachment = open("LocalReport/" + filename, 'rb')

            # instance of MIMEBase and named as p
            p = MIMEBase('application', 'octet-stream')

            # To change the payload into encoded form
            p.set_payload((attachment).read())

            # encode into base64
            encoders.encode_base64(p)

            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

            # attach the instance 'p' to instance 'msg'
            msg.attach(p)

            # creates SMTP session
            smtp = smtplib.SMTP('smtp.gmail.com', 587)

            # start TLS for security
            smtp.starttls()

            # Authentication
            smtp.login(msg['From'], configuration['PASSWORD'])

            # Converts the Multipart msg into a string
            text = msg.as_string()

            # sending the mail
            smtp.sendmail(msg['From'] , recepient_email, text)
            print('email send')


            # terminating the session
            smtp.quit()
    except Exception as e:
            print('the exception is '+str(e))

def send_email_to_botuser_global(recepient_email, message,id):
    try:
            config_reader=ConfigReader()
            configuration=config_reader.read_config()

            # instance of MIMEMultipart
            msg = MIMEMultipart()

            # storing the senders email address
            msg['From'] = configuration['SENDER_EMAIL']

            # storing the receivers email address
            msg['To'] = ",".join(recepient_email)


            # storing the subject
            msg['Subject'] = configuration['EMAIL_SUBJECT']

            # string to store the body of the mail
            body=message

            # attach the body with the msg instance
            msg.attach(MIMEText(body, 'html'))

            filename = "report" + str(id) + ".html"
            attachment = open("GlobalReport/" + filename, 'rb')

            # instance of MIMEBase and named as p
            p = MIMEBase('application', 'octet-stream')

            # To change the payload into encoded form
            p.set_payload((attachment).read())

            # encode into base64
            encoders.encode_base64(p)

            p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

            # attach the instance 'p' to instance 'msg'
            msg.attach(p)

            # creates SMTP session
            smtp = smtplib.SMTP('smtp.gmail.com', 587)

            # start TLS for security
            smtp.starttls()

            # Authentication
            smtp.login(msg['From'], configuration['PASSWORD'])

            # Converts the Multipart msg into a string
            text = msg.as_string()

            # sending the mail
            smtp.sendmail(msg['From'] , recepient_email, text)
            print('email send')


            # terminating the session
            smtp.quit()
    except Exception as e:
            print('the exception is '+str(e))





