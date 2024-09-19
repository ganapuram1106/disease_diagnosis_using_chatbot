import os
import smtplib

def sendMails(email, message, disease):
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as connection:
        email_address = 'kaleem202120@gmail.com'
        email_password = 'xyljzncebdxcubjq'
        connection.login(email_address, email_password)
        connection.sendmail(from_addr="kaleem202120@gmail.com", to_addrs=email, msg="Subject : Disease Predictd As "+disease+"\n\n"+message+" Booking Confirmed with above doctor")


for root, dirs, directory in os.walk('diets'):
    for j in range(len(directory)):
        diet = ""
        with open(root+"/"+directory[j], "r") as file:
            lines = file.readlines()
            for i in range(len(lines)):
                diet += lines[i]+"\n"
        file.close()
        print(directory[j])
        sendMails("kaleem.mmd@gmail.com", diet, "hello")
