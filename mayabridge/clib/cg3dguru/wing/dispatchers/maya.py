from .dispatcher import * 
import socket

class MayaDispatch(Dispatcher):
    commandPort = 6000

    
    def __init__(self, *args, **kwargs):
        super(MayaDispatch, self).__init__(*args, **kwargs)
        
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #import socket        



    #def write_temp_file(language):
        #"""
        #Send the selected code to be executed in Maya
    
        #language : string : either 'mel' or 'python'
        #"""
    
    
        #if language != "mel" and language != "python":
            #raise ValueError("Expecting either 'mel' or 'python'")
    
        ## Save the text to a temp file. If we're dealing with mel, make sure it
        ## ends with a semicolon, or Maya could become angered!
        #txt = getWingText()
        #if language == 'mel':
            #if not txt.endswith(';'):
                #txt += ';'
        #tempFile = os.path.join(os.environ['TMP'], 'wingData.txt')
        #f = open(tempFile, "wb")
    
        #print(tempFile)
        ##txt_unicode = uni(txt,'utf-8')
        ##txt_u8 = txt_unicode.encode('utf-8')
        ##f.write(txt_u8)
    
        #f.write ( txt.encode() )
    
        #f.close()

    def get_socket(self):
        
        # The commandPort you opened in userSetup.py Make sure this matches!
        m_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        # Now ping Maya over the command-port
        try:
            # Make our socket-> Maya connection: There are different connection ways
            # which vary between machines, so sometimes you need to try different
            # solutions to get it to work... :-S
            #mSocket.connect(("127.0.0.1", commandPort))
            #mSocket.connect(("::1",commandPort)) #works!
            m_socket.connect(("127.0.0.1", MayaDispatch.commandPort))

        except Exception as e:
            print('Connection to Maya failed: {}'.format(e))
            m_socket.close()
            m_socket = None

        finally:
            return m_socket




    def dispatch(self, highlighted_text, module_path, file_path, doc_type):
        """The main entry point for sending content from wing to an external app"""
        pass

    def can_dispatch(self):
        """Check if conditions are right to send code to application
        
        can_dispatch() is used to determine what dispatcher wing will use
        with when there's no active dispatcher found.  This is used in conojuction
        with the Dispatcher priority level to find the active_dispatcher    
        """
        m_socket = self.get_socket()
        if m_socket is not None:
            m_socket.close()
            return True
        else:
            return False
        

    def owns_process(self, process):
        """Returns true if the process is the Dispatchers target applications
        
        This is used when an external application is connects to wing. When True
        is returned the Dispatcher becomes the active dispatcher to send commands
        to.
        
        Args:
            process (psutils.Process) : The node to remove the data from.  
        """
        pass
