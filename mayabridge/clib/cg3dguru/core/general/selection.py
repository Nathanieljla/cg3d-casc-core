
import csc
import common.selection_operations as so

from . import scene


def print_behavior_names(behaviour_viewer, guids):
    for guid in guids:
        print(behaviour_viewer.get_behaviour_name(guid))
           
    

def run():
    print("here")
    
    
    ##Rename and parent object
    #results = scene.get_scene_objects(names=['pelvis_Box', 'plane'])
    #if results:
        #beh = results[0].RigAdditionalInfo
        #attr = beh.joint
        #print(attr)
        
        #results[0].parent = results[1]
        #results[0].name = "New Name"        
    
    
    
    results = scene.get_scene_objects(names=['SKM_Manny_Simple'])
    if results:
        mesh_objects = results[0].get_behaviours()
        for b in mesh_objects:
            print(b)
            
        print(mesh_objects)
        
        beh = results[0].MeshObject
        results = beh.linked_objects.get()
        for r in results:print(r.name)
    
    
        