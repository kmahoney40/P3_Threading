import logging
import datetime
import smtplib
import socket
import string



class e_mail:
    def __init__(self):
        self.today = datetime.date.today()
        self.host_name = socket.gethostname()
        self.host_ip = socket.gethostbyname(self.host_name)
        self.smtp_obj = smtplib.SMTP('smtp.gmail.com', 587)
        self.smtp_obj.starttls()
        self.smtp_obj.login('k.mahohney.40@gmail.com','mQTwsUzys2panGZ')
        self.sender = 'k.mahohney.40@gamil.com'
        self.subject = "Daily Update"
        self.body = ""
        self.receivers = ['kmahoney40@hotmail.com']
        self.message = """
        From k.mahohney.40@gmail.com
        To kmahoney40@hotmail.com
        Subject: {}
        {}
        Current IP: {}
        Time: {}
        """
    #def __init__

    def get_ip(cls):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    def send_mail(cls, sub=None, bod=None):
        dt_now = str(datetime.datetime.now())
    
        if sub != None:
            cls.subject = sub
        if bod != None:
            cls.body = bod
        cls.host_ip = cls.get_ip()# socket.gethostbyname(cls.host_name)
        ipAsList = str.split(cls.host_ip, ".")
        cls.host_ip = "x.x." + ipAsList[2] + "." + ipAsList[3]
        cls.message = cls.message.format(cls.subject, cls.body, cls.host_ip, dt_now)
        #cls.smtp_obj.sendmail(cls.sender, cls.receivers, cls.message)
        cls.smtp_obj.quit() 
        
     # def send_mail()
# class e_mail