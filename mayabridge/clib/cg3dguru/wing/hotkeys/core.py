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
#_file_path = os.path.join(_file_path, 'site-packages')
if _file_path not in sys.path:
    sys.path.append(_file_path)
    
#_file_path = os.path.join(_file_path, 'site-packages')
#if _file_path not in sys.path:
    #sys.path.append(_file_path)    

import dispatchers
import dispatchers.maya


DISPATCHERS = [
    dispatchers.maya.MayaDispatch()
]

  
_ACTIVE_DISPATCHER : dispatchers.dispatcher.Dispatcher = None


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
    global DISPATCHERS

    if _ACTIVE_DISPATCHER is None or not _ACTIVE_DISPATCHER.owns_process(process):
        _ACTIVE_DISPATCHER = None
        
        for dis in DISPATCHERS:
            if dis.owns_process(process):  
                _ACTIVE_DISPATCHER = dis
                break
            
    #we'll always the last active dispatcher at the top of our dispatcher list
    if _ACTIVE_DISPATCHER and DISPATCHERS[0] !=  _ACTIVE_DISPATCHER:
        idx = DISPATCHERS.index(_ACTIVE_DISPATCHER)
        DISPATCHERS.pop(idx)
        DISPATCHERS.insert(0, _ACTIVE_DISPATCHER)
                


def _find_best_process():
    valid_dispatchers = []
    
    for dis in DISPATCHERS:
        if dis.can_dispatch():
            valid_dispatchers.append(dis)
            
    if not valid_dispatchers:
        return None
    
    if len(valid_dispatchers) > 1:
        print("Mutliple dispatchers found. Using first one :{}".format(valid_dispatchers))
        
    return valid_dispatchers[0]



def _activate_by_process(process):
    global _ACTIVE_DISPATCHER
    """If we're actively debugging try to find the process owner"""
    #process = _get_debug_process()
    if process:
        _find_process_owner(process)
    else:
        _ACTIVE_DISPATCHER = None
        
        

def dispatch():
    global _ACTIVE_DISPATCHER
    if not _ACTIVE_DISPATCHER:
        #we dont' have an active dispatcher, so let's try to find one
        _ACTIVE_DISPATCHER = _find_best_process()
        
    
    if _ACTIVE_DISPATCHER is not None:
        highlighted_text, doc_type = _get_document_text()
        module_path, file_path = _get_module_info()
        file_path = file_path.replace("\\", "/")
        print('module path:{} full path:{}'.format(module_path, file_path))        
        
        _ACTIVE_DISPATCHER.dispatch(highlighted_text, module_path, file_path, doc_type)
    else:
        print("No application to dispatch to!")
        

      
def _get_debug_process(current_run_state=None) -> psutil.Process:
    if current_run_state is None:
        debugger = wingapi.gApplication.GetDebugger()
        current_run_state = debugger.GetCurrentRunState()

    if not current_run_state:
        print("no debug run state found")
        return
    
    pid = current_run_state.GetProcessID()
    process: psutil.Process = psutil.Process(pid=pid)
    print('connected to PID:{}    name:{}    exe:{}'.format(process.pid, process.name(), process.exe()))

    return process
        
        
        
def _debugger_connected(*args, **kwargs):
    print("callback connected")
    print(args)
    
    if args:
        process = _get_debug_process(args[0])
        _activate_by_process(process)


    
def _debugger_changed(*args, **kwargs):
    if not args:
        _activate_by_process(None)
    
    print('current-runstate-changed')
    print("callback changed")
    print(args)
    print(kwargs)
        
        
        
print("Connecting signals")
debugger = wingapi.gApplication.GetDebugger()
debugger.Connect('new-runstate', _debugger_connected)
debugger.Connect('current-runstate-changed', _debugger_changed)
