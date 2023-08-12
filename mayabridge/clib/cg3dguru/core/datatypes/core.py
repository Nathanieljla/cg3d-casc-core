from __future__ import annotations #used so I don't have to forward declare classes for type hints

# https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html


from enum import Enum
import typing

import csc


################
###---Exceptions
################

class EditorError(Exception):
    """Thrown when someone attempts to access and editor at an invalid time
    
    The SceneElement properties 'mod_editor, 'beh_editor', 'dat_editor',
    'update_editor', scene_updater, and 'session' should only be accessed
    after SceneElement.edit has been called and inside of the assigned
    callback. Outside of this condition an error is raised.    
    """
    def __init__(self, editor_name, message=''):
        if not message:
            message = "{} can't be accessed outside of call to PyScene.edit".format(editor_name)
            
        super().__init__(message)
        
    

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
    object.get_behaviours_by_name(behaviour_name) instead. This programmers
    users to examine and determine the right instance to use.
    """
    
    def __init__(self, object_name, behaviour_name, message=''):
        if not message:
            message = "{0}.{1} ERRORs, because more than one behaviour exists. Try {0}.get_behaviours('{1}')[0] instead.".format(object_name, behaviour_name)
            
        super().__init__(message)
        
        
        
class PropertyError(Exception):
    """Thrown when a PyBehaviour doesn't have a property of a given name
    
    If PyBehaviour.attribute_name doesn't exist, this will be thrown.
    """
    
    def __init__(self, behaviour_name, attr_name, message=''):
        if not message:
            message = "Can't find attribute named:{} in behaviour {}".format(attr_name, behaviour_name)
            
        super().__init__(message)



#################
####---Classes---
#################


class CscWrapper(object):
    def __init__(self, data, creator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if isinstance(data, CscWrapper):
            data = data.unwrap()
        
        self.__data = data
        self.__creator = creator

         
    def __repr__(self):
        return "{}: {}".format(self.__class__.__name__, self.__data.__class__.__name__)

    
    def __eq__(self, other):
        if isinstance(other, CscWrapper):
            return ((self.__data == other.__data))
        else:
            return False
        
        
    def __hash__(self):
        return self.__data.__hash__()
    
    
    def __getattr__(self, attr):
        if hasattr(self.__data, attr):
            def func_wrapper(*args, **kwargs):
                args = self.unwrap_list(args)
                CscWrapper.unwrap_dict(kwargs)
                
                func = getattr(self.__data, attr)
                result = func(*args, **kwargs)
                
                return self._wrap_result(result)
                
            return func_wrapper
        
        raise AttributeError(attr)
    
                
    @staticmethod
    def unwrap_list(in_list):
        """Replace all CscWrappers elements with their underlying data"""
        
        if isinstance(in_list, tuple):
            in_list = list(in_list)
        
        return [value.unwrap() if isinstance(value, CscWrapper) else value for value in in_list]
    
    
    @staticmethod
    def unwrap_dict(in_dict):
        """Replace all CscWrappers elements with their underlying data"""
        for key, value in in_dict.items():
            if isinstance(value, CscWrapper):
                in_dict[key] = value.unwrap()
    
        
    @staticmethod
    def wrap(data: object, creator: object) -> CscWrapper: #, default_class = None) -> CscWrapper:
        """Takes the data and returns an instance of CscWrapper
        
        Args:
            data: The data to wrap
            creator: The owner of the data. None is a valid value.
        """
        if hasattr(data, 'is_null'):
            if data.is_null():
                return None
            
        class_mapping = {
            csc.model.ObjectId: PyObject,
            csc.model.DataId: DataProperty,
            csc.model.SettingId: SettingProperty,
            csc.Guid: PyGuid,
            csc.view.Scene: PyScene,
            csc.domain.Scene: DomainScene,
            csc.model.BehaviourViewer: BehaviourViewer,
            csc.model.ModelViewer: ModelViewer,
            csc.model.DataViewer: DataViewer,
            csc.layers.Viewer: LayersViewer,
            csc.update.ObjectGroup: SceneElement,
            csc.update.Object: SceneElement,
        }
        
        mapping = None
        if data.__class__ in class_mapping:
            mapping = class_mapping[data.__class__]
            #print('found mapping')
            
        if mapping and mapping == PyGuid:
            if isinstance(creator, GuidMapper) and creator.guid_class is not None:
                mapping = creator.guid_class
                
        if mapping is None:
            return data
        
        if isinstance(mapping, Property):
            return mapping('', data, creator)
        else:
            return mapping(data, creator)
        
        
    @property
    def creator(self):
        """What object is respsonsible for this object's data"""
        return self.__creator
    
    
    def replace_data(self, data):
        """Directly replace the underlying content that is wrapped"""
        self.__data = data
   
              
    def unwrap(self):
        """Return the underlying data that's wrapped"""
        return self.__data
                       
               
    def _wrap(self, csc_handle):
        return self.wrap(csc_handle, self)
    
    
    def _wrap_result(self, result: object):
        if hasattr(result, 'is_null') and result.is_null():
            return None
        
        if isinstance(result, list) or isinstance(result, tuple):
            return [CscWrapper.wrap(value, self) for value in result]
        elif isinstance(result, set):
            result_list = list(result)
            return set([CscWrapper.wrap(value, self) for value in result_list])
        else:
            return CscWrapper.wrap(result, self)



