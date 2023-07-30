import inspect
import subprocess

PSUTIL_EXISTS = False
try:
    
    import psutil
    PSUTIL_EXISTS = True
except:
    #this will fail when using the module in cascadeur
    print("Missing python package 'psutil'. CascadeurPigeon functionality limited to receiving")
    pass



CSC_EXISTS = False
try:
    import csc
    CSC_EXISTS = True
except:
    #this will fail when using the module in wing
    pass


from .pigeon import *


class CascadeurPigeon(Pigeon):
    def __init__(self, *args, **kwargs):
        super(CascadeurPigeon, self).__init__(*args, **kwargs)
        self.known_pid = None


    @staticmethod
    def run_shell_command(cmd):
        #NOTE: don't use subprocess.check_output(cmd), because in python 3.6+ this error's with a 120 code.
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        stdout = stdout.decode()
        stderr = stderr.decode()

        print(stdout)
        print(stderr)
        if proc.returncode:
            raise Exception('Command Failed:\nreturn code:{0}\nstderr:\n{1}\n'.format(proc.returncode, stderr))

        return(stdout, stderr)


    @classmethod
    def get_temp_filename(cls):
        return('cascadeur_code.txt')
    
    
    def get_running_path(self):
        """Return the exe path of any running instance of cascadeur"""

        #we might already have a cached pid from wing.  let's try it first.
        if self.known_pid:
            try:
                process = psutil.Process(pid=self.known_pid)
                return process.exe()
            except:
                self.known_pid = None


        #let's search the running processes for cascadeur
        #ls: list = [] # since many processes can have same name it's better to make list of them
        for p in psutil.process_iter(['name', 'pid']):
            if p.info['name'] == 'cascadeur.exe':
                #we can only have one running process of cascadeur
                return psutil.Process(p.info['pid']).exe()

        return ''


    def can_dispatch(self):
        """Check if conditions are right to send code to application
        
        can_dispatch() is used to determine what dispatcher wing will use
        with when there's no active dispatcher found.
        """
        exe_path = self.get_running_path()
        return len(exe_path) > 0
    
    
    def owns_process(self, process):
        """Returns true if the process is the pigeons target application
        
        This is used when an external application is connects to wing. When True
        is returned the Dispatcher becomes the active dispatcher to send commands
        to.
        
        Args:
            process (psutils.Process) : The node to remove the data from.  
        """
        valid_process = 'cascadeur' in process.name()
        
        if valid_process:
            self.known_pid = process.pid
            
        return valid_process
    
    

    @classmethod
    def post_module_import(cls, module):
        """call the run function on the imported module if it exists
        
        We'll assume that if the run() takes any arguments that the first
        argument is the current scene, since this is the cascadeur standard.
        """

        print("Calling post module import")
        if hasattr(module, 'run'):
            signature = inspect.signature(module.run)
            if signature.parameters:
                if CSC_EXISTS:
                    scene = csc.app.get_application().get_scene_manager().current_scene()
                    module.run(scene)
                else:
                    module.run(None)
            else:
                module.run()

    

    def send(self, highlighted_text, module_path, file_path, doc_type):
        #put this after writing the file, so the code is ready to execute one casc is opened
        exe_path = self.get_running_path()
        if not exe_path:
            print('No instances of cascadeur are running')
            return

        if highlighted_text:
            self.write_temp_file(highlighted_text)
        else:
            command = u"import wingedcarrier.pigeons; wingedcarrier.pigeons.CascadeurPigeon.receive(\'{}\',\'{}\')".format(module_path, file_path)
            self.write_temp_file(command)
    
        command = '{}&-run-script&{}'.format(exe_path, 'commands.guru.read_external_code')
        CascadeurPigeon.run_shell_command(command.split('&'))



    @staticmethod
    def receive(module_path, file_path):
        if not module_path:
            CascadeurPigeon.read_file(file_path)
        else:
            CascadeurPigeon.import_module(module_path, file_path)