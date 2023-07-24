"""This us used in wing to send commands to Cascadeur.

Directions
Add this file to Wing's preferences > IDE Extension Scripting
then bind 'send_to_cascadeur' to a hotkey via:
preferences > User Interface > Keyboard > Custom keybindings

This is a modified version of:
https://github.com/raiscui/wing-scripts/blob/master/wingHotkeys.py

Changes include:
*  unified highlighted text and sending py files to app
*  Reloading and importing py files in the namespace of their package

#starting with Pymel 1.3 we no longer need to worry about adding the completion\pi files
#https://dev.to/chadrik/pymels-new-type-stubs-2die


#The outdated way------------------------------------------
#download the devkit

#add the pi interfaces found here:
#devkitBase\devkit\other\pymel\extras\completion\pi

#Note: Maya 2023 is missing the other folder, so download Maya 2022 devkit and copy the other folder into
#the 2023 devkit

#to wing
#This can be added to the Source Analysis > Advanced > Interface File Path preference in Wing.
"""


import wingapi
import subprocess
import socket
import os,time #,locale
#import codecs
import psutil
import tempfile

from pathlib import Path



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



def get_running_path() -> list:
    """Find the path of any running instance of cascadeur"""

    ls: list = [] # since many processes can have same name it's better to make list of them
    for p in psutil.process_iter(['name', 'pid']):
        if p.info['name'] == 'cascadeur.exe':
            ls.append(psutil.Process(p.info['pid']).exe())

    return ls


def get_temp_filename():
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'cascadeur_code.txt')

    return file_path



def run_command_in_casc(command_string):

    file_path = get_temp_filename()
    f = open(file_path, 'w')
    f.writelines(command_string)
    f.close()

    #put this after writing the file, so the code is ready to execute one casc is opened
    exe_path = get_running_path()
    if not exe_path:
        print('No instances of cascadeur are running')
        return

    command = '{}&-run-script&{}'.format(exe_path, 'commands.guru.read_external_code')
    print(command)
    run_shell_command(command.split('&'))





###https://github.com/raiscui/wing-scripts/blob/master/wingHotkeys.py###

def get_wing_text():
    """
    Based on the Wing API, get the selected text, and return it
    """
    editor = wingapi.gApplication.GetActiveEditor()
    if editor is None:
        return ''
    doc = editor.GetDocument()
    start, end = editor.GetSelection()
    txt = doc.GetCharRange(start, end)
    return txt


def __Add_Parent_Module(name, path):
    found = False
    parent_module = os.path.join(path.parent, '__init__.py')

    if os.path.exists(parent_module):
        path = path.parent
        name = os.path.basename(path) + "." + name
        found = True

    return (found, name, path)


def get_module_info():
    """
    returns the module namespace and the path to the file.
    """
    editor = wingapi.gApplication.GetActiveEditor()
    if editor is None:
        return ''

    doc = editor.GetDocument()
    full_path = doc.GetFilename()

    name = os.path.basename(full_path).split('.')[0]
    path = Path(full_path)
    loop = True
    count = 0
    while loop and count < 20:
        count += 1
        loop, name, path = __Add_Parent_Module(name, path)

    #special case for when someone executes an __init__ file
    if (name.endswith(".__init__")):
        name = name.removesuffix(".__init__")

    return (name, full_path)


#"""
#Takes a string and sends to to maya over the commandline.  The string is converted by bytes on send
#"""
#def send_to_csc(sendCode):	
    ## The commandPort you opened in cg3Dguru.com.server.py Make sure this matches!
    #commandPort = 50000

    ##mSocket = socket.socket(af, socktype, proto)
    #mSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #print(sendCode)

    ## Now ping csc over the command-port
    #try:
        ## Make our socket-> Maya connection: There are different connection ways
        ## which vary between machines, so sometimes you need to try different
        ## solutions to get it to work... :-S
        ##mSocket.connect(("127.0.0.1", commandPort))
        ##mSocket.connect(("::1",commandPort)) #works!
        #mSocket.connect(("127.0.0.1", commandPort))

        ## Send our code to Maya:
        #mSocket.send( sendCode.encode() )

    #except Exception as e:
        #print ("Send to Cascadeur fail:", e)

    #time.sleep(0.3)
    #mSocket.close()



def write_temp_file(txt):
    """
    Send the selected code to be executed in Csc
    """

    # Save the text to a temp file. If we're dealing with mel, make sure it
    # ends with a semicolon, or Maya could become angered!
    #txt = get_wing_text()
    temp_path = os.path.join(os.environ['TMP'], 'wing_output_text.txt')
    f = open(temp_path, "wb")

    print(temp_path)
    f.write(txt.encode())

    f.close()

    return temp_path


#=============------------ myself mod ------------ =============#
def _highlight_to_csc(txt):
    """save the input text to file and have Cascadeur execute it"""
    
    temp_path = write_temp_file(txt)
    send_code = u'"import cg3dguru.utils.execute_wing_code; cg3dguru.utils.execute_wing_code.read_file(file_path = {})"'.format(temp_path)

    return send_code
#=============------------ myself mod ------------ =============#


def _file_to_csc():
    """send the current file's module path and file path to cascaduer"""
    
    module_path, file_path = get_module_info()
    file_path = file_path.replace("\\", "/")
    print('module path:{} full path:{}'.format(module_path, file_path))
    send_code = u'"import cg3dguru.utils.execute_wing_code; cg3dguru.utils.execute_wing_code.import_and_run(\'{0}\', file_path=\'{1}\')"'.format(module_path, file_path)
    
    return send_code


def send_to_cascadeur():
    """Assign this to your Wing IDE Hotkey"""
    highlighted_text = get_wing_text()
    if highlighted_text:
        send_code = _highlight_to_csc(highlighted_text)
    else:
        send_code = _file_to_csc()
        
    run_command_in_casc(send_code)


#def test_script():
    #app = wingapi.gApplication
    #v = "Product info is: " + str(app.GetProductInfo())
    #doc = app.GetCurrentFiles()
    #dira = app.GetStartingDirectory()
    #v += "\nAnd you typed: %s" % doc
    #v += "\nAnd you typed: %s" % dira
    #wingapi.gApplication.ShowMessageDialog("Test Message", v)


#def open_folder():
    #app = wingapi.gApplication
    #folder = app.GetStartingDirectory()
    #app.OpenURL(folder)