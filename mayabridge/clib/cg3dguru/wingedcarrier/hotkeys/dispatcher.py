import site
import sys
import subprocess
import socket
import os
import tempfile
from pathlib import Path


import wingapi


print('User site:{}'.format(site.USER_SITE))


#TODO: What's the best way to get access psutil packaage?    
global_site_package = r'C:\Users\natha\AppData\Roaming\Python\Python310\site-packages'
if global_site_package not in sys.path:
    sys.path.append(global_site_package)

import psutil


#we need to dynamically add our dispatchers package
_file_path = os.path.dirname(__file__)
_file_path = os.path.dirname(_file_path)

if _file_path not in sys.path:
    sys.path.append(_file_path)
    
#_file_path = os.path.join(_file_path, 'site-packages')
#if _file_path not in sys.path:
    #sys.path.append(_file_path)    

import pigeons
import pigeons.maya
import pgeons.cascadeur


CARRIERS = [
    pigeons.maya.MayaPigeon(),
    pigeons.cascaduer.CascadeurPigeon()
]
"""The global list of all carrier pigeons that can be dispatched

If a new Pigeon sub-class is created, it must also be added to this list to
be used.
"""

_CLASS_INSTANCE_MAPPING = {item.__class__.__name__: item for item in CARRIERS}
print(_CLASS_INSTANCE_MAPPING)


_ACTIVE_CARRIER: pigeons.pigeon.Pigeon = None



        
def _get_document_text():
    """Based on the Wing API returns (selected text, doctype) """
    
    editor = wingapi.gApplication.GetActiveEditor()
    if editor is None:
        return ''
    
    doc = editor.GetDocument()
    doc_type = doc.GetMimeType()
    start, end = editor.GetSelection()
    txt = doc.GetCharRange(start, end)
    return (txt, doc_type)



def _get_module_info():
    """Returns the module namespace and the path to the file."""
    
    def _add_parent_module(name, path):
        found = False
        parent_module = os.path.join(path.parent, '__init__.py')
    
        if os.path.exists(parent_module):
            path = path.parent
            name = os.path.basename(path) + "." + name
            found = True
    
        return (found, name, path)    
    

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
        loop, name, path = _add_parent_module(name, path)

    #special case for when someone executes an __init__ file
    if (name.endswith(".__init__")):
        name = name.removesuffix(".__init__")

    return (name, full_path)



def _find_process_owner(process):
    global CARRIERS

    if _ACTIVE_DISPATCHER is None or not _ACTIVE_DISPATCHER.owns_process(process):
        _ACTIVE_DISPATCHER = None
        
        for dis in CARRIERS:
            if dis.owns_process(process):  
                _ACTIVE_DISPATCHER = dis
                break
            
    #we'll always the last active dispatcher at the top of our dispatcher list
    if _ACTIVE_DISPATCHER and CARRIERS[0] !=  _ACTIVE_DISPATCHER:
        idx = CARRIERS.index(_ACTIVE_DISPATCHER)
        CARRIERS.pop(idx)
        CARRIERS.insert(0, _ACTIVE_DISPATCHER)
                


def _find_best_process():
    valid_dispatchers = []
    
    for dis in CARRIERS:
        if dis.can_dispatch():
            valid_dispatchers.append(dis)
            
    if not valid_dispatchers:
        return None
    
    if len(valid_dispatchers) > 1:
        print("Mutliple dispatchers found. Using first one :{}".format(valid_dispatchers))
        
    return valid_dispatchers[0]



def _activate_by_process(process):
    """If we're actively debugging try to find the process owner"""
    global _ACTIVE_CARRIER

    if process:
        _find_process_owner(process)
    else:
        _ACTIVE_CARRIER = None
        
        

def dispatch_carrier(carrier: pigeons.pigeon.Pigeon = None):
    """Used to send the data to an external app via the active carrier
    
    When no carrier is provided the active carrier will be the last carrier
    dispatched. When a new debug connection is established, that app pigeon
    will automatically become the active carrier, until overridden by a user
    specific hotkey such as dispactch_maya().
    
    If an active carrier doesn't exist, then the function will attempt to
    find the best process to communicate with via Pigeon.can_dispatch()
    
    args:
        carrier (Pigeon)(Optional) : a specific pigeon to become the active carrier
        
    """
    global _ACTIVE_CARRIER

    print("here")
    if carrier:
        _ACTIVE_CARRIER = carrier
    
    if _ACTIVE_CARRIER is None:
        _ACTIVE_CARRIER = _find_best_process()
        

    if _ACTIVE_CARRIER is not None:
        highlighted_text, doc_type = _get_document_text()
        module_path, file_path = _get_module_info()
        file_path = file_path.replace("\\", "/")
        print('module path:{} full path:{}'.format(module_path, file_path))        
        
        _ACTIVE_CARRIER.send(highlighted_text, module_path, file_path, doc_type)
    else:
        print("No application to dispatch to!")
        
        

def dispatch_maya():
    dispatch_carrier(carrier=_CLASS_INSTANCE_MAPPING['MayaPigeon'])

    

def dispatch_cascadeur():
    dispatch_carrier(carrier=_CLASS_INSTANCE_MAPPING['CascadeurPigeon'])
        




#-----------WIN-IDE signal slots for active debug is below this line--------------
      
def _get_debug_process(current_run_state=None) -> psutil.Process:
    if current_run_state is None:
        debugger = wingapi.gApplication.GetDebugger()
        current_run_state = debugger.GetCurrentRunState()

    if not current_run_state:
        print("no debug run state found")
        return None
    
    pid = current_run_state.GetProcessID()
    process: psutil.Process = psutil.Process(pid=pid)
    print('connected to PID:{}    name:{}    exe:{}'.format(process.pid, process.name(), process.exe()))

    return process


        
def _debugger_connected(*args, **kwargs):
    if args:
        process = _get_debug_process(args[0])
        _activate_by_process(process)


    
def _debugger_changed(*args, **kwargs):
    if not args:
        _activate_by_process(None)



debugger = wingapi.gApplication.GetDebugger()
debugger.Connect('new-runstate', _debugger_connected)
debugger.Connect('current-runstate-changed', _debugger_changed)
