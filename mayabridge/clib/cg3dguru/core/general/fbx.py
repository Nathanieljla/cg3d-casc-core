import csc
from . import scene

def import_fbx_model(file_path, new_scene=False):
    if new_scene:
        scene.new_scene()
        
    current_scene = scene.get_current_scene()
    
    tools_manager = csc.app.get_application().get_tools_manager()
    fbx_scene_loader = tools_manager.get_tool("FbxSceneLoader").get_fbx_loader(current_scene)
    fbx_scene_loader.import_model(file_path)