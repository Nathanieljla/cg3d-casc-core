from enum import Enum

import csc




class CscWrapper(object):
    def __init__(self, viewer):
        super().__init__()
        
        self._viewer = viewer
        
        
    @staticmethod
    def _class_to_guid(input_args):
        arg_list = list(input_args)
        
        return [value.guid if isinstance(value, PyGuid) else value for value in arg_list]
    
    
    #@staticmethod
    #def _guid_to_class(value):
        #pass
    
    
    #@staticmethod
    #def _convert_result(result):
        #if isinstance(result, csc.Guid):
            #if result.is_null():
                #return None
            #else:
                #return CscWrapper._guid_to_class(result)
        

    def __getattr__(self, attr):
        if hasattr(self._viewer, attr):
            def func_wrapper(*args, **kwargs):
                args = CscWrapper._class_to_guid(args)
                func = getattr(self._viewer, attr)
                #result = func(*args, **kwargs)
                #return CscWrapper._convert_result(result)
                return func(*args, **kwargs)
                
            return func_wrapper
        
        return AttributeError(attr)



class PyGuid(object):
    """Base class for wrappping csc.Guid and all sub-classes"""
    
    def __init__(self, guid, context, *args, **kwargs):
        #call objects.__init__ so it plays nice with mixins
        super(PyGuid, self).__init__(*args, **kwargs)
        
        self.guid = guid
        self._context = context

    def __repr__(self):
        return "{}: {}-> {}".format(self.__class__.__name__, self.guid.__class__.__name__, self.guid.to_string())
        
        
    def __hash__(self):
        return hash(self.__repr__())
        
        
    def __eq__(self, other):
        if isinstance(other, PyGuid):
            return ((self.guid == other.guid))
        else:
            return False
        
    
    def __getattr__(self, attr):
        if hasattr(self.guid, attr):
            return getattr(self.guid, attr)
        
        raise AttributeError(attr)   
    
    
    
class PyBehaviour(PyGuid):
    #declared here so PyObject can reference it.
    #re-declared below PyObject
    pass



class BehaviourError(Exception):
    """Thrown when a PyObject doesn't have a behaviour of a given name
    
    If code uses the shorthand of object.behaviour_name and the behaviour
    doesn't exist, this error will be thrown.
    """
    
    def __init__(self, behaviour_name, message=''):
        if not message:
            message = "Can't find behaviour {}".format(behaviour_name)
            
        super().__init__(message)
        
        
        
class BehaviourSizeError(Exception):
    """Thrown when a only one behaviour of a given type should exist
    
    If code uses the shorthand of object.behaviour_name and more than one
    behaviour of the given name exists, this error will be thrown.
    
    In these cases code should probably be refactored to call
    object.get_behaviours(behaviour_name) instead. This allows users to
    examine and determine the right instance to use.
    """
    
    def __init__(self, object_name, behaviour_name, message=''):
        if not message:
            message = "{0}.{1} ERRORs, because more than one behaviour exists. Try {0}.get_behaviours('{1}')[0] instead.".format(object_name, behaviour_name)
            
        super().__init__(message)



