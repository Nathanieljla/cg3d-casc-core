import sys
import os
import win32com.server.register
import socket

#https://stackoverflow.com/questions/33003498/typeerror-a-bytes-like-object-is-required-not-str
class client(object):
    
    @staticmethod
    def log(message):
        s = None
        try:
            host = 'localhost'
            port = 50000
            size = 1024
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host,port))
            s.send(message.encode())
            return True
        except socket.error as e:
            if s:
                s.close()
            print ("Could not open socket: " + e)
    
            return False
    
    
    
    
if __name__ == '__main__':
    client.log("this is data")