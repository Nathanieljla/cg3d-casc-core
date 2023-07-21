
import csc

def new_scene():
    """Creates a new scene and makes it the active scene
    
    Returns:
        csc.View.Scene
    """
    scene_manager = csc.app.get_application().get_scene_manager()    
    application_scene = scene_manager.create_application_scene()
    scene_manager.set_current_scene(application_scene)
    
    return application_scene


def get_current_scene():
    """Get the current scene"""
    scene_manager = csc.app.get_application().get_scene_manager()
    return scene_manager.current_scene()
    