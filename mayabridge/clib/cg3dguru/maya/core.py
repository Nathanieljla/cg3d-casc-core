
import tempfile
import os

import csc
import rig_mode.on as rm_on
import rig_mode.off as rm_off

import cg3dguru.core

def get_temp_qrig_filename():
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'hik_to_.qrigcasc')
    
    return file_path


def get_temp_fbx_filename():
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'maya_to_casc.fbx')
    
    return file_path


def get_temp_commmand_filename():
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, 'csc_command_args.json')

    return file_path


def import_maya_qrig_file():
    file_path =  get_temp_qrig_filename()
    
    if not os.path.exists(file_path):
        print('MAYA IMPORT : No qrig file to import.')
        return
    
    scene_manager = csc.app.get_application().get_scene_manager()
    application_scene = scene_manager.current_scene()
    rm_on.run_raw(application_scene.domain_scene(), [0.0, 0.5, 0.0])
    rig_tool = csc.app.get_application().get_tools_manager().get_tool('RiggingToolWindowTool').editor(application_scene)
    rig_tool.open_quick_rigging_tool()
    rig_tool.load_template_by_fileName(file_path)
    rig_tool.generate_rig_elements()
    

def import_maya_fbx_file(new_scene=False, *args, **kwargs):
    fbx_file = get_temp_fbx_filename()
    if not os.path.exists(fbx_file):
        print('No FBX file found')
        return False
    
    #if new_scene:
        #cg3dguru.core.new_scene()
    
    cg3dguru.core.import_fbx_model(fbx_file, new_scene)
    
    return True
    
    
    
def run(*args, **kwargs):
    print("Run function called")
    
  
  
print('core imported')  
    
#if __name__ == '__main__':
    #print("Importing")
    #import_fbx_file()