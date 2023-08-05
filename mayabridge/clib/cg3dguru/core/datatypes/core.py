
import csc



class PyGuid(object):
    #_instances = {}
    
    #def __new__(cls, guid, context):
        #if guid not in cls._instances:
            #instance = super().__new__(cls) #, guid, context)
            #cls._instances[guid] = instance
            
        #return cls._instances[guid]
        
        
    def __init__(self, guid, context):
        self.guid = guid
        self._context = context

        
    @classmethod
    def get_instance(cls, guid):
        if guid in cls._instances:
            return cls._instances[guid]
        
        return None
    

    @classmethod
    def flush_instances(cls):
        cls._instances = {}
        
        
        
class PyBehaviour(PyGuid):
    pass


class BehaviourError(Exception):
    pass


class PyObject(PyGuid):
    """Wrapper around ccs.model.ObjectId"""
    
    def __init__(self, guid: csc.model.ObjectId, scene: csc.view.Scene):
        super(PyObject, self).__init__(guid, scene)
        
        self.domain_scene = self.scene.domain_scene()
        self.model_viewer = self.domain_scene.model_viewer()
        self.behaviour_viewer =self.domain_scene.behaviour_viewer()
        self.data_viewer = self.domain_scene.data_viewer()
        
        self._behaviours_cache = {}
        
        
    @property
    def scene(self):
        """The view.Scene for this model"""
        return self._context
    
    
    @property
    def name(self):
        """The name of the object"""
        return self.model_viewer.get_object_name(self.guid)
    
    
    @name.setter
    def name(self, value):
        def mod(model_editor, update_editor, scene_updater):
            model_editor.set_object_name(self.guid, value)
        
        self.domain_scene.modify_update("Rename {}".format(self.name), mod)
        
        
    @property
    def children(self):
        """Returns a list of children parented to the current model"""
        return self.behaviour_viewer.get_children(self.guid)
        
    
    def __getattr__(self, attr):
        behaviour = self.get_behaviour(attr)
        if behaviour is not None:
            return behaviour
        
        raise BehaviourError(attr)
    
    
    def _cache_behaviours(self):
        self._behaviours_cache = {}
        
        behaviours = self.behaviour_viewer.get_behaviours(self.guid)
        for guid in behaviours:
            name = self.behaviour_viewer.get_behaviour_name(guid)
            behaviour = PyBehaviour(guid, self)
            self._behaviours_cache[name] = behaviour
            self._behaviours_cache[name.lower()] = behaviour
      
            
    def has_behaviour(self, behaviour_name) -> bool:
        """Returns true if a behaviour of the given name exists"""
        
        if behaviour_name not in self._behaviours_cache:
            self._cache_behaviours()
            
        return behaviour_name in self._behaviours_cache
    
    
    def get_behaviour(self, behaviour_name) -> PyBehaviour | None:
        """Returns the behaviour of a given name if it exists"""
        
        if self.has_behaviour(behaviour_name):
            return self._behaviours_cache[behaviour_name]
        
        return None
        


class BehaviourError(Exception):
    """Thrown when a PyObject doesn't have a behaviour of a given name"""
    
    def __init__(self, behaviour_name, message=''):
        if not message:
            message = "Can't find behaviour {}".format(behaviour_name)
            
        super().__init__(message)


        
class PyBehaviour(PyGuid):
    """A wrapper for Cascadeur behaviours"""
    
    def __init__(self, guid: csc.Guid, model: PyObject):
        super(PyBehaviour, self).__init__(guid, model)

        
    @property
    def model(self):
        return self._context
    
    
    def __getattr__(self, attr):
        data_id = self.model.behaviour_viewer.get_behaviour_data(self.guid, attr)
        
        return PyData(data_id, self)
        
        

class PyData(PyGuid):
    """Wrapper around ccs.model.DataId that are part of a behaviour"""
    
    def __init__(self, guid: csc.model.DataId, behaviour: PyBehaviour):
        super(PyData, self).__init__(guid, behaviour)
        
        
    @property
    def behaviour(self):
        return self._context
    
    
    def get_value(self, frame = -1):
        if frame < 0:
            frame = self.behaviour.model.domain_scene.get_current_frame()
        
        return self.behaviour.model.data_viewer.get_data_value(self.guid, frame)


