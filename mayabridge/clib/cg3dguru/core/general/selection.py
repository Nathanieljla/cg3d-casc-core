
import csc
import common.selection_operations as so

from . import scene


def print_behavior_names(behaviour_viewer, guids):
    for guid in guids:
        print(behaviour_viewer.get_behaviour_name(guid))
           
    
    
def run():
    #Rename and parent object
    current_scene = scene.get_current_scene()
    print(current_scene.get_animation_size())
    
    results = scene.get_scene_objects(names=['sphere', 'plane'])
    if results:
        parent = results[0].parent
        
        if parent is None:
            results[0].parent = results[1]
        else:
            results[0].parent = None
            
        #results[0].name = "New Name"        
    
        #basic = results[0].Basic
        #basic.parent.set(results[1])
        
        #results[0].parent = results[1]
        
        #results[0].parent = results[1]
    
    
    
    #results = scene.get_scene_objects(names=['SKM_Manny_Simple'])
    #if results:
        #mesh_objects = results[0].get_behaviours()
        #for b in mesh_objects:
            #print(b)
            
        #print(mesh_objects)
        
        #beh = results[0].MeshObject
        #results = beh.linked_objects.get()
        #for r in results:print(r.name)
    
    
        