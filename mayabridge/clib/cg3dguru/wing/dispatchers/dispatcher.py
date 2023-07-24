
import os


class Dispatcher(object):
    def __init__(self, *args, **kwargs):
        pass
    
    
    @classmethod
    def get_temp_filename(cls):
        return('wing_output_text.txt')


    @classmethod
    def write_temp_file(cls, txt):
        """
        Send the selected code to be executed in Csc
        """
    
        # Save the text to a temp file. If we're dealing with mel, make sure it
        # ends with a semicolon, or Maya could become angered!
        #txt = get_wing_text()
        temp_path = os.path.join(os.environ['TMP'], cls.get_temp_filename())
        f = open(temp_path, "wb")
    
        print('writing temp file:{}'.format(temp_path))
        f.write(txt.encode())
    
        f.close()
    
        return temp_path
    
    #@property
    #def priority(self):
        #return self.get_priority()
        

    #def get_priority(self):
        #"""What is the priority of this dispatcher over other dispatchers
        
        #dispatchers.core.DISPATCHERS is an optional list of what the priority
        #between available dispatchers.  If the user hasn't defined this list
        #then the DISPATCHERS is build based on the priority returned by this
        #method.        
        #"""
        #return 0
        
    
    def dispatch(self, highlighted_text, module_path, file_path, doc_type):
        """The main entry point for sending content from wing to an external app"""
        pass
    

    def can_dispatch(self):
        """Check if conditions are right to send code to application
        
        can_dispatch() is used to determine what dispatcher wing will use
        with when there's no active dispatcher found.  This is used in conojuction
        with the Dispatcher priority level to find the active_dispatcher    
        """
        pass
    
    def owns_process(self, process):
        """Returns true if the process is the Dispatchers target applications
        
        This is used when an external application is connects to wing. When True
        is returned the Dispatcher becomes the active dispatcher to send commands
        to.
        
        Args:
            process (psutils.Process) : The node to remove the data from.  
        """
        return 'maya' in process.name()


