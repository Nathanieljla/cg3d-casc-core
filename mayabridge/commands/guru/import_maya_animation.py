

import os
import csc
import json

import cg3dguru.maya.core
import cg3dguru.core


def command_name():
    return "Guru.Maya.Import Animation"


def run(scene):
    #command_args = cg3dguru.maya.core.get_temp_commmand_filename()
    #if os.path.exists(command_args):
        #f = open(command_args)
        #data = json.load(f)
        #f.close()
        #args = data['args']
        #kwargs = data['kwargs']
    
    cg3dguru.maya.core.import_maya_fbx_animation() #**kwargs)