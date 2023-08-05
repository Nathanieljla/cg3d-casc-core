
import csc

import cg3dguru.core.datatypes

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



def get_scene_objects(names = [], selected = False, of_type = ''):
    def _get_by_name(model_viwer, names):
        found_guids = []
        if names:
            for name in names:
                result = model_viewer.get_objects(name)
                if result:
                    found_guids.append(result[0])
                    
        return found_guids
    
    
    current_scene = get_current_scene()
    domain_scene = current_scene.domain_scene()
    model_viewer = domain_scene.model_viewer()
    name_list = []
    
    if selected:
        object_ids = domain_scene.selector().selected().ids
        if names:
            name_list = _get_by_name(model_viewer, names)
    elif names:
        object_ids = _get_by_name(model_viewer, names)
    else:
        object_ids = model_viewer.get_objects()

    
    if name_list:
        set_a = set(name_list)
        set_b = set(object_ids)
        
        set_b.intersection_update(set_a)
        object_ids = list(set_b)
        
        
    if of_type:
        object_ids = [guid for guid in object_ids if model_viewer.get_object_type_name(guid) == of_type]
        
        
    return [cg3dguru.core.datatypes.PyObject(guid, current_scene) for guid in object_ids]
    