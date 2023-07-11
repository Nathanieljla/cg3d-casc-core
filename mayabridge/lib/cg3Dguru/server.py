

import socket
import threading


__SERVER = None


#TODO: Read this https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
#TODO: I should probably change this to a subprocess or multiprocess? https://stackoverflow.com/questions/2629680/deciding-among-subprocess-multiprocessing-and-thread-in-python
#TODO: Handle killing thread/subprocess if parent process crashes. https://stackoverflow.com/questions/23434842/python-how-to-kill-child-processes-when-parent-dies
class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self) 
        self.host = ''
        self.port = 50000
        self.backlog = 5
        self.size = 1024
        self.socket = None
        self.running = self.open_socket()
        
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
        if not self.running:
            print("Failed to open port!  Thread failed.")
            return

        while self.running:
            client, address = self.socket.accept()
            data = client.recv(self.size)
            if data:
                exec(data.decode())

            client.close() 

        if self.socket:
            self.socket.close()


    def stop(self):
        self.running = False
        #if self.socket:
            #self.socket = None



def start_server():
    global __SERVER
    if __SERVER is None:
        __SERVER = Server()
        
    __SERVER.run()
    return __SERVER.is_alive()


def stop_server():
    if __SERVER is not None and __SERVER.is_alive():
        __SERVER.stop()




if __name__ == "__main__":
    s = Server()
    s.start()
    #time.sleep(4)
    #s.Stop()
    pass