class SceneElement(CscWrapper):
    """Base class used to represent any wrapped data existing/related to a scene
    
    Used to share global scene access between scene data-specific classes.
    The csc viewers and editors need to be instanced in context to the
    current scene. Scene objects needing these viewers and editors is commmon
    among any datatypes.classes that represent scene data.
    """
    
    def __init__(self, *args, **kwargs):
        super(SceneElement, self).__init__(*args, **kwargs)
        
        self._scene: PyScene = None
        
        if self.creator is not None:
            if isinstance(self.creator, SceneElement):
                self._scene = self.creator.scene
            else:
                raise TypeError("{} is not an instance of SceneElement".format(self.creator.__class__.__name__))
            
            
    @property
    def scene(self):
        """Returns the view.Scene"""
        return self._scene
    
    
    @property
    def dom_scene(self):
        """Returns the domain.Scene"""
        #this property name is abbreviated to avoid conflicts with the csc
        #api function name domain_scene.        
        return self._scene.ds
    
    @property
    def mod_viewer(self):
        """Returns the ModelViewer"""
        #this property name is abbreviated to avoid conflicts with the csc
        #api function name model_viewer.
        
        return self._scene.mv
    
    @property
    def beh_viewer(self):
        """Returns the BehaviourViewer"""
        #this property name is abbreviated to avoid conflicts with the csc
        #api function name behaviour_viewer.        
        return self._scene.bv
    
    @property
    def dat_viewer(self):
        """Returns the DataViewer"""
        #this property name is abbreviated to avoid conflicts with the csc
        #api function name data_viewer.
        return self._scene.dv
    
    @property
    def lay_viewer(self):
        """Returns the LayersViewer"""
        return self._scene.lv
    
    @property
    def mod_editor(self):
        """Returns the active model editor
        
        This will only be valid during the call to self.scene.edit()
        """
        if not self._scene.editing:
            raise EditorError('Model Editor')
        return self._scene.me
    
    @property
    def beh_editor(self):
        """Returns the active behaviour editor
        
        This will only be valid during the call to self.scene.edit()
        """
        if not self._scene.editing:
            raise EditorError('Behaviour Editor') 
        return self._scene.be
    
    @property
    def dat_editor(self):
        """Returns the active data editor
        
        This will only be valid during the call to self.scene.edit()
        """
        if not self._scene.editing:
            raise EditorError('Data Editor')
        return self._scene.de
    
    @property
    def update_editor(self):
        """Returns the active update editor
        
        This will only be valid during the call to self.scene.edit()
        """
        if not self._scene.editing:
            raise EditorError('Update Editor')        
        return self._scene.ue
    
    @property
    def scene_updater(self):
        """Returns the active scene editor
        
        This will only be valid during the call to self.scene.edit()
        """
        if not self._scene.editing:
            raise EditorError('Scene Editor')        
        return self._scene.su
    
    @property
    def session(self):
        """Return the session associated with the current scene"""
        if not self._scene.editing:
            raise EditorError('Session')        
        return self._scene.sess

    
    
    
