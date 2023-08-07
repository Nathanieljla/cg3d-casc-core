
import csc
import common.selection_operations as so

from . import scene


def print_behavior_names(behaviour_viewer, guids):
    for guid in guids:
        print(behaviour_viewer.get_behaviour_name(guid))
           
    


def run():
    results = scene.get_scene_objects(names=['sphere', 'plane'])
    results_2 = scene.get_scene_objects(names=['sphere', 'plane'])
    
    
    
    #result = results[0].RigAdditionalInfo.joint.get()
    print(results)
    print(results[0].parent)
    print(results[0])
    results[1].parent = None #results[1]
    
    print(results)
    
    #selected = scene.get_scene_objects(selected=True, of_type='')
    #selected_A = scene.get_scene_objects(selected=True, of_type='')
    
    #if not selected:
        #print("select something")
        #return
    
    #print (selected[0].guid == selected_A[0].guid)
    #print (selected[0].guid is selected_A[0].guid)  
    #selected[0].name = 'howard'
    
    #basic = selected[0].Basic
    
    #print("visibility:{}".format(basic.visibility.get_value()))
    
    
        