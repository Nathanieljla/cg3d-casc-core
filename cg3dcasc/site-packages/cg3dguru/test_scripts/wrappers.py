import csc
import cg3dguru.core
import cg3dguru.core.datatypes

scene = cg3dguru.core.get_current_scene()
objects = cg3dguru.core.get_scene_objects(selected=True)
if objects:
    try:
        
        apple = csc.Guid()
        print("Raw Guid")
        print("obj {}".format(apple))
        print("Hash {}".format(apple.__hash__()))
        
        wrapped = cg3dguru.core.datatypes.CscWrapper.wrap(apple, None)
        print("wrapped")
        print("obj {}".format(wrapped))
        print("Hash {}".format(wrapped.__hash__()))
        
        wrapped_2 = cg3dguru.core.datatypes.CscWrapper.wrap(apple, None)
        print("wrapped 2")
        print("obj {}".format(wrapped_2))
        print("Hash {}".format(wrapped_2.__hash__()))        
        
        
        print("Are the same : {}".format(wrapped_2 == wrapped))
        
        
        set1 = set([wrapped])
        set2 = set([wrapped_2])
        
        set1.difference_update(set2)
        print (set1)
        
        
        #print(objects[0].parent)
        #print(objects[0].name)
        #basic = objects[0].Basic
        #attr = basic.joint
        #print('Attr is {}'.format(attr.__class__.__name__))
        #attr = objects[0].parent
        #print(attr.__class__)
    except Exception as e:
        print('Exception {}'.format(e))