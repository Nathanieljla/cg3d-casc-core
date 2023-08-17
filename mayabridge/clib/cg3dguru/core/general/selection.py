
import csc
import common.selection_operations as so

from . import scene


def print_behavior_names(behaviour_viewer, guids):
    for guid in guids:
        print(behaviour_viewer.get_behaviour_name(guid))
       
        
        
        
def node_network(scene, *args, **kwargs):
    parent_object = None
    if args:
        parent_object = args[0]
        
    print(parent_object)
    if not parent_object:
        return
    
    node = scene.update_editor.get_node_by_id(parent_object)
    print(node)
    root_group = node.root_group()

            
    n1 = 'my_group'
    n2 = 'my_group_child'
    
    print(root_group)

            
    #object_node = scene.update_editor.create_object_node('this')
    #new_object = object_node.object_id()

    #if parent_object:
        #new_object.parent = parent_object
        
    #parent_group = object_node.parent_group()
    #for obj in parent_group.objects():
        #print(obj)
        #print(obj.name())
        
    #print(parent_group.is_root())
    
    
    #object_node.add_input('new input')
    #update_group = object_node.root_group()
    #sub_group = update_group.create_sub_update_group('new sub group') #, object_node.parent_group)
    #scene.scene_updater.generate_update()
    
    #print(sub_group)
    
    #sub_group = parent_group.create_sub_object_group('sub group')
    #scene.scene_updater.generate_update()
    #print("sub group class {}".format(sub_group.__class__.__name__))
    
    #group = parent_group.create_group('generic group')
    #scene.scene_updater.generate_update()
    #print("group class {}".format(group.__class__.__name__))
    
    
  
  
  
def dynamic_behaviour(scene):
    new_object = scene.create_object('MyObject')
    behaviour = new_object.add_behaviour('Dynamic', 'My Class', group_name='my_class_logic')
    behaviour_name = behaviour.behaviourName
    print(behaviour_name)
    
    #print(behaviour.name)
    
    
    #data_size_id = de.add_data(obj_id, 'Collision Box Size', csc.model.DataMode.Static, [100.0, 100.0, 100.0]).id
    #be.set_behaviour_data(beh_id, 'size', data_size_id)
    #data_active_id = de.add_data(obj_id, 'Collision Box Active', csc.model.DataMode.Animation, True).id
    #be.set_behaviour_data(beh_id, 'is_active', data_active_id)
    
    
def get_dynamic(scene):
    pass
    
        
       
def run():

    current_scene = scene.get_current_scene()
    
    
    
    objects = scene.get_scene_objects(names=['grand_parent'])
    #if objects:
        #beh = objects[0].get_behaviours_by_name('Dynamic')
    

    network = False
    if network:
        #objects = scene.get_scene_objects(names=['parent'])
        if objects:
            current_scene.edit("test", node_network, objects[0])
        else:
            current_scene.edit("test", node_network)
            
    else:
        current_scene.edit("Add dynamic behaviour", dynamic_behaviour)
        
    
    
    
    
    
    #results = scene.get_scene_objects(names=['sphere', 'plane'])
    #if results:
        #parent = results[0].parent
        
        #if parent is None:
            #results[0].parent = results[1]
        #else:
            #results[0].parent = None
            
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
    
    
        