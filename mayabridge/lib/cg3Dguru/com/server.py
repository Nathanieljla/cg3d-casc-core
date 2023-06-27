

import socket
import threading


#TODO:  Read this https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self) 
        self.host = ''
        self.port = 50000
        self.backlog = 5
        self.size = 1024
        self.socket = None
        self.running = False
        
    def __del__(self):
        print("Deleting cg3Dguru.com.server")
        try:
            self.socket.close()
        except:
            pass
        

    def open_socket(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.host,self.port))
            self.socket.listen(5)
            return True

        except OSError as e:
            if self.socket:
                self.socket.close()
            print ("Could not open socket:{}".format(e))
            return False

    def run(self):
        self.running = self.open_socket()

        while self.running:
            client, address = self.socket.accept()
            data = client.recv(self.size)
            if data:
                eval(data.decode())

            client.close() 

        if self.socket:
            self.socket.close()


    def stop(self):
        self.running = False
        if self.socket:
            self.socket = None



if __name__ == "__main__":
    s = Server()
    s.start()
    #time.sleep(4)
    #s.Stop()
    pass