class PyScene(SceneElement):
    """Represents a csc.view.Scene and all the scene's viewers and editors"""
    
    def __init__(self, *args, **kwargs):
        super(PyScene, self).__init__(*args, **kwargs)
        self._scene = self
        self.ds = self.domain_scene()
        
        self.mv = self.ds.model_viewer()
        self.bv = self.ds.behaviour_viewer()
        self.dv = self.ds.data_viewer()
        self.lv = self.ds.layers_viewer()
        
        self._editing = False
        self.me = None
        self.be = None
        self.de = None
        self.le = None
        
        self.ue = None
        self.se = None        
        self.sess = None
        
        
    @property
    def editing(self):
        return self._editing
        
    def _start_editing(self, model_editor,
                       update_editor: csc.update.Update,
                       scene_updater: csc.domain.SceneUpdater,
                       session: csc.domain.Session
                       ):
        self._editing = True
        self.me = CscWrapper(model_editor, None) #model editor
        self.ue = SceneElement(update_editor, self) #update editor
        self.su = SceneElement(scene_updater, self) #scene updater
        self.sess = SceneElement(session, self) #session
        
        self.be = CscWrapper(model_editor.behaviour_editor(), None) #behaviour editor
        self.de = CscWrapper(model_editor.data_editor(), None) #data editor
        self.le = CscWrapper(model_editor.layers_editor(), None) #layers editor
        

    def _stop_editing(self):
        self._editing = False
        self.me = self.be = self.de = self.le = None
        self.ue = self.su = self.sess = None
        
        
    def edit(self, title: str, callback: typing.Callable, *callback_args, _low_level=True, **callback_kwargs):
        """Used to allow proper editing of scene content.
        
        Provides access to the domain_scene.editors and updaters. If an edit
        isn't in process then an undo operation is started. Any arguments
        that you need to pass into your func can be included when calling
        edit(). For Example:
        
        edit('making some changes', myFunc, param1, param2=True)
        Args:
            title: The title of the undo operation
            callback: the function/method to run after the editors are
            initialized
        """
                
        def mod(model_editor, update_editor, scene_updater, session):
            self._start_editing(model_editor, update_editor, scene_updater, session)
            callback(*callback_args, **callback_kwargs)
            self._stop_editing()
    
        if self._editing:
            callback(*callback_args, **callback_kwargs)
        else:
            if _low_level:
                self.dom_scene.warning("Scene edits should be made through PyScene.edit")
            
            self.ds.modify_update_with_session(title, mod)

                
    @staticmethod
    def _create_object(name, scene):
        #This was a def inside of create_object, but it's crashing
        #so I'm exprimenting with my options.
        root_group = scene.update_editor.root()
        root_group.create_object(name)        
            
            
    def create_object(self, name='') -> PyObject:
        #def _create_object(name):
            #root_group = self.update_editor.root()
            #root_group.create_object(name)
            
        self.edit('Create Object', PyScene._create_object, name, self, _low_level=True)

            
    def get_animation_size(self):
        return self.dat_viewer.get_animation_size()
            
              
                  
