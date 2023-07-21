
import os
import csc

import cg3dguru.maya.core
import cg3dguru.core


def command_name():
    return "Guru.Maya.Import model"


def run(scene):
    imported = cg3dguru.maya.core.import_maya_fbx_file()
    if imported:
        cg3dguru.maya.core.import_maya_qrig_file()