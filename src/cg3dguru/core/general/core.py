from __future__ import annotations #used so type hints are resolved after all content is read
import typing

import csc

import cg3dguru.core.datatypes

def new_scene() -> cg3dguru.core.datatypes.PyScene:
    """Creates a new scene and makes it the active scene
    
    Returns:
        csc.View.Scene
    """
    scene_manager = csc.app.get_application().get_scene_manager()    
    application_scene = scene_manager.create_application_scene()
    scene_manager.set_current_scene(application_scene)
    
    return cg3dguru.core.datatypes.PyScene.wrap(application_scene, None)



def get_current_scene() -> cg3dguru.core.datatypes.PyScene:
    """Get the current scene"""
    scene_manager = csc.app.get_application().get_scene_manager()
    scene = scene_manager.current_scene()
    
    return cg3dguru.core.datatypes.PyScene.wrap(scene, None)



def get_scene_objects(names = [], selected = False, of_type = '', only_roots = False) -> typing.List[cg3dguru.datatypes.PyObject]:
    current_scene = get_current_scene()
    return current_scene.get_scene_objects(names, selected, of_type, only_roots)

    #def _get_by_name(model_viewer, names):
        #found_guids = []
        #if names:
            #for name in names:
                #result = model_viewer.get_objects(name)
                #if result:
                    #found_guids.append(result[0])
                    
        #return found_guids
    
    
    #current_scene = get_current_scene()    
    #domain_scene = current_scene.dom_scene
    #model_viewer = domain_scene.mod_viewer
    #name_list = []
    
    #if selected:
        #found_objects = domain_scene.selector().selected().ids
        #if names:
            #name_list = _get_by_name(model_viewer, names)
    #elif names:
        #found_objects = _get_by_name(model_viewer, names)
    #else:
        #found_objects = model_viewer.get_objects()

    
    #if name_list:
        #set_a = set(name_list)
        #set_b = set(found_objects)
        
        #set_b.intersection_update(set_a)
        #found_objects = list(set_b)
        
        
    #if of_type:
        #found_objects = [obj for obj in found_objects if model_viewer.get_object_type_name(obj) == of_type]
        
    #if only_roots:
        #found_objects = [obj for obj in found_objects if obj.parent is None]
        
        
    #return found_objects
    