class PyGuid(SceneElement):
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
        guid = ''
        if self.unwrap():
            guid = self.unwrap().to_string()
        
        return "{}->{}->{}".format(self.__class__.__name__, self.name, guid)
        

    def __getattr__(self, attr):
        return getattr(self.unwrap(), attr)

    
    @property
    def name(self):
        """The name of the object"""
        return self.mod_viewer.get_object_name(self)
    
    
    @name.setter
    def name(self, value):
        """Set the name of the object"""
        def _set():
            self.mod_editor.set_object_name(self, value)
        
        title = "Set name".format(value)
        self.scene.edit(title, _set, _low_level=True)
        
        
    @property
    def children(self):
        """Returns a list of children parented to the current model"""
        return self.beh_viewer.get_children(self)
    
    
    @property
    def parent(self):
        """Get's the 'Basic' behaviour parent property value"""
        return self.Basic.parent.get()
    
    
    @parent.setter
    def parent(self, value):
        self.Basic.parent.set(value)
        

    def get_behaviours(self) -> typing.List[PyBehaviour]:
        """Returns a flat list of all the behaviours attached to the object"""
        return self.beh_viewer.get_behaviours(self)
    
    
    def get_behaviours_by_name(self, behaviour_name) -> list:
        """Returns a list of all the behaviours that match the given name"""
        
        if self.has_behaviour(behaviour_name):
            return self._behaviours_cache[behaviour_name]
        
        return []
    
    
    def get_behaviour_by_name(self, name) -> PyBehaviour | None:
        """Returns the PyBehaviour that matches the given input name
        
        raises:
            BehaviourSizeError: If more than one behaviour of the given name
            exists.
        """
        behaviours = self.get_behaviours_by_name(name)
        if not behaviours:
            return None
        
        elif len(behaviours) > 1:
            raise BehaviourSizeError(self.name, name)
        
        return behaviours[0] 
      
        
    def __getattr__(self, attr):
        result = self.get_behaviour_by_name(attr)
        if result:
            return result
        else:
            raise BehaviourError(attr)
    
    
    def _cache_behaviours(self):
        self._behaviours_cache = {}
        
        behaviours = self.get_behaviours() #beh_viewer.get_behaviours(self)
        for behaviour in behaviours:
            if behaviour.name in self._behaviours_cache:
                self._behaviours_cache[behaviour.name].append(behaviour)
            else:
                self._behaviours_cache[behaviour.name] = [behaviour]        

            
    def has_behaviour(self, behaviour_name) -> bool:
        """Returns True if a behaviour of the given name exists else False"""
        
        #If a requested behaviour is missing the internal behaviour cache is
        #rebuild before validating the missing data.
        
        if behaviour_name not in self._behaviours_cache:
            self._cache_behaviours()
            
        return behaviour_name in self._behaviours_cache
 