class SceneInterface(object):
    """A common set of methods for getting various viewers and scenes"""
    
    def __init__(self, *args, **kwargs):
        #call objects.__init__ so it plays nice with mixins
        super(SceneInterface, self).__init__(*args, **kwargs)    
    
    @property
    def scene(self):
        """Returns the view.Scene"""
        
        raise NotImplementedError
    
    @property
    def domain_scene(self):
        """Returns the domain.Scene"""
        
        raise NotImplementedError
    
    @property
    def model_viewer(self):
        """Returns the ModelViewer"""
        
        raise NotImplementedError
    
    @property
    def behaviour_viewer(self):
        """Returns the BehaviourViewer"""
        
        raise NotImplementedError
    
    @property
    def data_viewer(self):
        """Returns the DataViewer"""
        
        raise NotImplementedError        
    


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
    
    
    @property
    def parent(self):
        return self.Basic.parent.get()  #self.behaviour_viewer.get_behaviour_object(self.basic.guid, 'parent')
    
    
    @parent.setter
    def parent(self, value):
        self.Basic.parent.set(value)
    
    
    @staticmethod
    def get_behaviour_name(behaviour_id, b_viewer: csc.model.BehaviourViewer, m_viewer: csc.model.DataViewer):
        """Returns a tuple of the behaviour name and if the behaviour is Dynamic"""
        name = b_viewer.get_behaviour_name(behaviour_id)
        
        is_dynamic = name == 'Dynamic'
        if is_dynamic:
            data_guid = b_viewer.get_behaviour_data(behaviour_id, 'behaviourName')
            name = m_viewer.get_data_value(data_guid)
            
        return (name, is_dynamic)
    
    
    
    def __getattr__(self, attr):
        behaviours = self.get_behaviours(attr)
        if not behaviours:
            try:
                return super().__getattr__(attr)
            Exception: 
                raise BehaviourError(attr)
        elif len(behaviours) > 1:
            raise BehaviourSizeError(self.name, attr)
        
        return behaviours[0]
    
    
    def _cache_behaviours(self):
        self._behaviours_cache = {}
        
        behaviours = self.behaviour_viewer.get_behaviours(self.guid)
        for guid in behaviours:
            name, is_dynamic = self.get_behaviour_name(guid, self.behaviour_viewer, self.data_viewer)
     
            #name = self.behaviour_viewer.get_behaviour_name(guid)
            
            #is_dynamic = name == 'Dynamic'
            #if name == 'Dynamic':
                #data_guid = self.behaviour_viewer.get_behaviour_data(guid, 'behaviourName')
                #name = self.data_viewer.get_data_value(data_guid)
                    
            behaviour = PyBehaviour(name, is_dynamic, guid, self)
            if name in self._behaviours_cache:
                self._behaviours_cache[name].append(behaviour)
            else:
                self._behaviours_cache[name] = [behaviour]
      
            
    def has_behaviour(self, behaviour_name) -> bool:
        """Returns true if a behaviour of the given name exists
        
        If a requested behaviour is missing the internal behaviour cache is
        rebuild before validating the missing data.
        """
        
        if behaviour_name not in self._behaviours_cache:
            self._cache_behaviours()
            
        return behaviour_name in self._behaviours_cache
    
    
    def get_behaviours(self, behaviour_name) -> list:
        """Returns a list of all the behaviours that match the input name"""
        
        if self.has_behaviour(behaviour_name):
            return self._behaviours_cache[behaviour_name]
        
        return []
        


class AttributeError(Exception):
    """Thrown when a PyBehaviour doesn't have a attribute of a given name
    
    If PySettings.attribute_name doesn't exist, this will be thrown.
    """
    
    def __init__(self, behaviour_name, attr_name, message=''):
        if not message:
            message = "Can't find attribute named:{} in behaviour {}".format(attr_name, behaviour_name)
            
        super().__init__(message)



