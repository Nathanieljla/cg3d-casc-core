
import csc
import common.selection_operations as so

from . import scene


def print_behavior_names(behaviour_viewer, guids):
    for guid in guids:
        print(behaviour_viewer.get_behaviour_name(guid))
           
    

def run():
    print("here")
    results = scene.get_scene_objects(names=['sphere', 'plane'])
    
    if results:
        basic = results[0].Basic
        attr = basic.parent
        print(attr)
        
        results[0].parent = results[1]
        results[0].name = "New Name"
    
    
        