class PyBehaviour(PyGuid):
    """A wrapper for Cascadeur Behaviours"""
    
    def __init__(self, *args, **kwargs):
        super(PyBehaviour, self).__init__(*args, **kwargs)
            
        self._name, self.is_dynamic = self.get_behaviour_name(self, self.beh_viewer, self.dat_viewer)
    
        
    @property
    def name(self):
        """The name of the behaviour
        
        Dynamic behaviours will return the behaviourName property
        """
        return self._get_dynamic_name()

            
    @property
    def object(self):
        """Returns the object the behaviour is a part of"""
        return self.creator
    
    
    def _get_dynamic_name(self):
        if not self.is_dynamic:
            return self._name
        else:
            data_attr = self.get_data('behaviourName')
            data_attr.name = 'behaviourName'
            return self.dat_viewer.get_data_value(data_attr)
    
    
    @staticmethod
    def get_behaviour_name(behaviour_id: PyGuid, b_viewer: BehaviourViewer, d_viewer: DataViewer):
        """Returns a tuple of the behaviour name and if the behaviour is dynamic
        
        When the behaviour is dynamic behaviour.behaviourName is returned
        instead of 'Dynamic'.
        """
        
        name = b_viewer.get_behaviour_name(behaviour_id)
        
        is_dynamic = name == 'Dynamic'
        if is_dynamic:
            data_attr = b_viewer.get_behaviour_data(behaviour_id, 'behaviourName')
            data_attr.name = 'behaviourName'
            name = d_viewer.get_data_value(data_attr)
            
        return (name, is_dynamic)
    
    
    def _get_data(self, prop_name):
        try:
            #The CscWrapper returns a SettingProperty without the name
            dat_attr = self.get_data(prop_name)
            dat_attr.name = prop_name
            return dat_attr
        except:
            try:
                data_list = self.get_data_range(prop_name)
                return DataProperty(prop_name, data_list, self)
            except:
                pass
                
        return None
        

    def _get_setting(self, prop_name):
        try:
            #The CscWrapper returns a SettingProperty without the name
            setting_attr = self.get_setting(prop_name)
            setting_attr.name = prop_name
            return setting_attr
        except:
            try:
                settings_list = self.get_settings_range(prop_name)
                return SettingProperty(prop_name, settings_list, self)
            except:
                pass
        
        return None          

                
    def _get_object(self, prop_name):
        try:
            result_object = self.get_object(prop_name)
            return ObjectProperty(prop_name, result_object, self)
        except:
            try:
                object_list = self.get_objects_range(prop_name)
                return ObjectProperty(prop_name, object_list, self)
            except:
                pass
                        
        return None
        
        
    def _get_reference(self, prop_name):
        try:
            result_ref = self.get_reference(prop_name)
            return ReferenceProperty(prop_name, result_ref, self)
        except:
            try:
                ref_list = self.get_reference_range(prop_name)
                return ReferenceProperty(prop_name, ref_list, self)
            except:
                pass
                
        return None
        
            
    def __getattr__(self, attr):
        result = self._get_data(attr)
        if result:
            return result
        
        result = self._get_object(attr)
        if result:
            return result
        
        result = self._get_reference(attr)
        if result:
            return result
        
        result = self._get_setting(attr)
        if result:
            return result
        
        raise PropertyError(self.name, attr) 
        
    
    def get_name(self) -> str:
        """Returns the name of the behaviour
        
        For Dynamic behaviours this will return 'Dynamic'. Rather than Using
        this method consider using PyBehaviour.name property if you want the
        display name of a Dynamic behaviour.
        """
        return self.beh_viewer.get_behaviour_name(self)
        
    def get_owner(self) -> PyObject | None:
        """Returns the object holds the current behaviour"""
        return self.beh_viewer.get_behaviour_owner(self)

    def get_data(self, name) -> DataProperty:
        """Returns a DataProperty instance for the given property name"""
        return self.beh_viewer.get_behaviour_data(self, name)
    
    def get_data_range(self, name) -> DataProperty:
        """Returns a DataProperty instance for the given property name
        
        DataProperty.is_range() will return True.
        """
        return self.beh_viewer.get_behaviour_data_range(self, name)
    
    def get_setting(self, name):
        """Returns a SettingProperty instance for the given property name"""
        return self.beh_viewer.get_behaviour_setting(self, name)
    
    def get_settings_range(self, name):
        """Returns a SettingProperty instance for the given property name

        DataProperty.is_range() will return True.        
        """
        return self.beh_viewer.get_behaviour_settings_range(self, name)    

    def get_object(self, name) -> PyObject:
        """Returns a ObjectProperty instance for the given property name"""
        return self.beh_viewer.get_behaviour_object(self, name)
    
    def get_objects_range(self, name) -> typing.List[PyObject]:
        """Returns a ObjectProperty instance for the given property name
        
        DataProperty.is_range() will return True.            
        """
        return self.beh_viewer.get_behaviour_objects_range(self, name)
        
    def get_reference(self, name) -> PyBehaviour:
        """Returns a ReferenceProperty instance for the given property name"""
        return self.beh_viewer.get_behaviour_reference(self, name)
    
    def get_reference_range(self, name) -> typing.List[PyBehaviour]:
        """Returns a ReferenceProperty instance for the given property name
        
        DataProperty.is_range() will return True.            
        """
        return self.beh_viewer.get_behaviour_reference_range(self, name)
    
    def is_hidden(self) -> bool:
        return self.beh_viewer.is_hidden(self)
    
    def get_property_names(self):
        """Returns a list of all the property names for this behaviour"""
        return self.beh_viewer.get_behaviour_property_names(self)
    
    def get_property(self, name) -> DataProperty | ObjectProperty |\
        ReferenceProperty | SettingProperty | None:
        """Returns a property sub-class instance based on the property name
        
        This method will determine the correct getter method to call based on
        the type content the property name represents.
        
        Returns:
            DataProperty: For data properties
            ObjectProperty: For properties that hold object references
            ReferenceProperty: For propetries that hold behaviour references
            SettingProperty: For setting properties
            None: When a property by that name doesn't exist.        
        """
        
        property_names = self.get_property_names()

        try:
            idx = property_names.index(name)
            return self.__getattr__(property_names[idx])
        except:
            return None         
    
    
    
class PyLayer(PyGuid):
    def __init__(self, *args, **kwargs):
        super(PyLayer, self).__init__(*args, **kwargs)
        
    
    
class Property(PyGuid):
    """Base class for any Behaviour properties"""
    
    def __init__(self, name, *args, **kwargs):
        super(Property, self).__init__(*args, **kwargs)
        
        self._name = name
        
    @property
    def is_range(self):
        return isinstance(self.unwrap(), list)
                
        
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
        return self.creator
    
   
  