class PySettings(object):
    """Used to access behaviour attributes of type settings"""
    
    def __init__(self, behaviour: PyBehaviour, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.behaviour = behaviour
        
    def __getattr__(self, attr):
        try:
            data_id = self.behaviour_viewer.get_behaviour_setting(self.behaviour.guid, attr)
            return PyAttrSetting(attr, data_id, self)
        except:
            raise AttributeError(self.behaviour.name, attr)      



class PyBehaviour(PyGuid, SceneInterface):
    """A wrapper for Cascadeur Behaviours"""
    
    def __init__(self, name: str, is_dynamic: bool, guid: csc.Guid, model: PyObject):
        super(PyBehaviour, self).__init__(guid, model)
        
        self.is_dynamic = is_dynamic
        self.name = name
        self._settings = None
        
        
    @property
    def settings(self):
        if self._settings is None:
            self._settings =  PySettings(self)
        
        return self._settings
            
    @property
    def model(self):
        return self._context
    
    @property
    def scene(self):
        """The view.Scene for this model"""
        return self.model.scene
    
    @property
    def domain_scene(self):
        """Returns the domain.Scene"""
        
        return self.model.domain_scene
    
    @property
    def model_viewer(self):
        """Returns the ModelViewer"""
        
        return self.model.model_viewer
    
    @property
    def behaviour_viewer(self):
        """Returns the BehaviourViewer"""
        
        return self.model.behaviour_viewer
    
    @property
    def data_viewer(self):
        """Returns the DataViewer"""
        
        return self.model.data_viewer
    
    
    def _get_data(self, attr):
        try:
            data_id = self.behaviour_viewer.get_behaviour_data(self.guid, attr)
            return PyAttrData(attr, data_id, self)
        except:
            return None
        
        
    def _get_object(self, attr):
        try:
            object_id = self.behaviour_viewer.get_behaviour_object(self.guid, attr)
            return PyAttrObject(attr, object_id, self)
        except:
            return None
        
        
    def _get_reference(self, attr):
        try:
            ref_id = self.behaviour_viewer.get_behaviour_reference(self.guid, attr)
            return PyAttrRef(attr, ref_id, self)
        except:
            return None
            
            
    def __getattr__(self, attr):
        if hasattr(self.behaviour_viewer, attr):
            return getattr(self.behaviour_viewer, attr)
        
        result = self._get_data(attr)
        if result:
            return result
        
        result = self._get_object(attr)
        if result:
            return result
        
        result = self._get_reference(attr)
        if result:
            return result
        
        raise AttributeError(self.name, attr)      
        
    
    
class PyAttribute(PyGuid, SceneInterface):
    """Base class for any Behaviour attribute"""
    
    def __init__(self, name: str, *args, **kwargs):
        super(PyAttribute, self).__init__(*args, **kwargs)
        self._name = name
        
        
    def get(self):
        """get the data associated with the attribute"""
        
        raise NotImplementedError
    
    def set(self):
        """set the data associated with the atttribute"""
        
        raise NotImplementedError
    

    @property
    def name(self):
        return self._name

    @property
    def behaviour(self):
        return self._context
    
    @property
    def scene(self):
        """The view.Scene for this model"""
        return self.behaviour.model.scene
    
    @property
    def domain_scene(self):
        """Returns the domain.Scene"""
        
        return self.behaviour.model.domain_scene
    
    @property
    def model_viewer(self):
        """Returns the ModelViewer"""
        
        return self.behaviour.model.model_viewer
    
    @property
    def behaviour_viewer(self):
        """Returns the BehaviourViewer"""
        
        return self.behaviour.model.behaviour_viewer
    
    @property
    def data_viewer(self):
        """Returns the DataViewer"""
        
        return self.behaviour.data_viewer
   
  
    
class PyAttrData(PyAttribute):
    """Wrapper around ccs.model.DataId that are part of a behaviour"""
    
    def __init__(self, *args, **kwargs): #name: str, attr_type: AttrType, guid: csc.model.DataId, behaviour: PyBehaviour):
        super(PyAttrData, self).__init__( *args, **kwargs) #name, attr_type, guid, behaviour)    

        #TODO: will a data guid always safely return data?
        try:
            self._data = self.data_viewer.get_data(self.guid)
        except:
            self._data = None
            
    
    def is_animateable(self):
        return self._data is not None and self._data.mode == csc.model.DataMode.Animation
    
    
    def get(self, frame = -1):
        if self.is_animateable():
            if frame < 0:
                frame = self.domain_scene.get_current_frame()
                
            return self.data_viewer.get_data_value(self.guid, frame) 
        else:
            return self.data_viewer.get_data_value(self.guid)
        
        
    #def set(self, value):
        
        
        
class PyAttrObject(PyAttribute):
    """Represents behaviour data that maps to objects"""
        
    def __init__(self, *args, **kwargs):
        super(PyAttrObject, self).__init__( *args, **kwargs)


    def get(self):
        #object_id: csc.Guid = self.behaviour_viewer.get_behaviour_object(self.behaviour.guid, self.name)
        
        if not self.guid.is_null():
            return PyObject(self.guid, self.scene)
        
        return None
    
    
    def set(self, value: PyGuid):
        if value is None:
            value = PyGuid(csc.model.ObjectId.null(), None)
        
        def mod(model_editor, update_editor, scene_updater):
            model_editor.behaviour_editor().set_behaviour_model_object(self.behaviour.guid, self.name, value.guid)
        
        self.domain_scene.modify_update("Set {}.{}".format(self.behaviour.name, self.name), mod)        
    
    
    
class PyAttrRef(PyAttribute):
    """Represents behaviour data that stores references to other behaviours"""
    
    def __init__(self, *args, **kwargs):
        super(PyAttrRef, self).__init__( *args, **kwargs)


    def get(self):
        if not self.guid.is_null():
            name, is_dynamic = PyObject.get_behaviour_name(self.guid, self.behaviour_viewer, self.data_viewer)
                        
            return PyBehaviour(name, is_dynamic, self.guid, self.behaviour.get_behaviour_owner(self.guid))

    
    
    
class PyAttrSetting(PyAttribute):
    """Represents behaviour data that's stored in the settings"""
    
    def __init__(self, *args, **kwargs):
        super(PyAttrSetting, self).__init__( *args, **kwargs)


    def get(self):
        return self.data_viewer.get_setting_value(self.guid)