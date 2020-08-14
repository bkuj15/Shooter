import smtplib
import sys




if len(sys.argv) == 2:

    # Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP( "smtp.gmail.com", 587 )

    server.starttls()

    server.login( 'someemail', 'somepassword*' )

    subj = "Subject: Poco loco en stonks\n\n"
    msg = sys.argv[1]

    # Send text message through SMS gateway of destination number
    server.sendmail( 'someemail1', 'someemai2', subj + msg )
else:
    print("sike wrong number of args:" + str(len(sys.argv)))