class DataProperty(Property):
    """Represents behaviour.properties that store csc.model.Data(s)"""

    
    def __init__(self, *args, **kwargs): #name: str, attr_type: AttrType, guid: csc.model.DataId, behaviour: PyBehaviour):
        super(DataProperty, self).__init__( *args, **kwargs) #name, attr_type, guid, behaviour)    

        #TODO: will a dataId always safely return data?
        try:
            self._data = self.dat_viewer.get_data(self)
        except:
            self._data = None
            
    
    def is_animateable(self):
        return self._data is not None and self._data.mode == csc.model.DataMode.Animation
    
    
    def get(self, frame = -1):
        if self.is_animateable():
            if frame < 0:
                frame = self.domain_scene.get_current_frame()
                
            return self.dat_viewer.get_data_value(self, frame) 
        else:
            return self.dat_viewer.get_data_value(self)
        
        
    def get_default_value(self):
        return self.dat_viewer.get_behaviour_default_data_value(self.behaviour, self.name)
        
        
    #def set(self, value):
        #if value is None:
            #value = PyObject(csc.model.ObjectId.null(), self.scene)        

        #def _set():
            #self.beh_editor.set_behaviour_field_value(self.behaviour, self.name, value)
        
        #title = "Set {}.{}".format(self.behaviour.name, self.name)
        #self.scene.edit(title, _set)       
        
        
        
class SettingProperty(Property):
    """Represents behaviour.properties that store csc.model.Settings(s)"""
    
    def __init__(self, *args, **kwargs):
        super(SettingProperty, self).__init__( *args, **kwargs)
        
        #TODO: will a data guid always safely return data?
        try:
            self.__data = self.dat_viewer.get_setting(self) #.unwrap())
        except:
            self.__data = None
            
            
    def is_animateable(self):
        return self.__data is not None and self.__data.mode == csc.model.SettingMode.Animation


    def get(self, frame = -1):
        if self.is_animateable():
            if frame < 0:
                frame = self.domain_scene.get_current_frame()
                
            return self.dat_viewer.get_setting_value(self, frame) 
        else:
            return self.dat_viewer.get_setting_value(self)  
        
        
        
class ObjectProperty(Property):
    """Represents behaviour.properties that maps to object(s)"""
        
    def __init__(self, *args, **kwargs):
        super(ObjectProperty, self).__init__( *args, **kwargs)


    def __get(self, value):
        return PyObject(value, self.scene)


    def get(self) -> PyObject | typing.List[PyObject] | None:
        """returns the PyObject stored by the property
        
        When self.is_range() returns True, a list of results is returned.        
        """
        
        content = self.unwrap()
        if content is None:
            return None
        elif isinstance(content, list):
            return [self.__get(value) for value in content]
        else:
            return self.__get(content)
        

    def set(self, value: PyObject|None):
        if value is None:
            value = PyObject(csc.model.ObjectId.null(), self.scene)        

        def _set():
            self.beh_editor.set_behaviour_model_object(self.behaviour, self.name, value)
        
        title = "Set {}.{}".format(self.behaviour.name, self.name)
        self.scene.edit(title, _set, _low_level=True)     
    
    
    
class ReferenceProperty(Property):
    """Represents behaviour.properties that map to other behaviour(s)"""
    
    def __init__(self, *args, **kwargs):
        super(ReferenceProperty, self).__init__( *args, **kwargs)
        
        
    def __get(self, value):
        #we need to access the global behaviour viewer to find out what
        #behaviour owns the reference.
        behaviour_owner = self.behaviour.beh_viewer.get_behaviour_owner(value)
        return PyBehaviour(value, behaviour_owner)


    def get(self) -> PyBehaviour | typing.List[PyBehaviour] | None:
        """returns the PyBehaviour stored by the property
        
        When self.is_range() returns True, a list of results is returned.       
        """
        
        content = self.unwrap()
        if content is None:
            return None
        elif isinstance(content, list):
            return [self.__get(value) for value in content]
        else:
            return self.__get(content)



class GuidMapper(SceneElement):
    """Used to wrap a generic csc.Guid to a specific class"""
    guid_class = None    

          
class LayersViewer(GuidMapper):
    guid_class = PyLayer
    
        
class BehaviourViewer(GuidMapper):
    guid_class = PyBehaviour
       
        
class ModelViewer(GuidMapper):
    guid_class = None
          
        
class DataViewer(GuidMapper):
    guid_class = None
        

class DomainScene(GuidMapper):
    guid_class = None
        
        
        
        
    
