from __future__ import annotations #used so I don't have to forward declare classes for type hints

from enum import Enum

import csc


################
###---Exceptions
################

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
        
        
        
class AttrError(Exception):
    """Thrown when a PyBehaviour doesn't have a attribute of a given name
    
    If PySettings.attribute_name doesn't exist, this will be thrown.
    """
    
    def __init__(self, behaviour_name, attr_name, message=''):
        if not message:
            message = "Can't find attribute named:{} in behaviour {}".format(attr_name, behaviour_name)
            
        super().__init__(message)



#################
####---Classes---
#################



class CscWrapper(object):
    def __init__(self, data, container, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if isinstance(data, CscWrapper):
            data = data.unwrap()
        
        self._data = data
        self._container = container
        
        
    def __repr__(self):
        return "{}: {}".format(self.__class__.__name__, self._data.__class__.__name__)

    
    def __eq__(self, other):
        if isinstance(other, CscWrapper):
            return ((self._data == other._data))
        else:
            return False
        
        
    def __hash__(self):
        return self._data.__hash__()
    
    
    def __getattr__(self, attr):
        if hasattr(self._data, attr):
            def func_wrapper(*args, **kwargs):
                args = self.unwrap_list(args)
                CscWrapper.unwrap_dict(kwargs)
                
                func = getattr(self._data, attr)
                result = func(*args, **kwargs)
                
                return self._wrap_result(result)
                
            return func_wrapper
        
        raise AttributeError(attr)
    
                
    @staticmethod
    def unwrap_list(in_list):
        """Replace all CscWrappers elements with their csc_handle"""
        
        if isinstance(in_list, tuple):
            in_list = list(in_list)
        
        return [value.unwrap() if isinstance(value, CscWrapper) else value for value in in_list]
    
    
    @staticmethod
    def unwrap_dict(in_dict):
        for key, value in in_dict.items():
            if isinstance(value, CscWrapper):
                in_dict[key] = value.unwrap()
    
        
    @staticmethod
    def wrap(data: object, container: object) -> CscWrapper:
        """Takes the data and returns an instance of CscWrapper
        
        Argg:
            data: The data to wrap
            container: The owner of the data. None is a valid value.
        """
        
        #guidIds are resolved first
        if hasattr(data, 'is_null'):
            if data.is_null():
                return None
            elif isinstance(data, csc.model.ObjectId):
                return PyObject(data, container)
            elif isinstance(data, csc.model.DataId):
                return AttrData('', data, container)
            elif isinstance(data, csc.Guid):
                if isinstance(container, GuidMapper) and container.guid_class is not None:
                    return container.guid_class(data, container)
                else:
                    return PyGuid(data, container)  
            else:
                #can't wrap this with anything
                print("Can't wrap:{}".format(data))
                return data        
        
        #if we don't have a guid let's see if this is another type of csc object.
        elif isinstance(data, csc.view.Scene):
            return PyScene(data, container)
        elif isinstance(data, csc.domain.Scene):
            return DomainScene(data, container)
        elif isinstance(data, csc.model.BehaviourViewer):
            return BehaviourViewer(data, container)
        elif isinstance(data, csc.model.ModelViewer):
            return ModelViewer(data, container)
        elif isinstance(data, csc.model.DataViewer):
            return DataViewer(data, container)
        elif isinstance(data, csc.layers.Viewer):
            return LayersViewer(data, container)
        else:
            #can't wrap this with anything
            print("Can't wrap:{}".format(data.__class__))
            return data
        
        
    @property
    def container(self):
        return self._container
    
    
    def replace_data(self, data):
        """Directly replace the underlying content that is wrapped"""
        self._data = data
   
              
    def unwrap(self):
        return self._data
                       
               
    def _wrap(self, csc_handle):
        return self.wrap(csc_handle, self)
    
    
    def _wrap_result(self, result: object):
        if hasattr(result, 'is_null') and result.is_null():
            return None
        
        if isinstance(result, list) or isinstance(result, tuple):
            return [CscWrapper.wrap(value, self) for value in result]
        else:
            return CscWrapper.wrap(result, self)



    
    

class SceneRoot(CscWrapper):
    """Base class used to represent any wrapped data existing/related to a scene
    
    Used to share global scene access between scene data-specific classes.
    The csc viewers and editors need to be instanced in context to the
    current scene. Scene objects need these viewers and editors is commmon
    among any datatypes.classes that represent data within a scene. This
    class provides easy access of this data via the self.root member
    variable.
    """
    
    def __init__(self, *args, **kwargs):
        super(SceneRoot, self).__init__(*args, **kwargs)
        
        self._root: PyScene = None
        """Used to quickly access the PyScene that holds any sub-class data"""
        
        if self.container is not None:
            if isinstance(self.container, SceneRoot):
                self._root = self.container.scene
            else:
                #I'm not sure if this case is ever valid, so we'll raise an error for now.
                raise TypeError("{} is not an instance of SceneRoot".format(self.container))
            
            
    @property
    def scene(self):
        """Returns the view.Scene"""
        return self._root
    
    
    @property
    def dom_scene(self):
        """Returns the domain.Scene"""
        #this property name is abbreviated to avoid conflicts with the csc
        #api function name domain_scene.        
        return self._root.ds
    
    @property
    def mod_viewer(self):
        """Returns the ModelViewer"""
        #this property name is abbreviated to avoid conflicts with the csc
        #api function name model_viewer.
        
        return self._root.mv
    
    @property
    def beh_viewer(self):
        """Returns the BehaviourViewer"""
        #this property name is abbreviated to avoid conflicts with the csc
        #api function name behaviour_viewer.        
        return self._root.bv
    
    @property
    def dat_viewer(self):
        """Returns the DataViewer"""
        #this property name is abbreviated to avoid conflicts with the csc
        #api function name data_viewer.
        return self._root.dv   
    
    
    
class PyScene(SceneRoot):
    """Represents a csc.view.Scene and all the scene's viewers and editors"""
    
    def __init__(self, *args, **kwargs):
        super(PyScene, self).__init__(*args, **kwargs)
        self._root = self
        self.ds = self.domain_scene()
        
        self.mv = self.ds.model_viewer()
        self.bv = self.ds.behaviour_viewer()
        self.dv = self.ds.data_viewer()
        
        self.me = None
        self.be = None
        self.dv = None
                  
        
        
class PyGuid(SceneRoot):
    """Base class for wrappping csc.Guid and all Ids"""

    
    def __init__(self, *args, **kwargs):
        #call objects.__init__ so it plays nice with mixins
        super(PyGuid, self).__init__(*args, **kwargs)
        


class PyObject(PyGuid):
    """Wrapper around ccs.model.ObjectId"""

        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._behaviours_cache = {}
        
        
    def __str__(self):
        #return "{}->{} : {}-> {}".format(self.__class__.__name__, self.name, self.csc_handle.__class__.__name__, self.csc_handle.to_string())
        guid = ''
        if self._data:
            guid = self._data.to_string()
        
        return "{}->{}->{}".format(self.__class__.__name__, self.name, guid)
        

    def __getattr__(self, attr):
        return getattr(self._data, attr)

    
    @property
    def name(self):
        """The name of the object"""
        return self.mod_viewer.get_object_name(self)
    
    
    @name.setter
    def name(self, value):
        pass
        #def mod(model_editor, update_editor, scene_updater):
            #model_editor.set_object_name(self.csc_handle, value)
        
        #self.domain_scene.modify_update("Rename {}".format(self.name), mod)
        
        
    @property
    def children(self):
        """Returns a list of children parented to the current model"""
        return self.beh_viewer.get_children(self)
    
    
    @property
    def parent(self):
        return self.Basic.parent.get() #self.Basic.parent.get()  #self.behaviour_viewer.get_behaviour_object(self.basic.guid, 'parent')
    
    
    @parent.setter
    def parent(self, value):
        self.Basic.parent.set(value)
    
        
    def __getattr__(self, attr):
        #try:
            #return super().__getattribute__(attr) #getattr(super(), attr)
        #except AttributeError: 
            #behaviours = self.get_behaviours_by_name(attr)
            #if not behaviours:
                #raise BehaviourError(attr)   
            #elif len(behaviours) > 1:
                #raise BehaviourSizeError(self.name, attr)
        
        #return behaviours[0]        
        
        behaviours = self.get_behaviours_by_name(attr)
        if not behaviours:
            try:
                return super().__getattr__(attr)
            except AttributeError: 
                raise BehaviourError(attr)
        elif len(behaviours) > 1:
            raise BehaviourSizeError(self.name, attr)
        
        return behaviours[0]
    
    
    def _cache_behaviours(self):
        self._behaviours_cache = {}
        
        behaviours = self.beh_viewer.get_behaviours(self)
        for behaviour in behaviours:
            if behaviour.name in self._behaviours_cache:
                self._behaviours_cache[behaviour.name].append(behaviour)
            else:
                self._behaviours_cache[behaviour.name] = [behaviour]        

            
    def has_behaviour(self, behaviour_name) -> bool:
        """Returns true if a behaviour of the given name exists
        
        If a requested behaviour is missing the internal behaviour cache is
        rebuild before validating the missing data.
        """
        
        if behaviour_name not in self._behaviours_cache:
            self._cache_behaviours()
            
        return behaviour_name in self._behaviours_cache
    
    
    def get_behaviours_by_name(self, behaviour_name) -> list:
        """Returns a list of all the behaviours that match the input name"""
        
        if self.has_behaviour(behaviour_name):
            return self._behaviours_cache[behaviour_name]
        
        return []
        


class Settings(object):
    """Used to access behaviour attributes of type settings"""
    
    def __init__(self, behaviour: PyBehaviour, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.behaviour = behaviour
        
    def __getattr__(self, attr):
        try:
            data_id = self.behaviour_viewer.get_behaviour_setting(self.behaviour._data, attr)
            return AttrSettings(attr, data_id, self)
        except:
            raise AttrError(self.behaviour.name, attr)      



class PyBehaviour(PyGuid):
    """A wrapper for Cascadeur Behaviours"""
    
    def __init__(self, *args, **kwargs):
        super(PyBehaviour, self).__init__(*args, **kwargs)
            
        self.name, self.is_dynamic = self.get_behaviour_name(self, self.beh_viewer, self.mod_viewer)
        self._settings = None
        
        
    @property
    def settings(self):
        if self._settings is None:
            self._settings =  Settings(self)
        
        return self._settings
            
    @property
    def object(self):
        return self.container
    
    
    @staticmethod
    def get_behaviour_name(behaviour_id: PyGuid, b_viewer: BehaviourViewer, m_viewer: DataViewer):
        """Returns a tuple of the behaviour name and if the behaviour is Dynamic"""
        
        name = b_viewer.get_behaviour_name(behaviour_id)
        
        is_dynamic = name == 'Dynamic'
        if is_dynamic:
            data_attr = b_viewer.get_behaviour_data(behaviour_id, 'behaviourName')
            data_attr.name = 'behaviourName'
            name = m_viewer.get_data_value(data_attr)
            
        return (name, is_dynamic)
    
    
    def _get_data(self, attr):
        try:
            dat_attr = self.beh_viewer.get_behaviour_data(self, attr)
            dat_attr.name = attr
            return dat_attr
        except:
            return None
        
        
    def _get_object(self, attr):
        try:
            result_object = self.beh_viewer.get_behaviour_object(self, attr)
            return AttrObject(attr, result_object, self)
        except:
            return None
        
        
    def _get_reference(self, attr):
        try:
            result_ref = self.beh_viewer.get_behaviour_reference(self, attr)
            return AttrRef(attr, result_ref, self)
        except:
            return None
            
            
    def __getattr__(self, attr):
        if hasattr(self.beh_viewer, attr):
            return getattr(self.beh_viewer, attr)
        
        result = self._get_data(attr)
        if result:
            return result
        
        result = self._get_object(attr)
        if result:
            return result
        
        result = self._get_reference(attr)
        if result:
            return result
        
        raise AttrError(self.name, attr)
    

    
    
    
    
class PyLayer(PyGuid):
    def __init__(self, *args, **kwargs):
        super(PyLayer, self).__init__(*args, **kwargs)
        
    
    
class Attr(PyGuid):
    """Base class for any Behaviour attribute"""
    
    def __init__(self, name, *args, **kwargs):
        #args = list(args)
        self._name = name
        
        super(Attr, self).__init__(*args, **kwargs)

        
        
    def get(self):
        """get the data associated with the attribute"""
        
        raise NotImplementedError
    
    
    def set(self):
        """set the data associated with the atttribute"""
        
        raise NotImplementedError
    

    @property
    def name(self):
        return self._name
    
    
    @name.setter
    def name(self, name):
        self._name = name


    @property
    def behaviour(self):
        return self.container
    
   
  
class AttrData(Attr):
    """Wrapper around ccs.model.DataId that are part of a behaviour"""
    
    def __init__(self, *args, **kwargs): #name: str, attr_type: AttrType, guid: csc.model.DataId, behaviour: PyBehaviour):
        super(AttrData, self).__init__( *args, **kwargs) #name, attr_type, guid, behaviour)    

        #TODO: will a data guid always safely return data?
        try:
            self._data = self.dat_viewer.get_data(self.unwrap())
        except:
            self._data = None
            
    
    def is_animateable(self):
        return self._data is not None and self._data.mode == csc.model.DataMode.Animation
    
    
    def get(self, frame = -1):
        if self.is_animateable():
            if frame < 0:
                frame = self.domain_scene.get_current_frame()
                
            return self.dat_viewer.get_data_value(self._data, frame) 
        else:
            return self.dat_viewer.get_data_value(self._data)
        
        
    #def set(self, value):
        
        
        
class AttrObject(Attr):
    """Represents behaviour data that maps to objects"""
        
    def __init__(self, *args, **kwargs):
        super(AttrObject, self).__init__( *args, **kwargs)


    def get(self):
        if self._data is None:
            return None
        
        return PyObject(self._data, self.scene)
        
        #if not self.csc_handle.is_null():
            #return PyObject(self.csc_handle, self.root)
        
        #return None
    
    
    #def set(self, value: PyGuid):
        #if value is None:
            #value = PyGuid(csc.model.ObjectId.null(), None)
        
        #def mod(model_editor, update_editor, scene_updater):
            #model_editor.behaviour_editor().set_behaviour_model_object(self.behaviour.csc_handle, self.name, value.csc_handle)
        
        #self.domain_scene.modify_update("Set {}.{}".format(self.behaviour.name, self.name), mod)        
    
    
    
class AttrRef(Attr):
    """Represents behaviour data that stores references to other behaviours"""
    
    def __init__(self, *args, **kwargs):
        super(AttrRef, self).__init__( *args, **kwargs)


    def get(self):
        pass
        #if not self.csc_handle.is_null():
            #name, is_dynamic = PyObject.get_behaviour_name(self.csc_handle, self.behaviour_viewer, self.data_viewer)
                        
            #return PyBehaviour(name, is_dynamic, self.csc_handle, self.behaviour.get_behaviour_owner(self.csc_handle))

    
    
class AttrSettings(Attr):
    """Represents behaviour data that's stored in the settings"""
    
    def __init__(self, *args, **kwargs):
        super(AttrSettings, self).__init__( *args, **kwargs)


    def get(self):
        return self.dat_viewer.get_setting_value(self)
    
    
    
class GuidMapper(SceneRoot):
    """Used to wrap a generic csc.Guid to a specific class"""
    guid_class = None    

          
class LayersViewer(GuidMapper):
    guid_class = PyLayer
    
        
class BehaviourViewer(GuidMapper):
    guid_class = PyBehaviour
       
        
class ModelViewer(GuidMapper):
    guid_class = PyBehaviour
          
        
class DataViewer(GuidMapper):
    guid_class = PyBehaviour
        

class DomainScene(GuidMapper):
    guid_class = PyBehaviour
    
        
        
        
        
    
