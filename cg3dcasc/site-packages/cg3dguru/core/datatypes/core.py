from __future__ import annotations #used so I don't have to forward declare classes for type hints

# https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html


from enum import Enum, Flag, auto
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
            message = "{0}.{1} ERRORs, because more than one behaviour exists. Try {0}.get_behaviours_by_name('{1}')[0] instead.".format(object_name, behaviour_name)
            
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
####---Enums---
#################
class PropertyType(Flag):
    RANGE = auto()
    DATA = auto()
    DATA_RANGE = DATA | RANGE
    SETTING = auto()
    SETTING_RANGE = SETTING | RANGE
    REFERENCE = auto()
    REFERENCE_RANGE = REFERENCE | RANGE
    OBJECT = auto()
    OBJECT_RANGE = OBJECT | RANGE



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
            creator: The owner of the data. Use None if there is no creator.
        """
        
        ##It seems like there's instances where we still want handles
        ##null objects.
        #if hasattr(data, 'is_null') and data.is_null():
            #return None
            
        class_mapping = {
            csc.model.ObjectId: PyObjectId,
            #csc.model.DataId: PyDataId, #DataProperty,
            #csc.model.SettingId: PySettingId, #SettingProperty,
            csc.Guid: PyGuid,
            csc.view.Scene: PyScene,
            csc.domain.Scene: DomainScene,
            csc.model.BehaviourViewer: BehaviourViewer,
            csc.model.ModelViewer: ModelViewer,
            csc.model.DataViewer: DataViewer,
            csc.layers.Viewer: LayersViewer,
            csc.update.ObjectGroup: SceneElement,
            csc.update.Object: PyObjectNode,
            #csc.update.UpdateGroup: UpdateGroup,
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

        return mapping(data, creator)        
        #if isinstance(mapping, Property):
            #return mapping('', data, creator)
        #else:
            #return mapping(data, creator)
        
        
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
        ##It seems like there's instances where we still want handles
        ##null objects.
        #if hasattr(result, 'is_null') and result.is_null():
            #return None
        
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


    
#def start_scene_edit(scene, callback, callback_args, callback_kwargs, model_editor, update_editor, scene_updater, session):
    #scene._start_editing(model_editor, update_editor, scene_updater, session)
    #callback(*callback_args, **callback_kwargs)
    #scene._stop_editing()    
    
    
    
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
        self._update_accessed = False
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
        self._update_accessed = False
        
        self.me = SceneElement(model_editor, self) #model editor
        self.ue = UpdateEditor(update_editor, self) #update editor
        self.su = SceneElement(scene_updater, self) #scene updater
        self.sess = SceneElement(session, self) #session

        self.be = BehaviourEditor(model_editor.behaviour_editor(), self) #behaviour editor
        self.de = SceneElement(model_editor.data_editor(), self) #data editor
        self.le = LayersEditor(model_editor.layers_editor(), self) #layers editor
        
        
    @SceneElement.update_editor.getter
    def update_editor(self):
        self._update_accessed = True
        return super().update_editor
        

    def _stop_editing(self):
        self._editing = False
        self._update_accessed = False
        self.me = self.be = self.de = self.le = None
        self.ue = self.su = self.sess = None
          
        
    def edit(self, title: str, callback: typing.Callable, *callback_args, _internal_edit=False, **callback_kwargs):
        """Used to allow proper editing of scene content.
        
        Provides access to the domain_scene.editors and updaters. If an edit
        isn't in process then an modify operation is started. Any arguments
        that you need to pass into your func can be included when calling
        edit(). For Example:
        
        edit('making some changes', myFunc, param1, param2=True)
        Args:
            title: The title of the modify operation
            callback: the function/method to run after the editors are
            initialized
        """
        def _scene_edit(model_editor, update_editor, scene_updater, session):
            self._start_editing(model_editor, update_editor, scene_updater, session)        
            callback(*callback_args, **callback_kwargs)          
            scene_updater.generate_update()
            self._stop_editing()
            
            
        if not _internal_edit:
            #external callbacks should have a handle to the PyScene so the editors can be accessed
            callback_args = list(callback_args)
            callback_args.insert(0, self)
    
        if self._editing:
            callback(*callback_args, **callback_kwargs)
        else:
            if _internal_edit:
                self.dom_scene.warning("Scene edits should be made through PyScene.edit")
             
            self.ds.modify_update_with_session(title, _scene_edit)

            
    def create_object(self, name='') -> PyObjectId:
        new_object = None
        
        def _create_object(name):
            nonlocal new_object
            new_object = self.update_editor.create_object_node(name)

            
        self.edit('Create Object', _create_object, name, _internal_edit=True)
        return new_object.object_id()

            
    def get_animation_size(self):
        return self.dat_viewer.get_animation_size()
    
         
                  
class PyGuid(SceneElement):
    """Base class for wrappping csc.Guid and all Ids"""

    def __init__(self, *args, **kwargs):
        #call objects.__init__ so it plays nice with mixins
        super(PyGuid, self).__init__(*args, **kwargs)
        
        
        
class PyObjectNode(SceneElement):
    """Represents an object within the node graph"""
    pass
    #def object_id(self):
        #return self.unwrap().object_id()
        


#class PyDataId(PyGuid):
    #pass


#class PySettingId(PyGuid):
    #pass


class PyObjectId(PyGuid):
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
        self.scene.edit(title, _set, _internal_edit=True)
        
        
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
        #rebuild to make sure the data is up to date.
        if behaviour_name not in self._behaviours_cache:
            self._cache_behaviours()
            
        return behaviour_name in self._behaviours_cache
 
 
    def add_behaviour(self, name, dynamic_name=None, group_name=None):
        add_dynamic = name == 'Dynamic'
        output = None
        def _add_behaviour():
            nonlocal output
            output = self.beh_editor.add_behaviour(self, name)
            if add_dynamic:
                name_prop = output.get_property('behaviourName')
                name_prop.add_data('dynamic name', csc.model.DataMode.Static, dynamic_name, group_name=group_name)
            
        if add_dynamic and dynamic_name is None:
            raise KeyError("add_behaviour optional arg 'dynamic_name' is missing.")
            
        self.scene.edit("Add Behaviour {}".format(name), _add_behaviour, _internal_edit=True)
        return output
    
#---wrapped behaviour viewer functions----    

    def get_behaviours(self) -> typing.List[PyBehaviour]:
        """Returns a flat list of all the behaviours attached to the object"""
        return self.beh_viewer.get_behaviours(self)

    
#---wrapped data editor functions
    def add_data(self, data_name: str, mode: csc.model.DataMode, value, data_id=None, group_name: str=None) -> csc.model.Data:
        """Wrapper DataEditor.add_data
        
        Args:
            data_name:user readable name of the data
            mode:Details of how the data will be stored
            value:The default value of the data.
            data_id (optional): an existing data_id to associate the data with. For testing/internal use.
            group_name (optional): If a group_name is defined, then the data
            will be added to a UpdateGroup of the given name. If the name
            doesn't exist, then one will be made.
            
        Returns:
            csc.model.Data            
        """
        result = None
        def _object_add_data():
            nonlocal result
            if data_id:
                result = self.dat_editor.add_data(self, data_name, mode, value, data_id)
            else:
                result = self.dat_editor.add_data(self, data_name, mode, value)
                
            if group_name:
                update_node = self.update_editor.get_node_by_id(self)
                root_group = update_node.root_group()
                target_group = None
                if not root_group.has_node(group_name):
                    target_group = root_group.create_sub_update_group(group_name)
                    self.scene_updater.generate_update()
                else:
                    for node in root_group.nodes():
                        if isinstance(node, csc.update.UpdateGroup) and node.name == group_name:
                            target_group = node
                            break
                        
                print(target_group)
                        
                
                        
                                      
                
        self.scene.edit("Add data to {}".format(self.name), _object_add_data, _internal_edit=True)
        return result
    
    
    def add_setting(self, setting_name: str, mode: csc.model.SettingMode, value, setting_id=None) -> csc.model.Setting:
        result = None
        def _object_add_setting():
            nonlocal result
            if setting_id:
                result = self.dat_editor.add_setting(self, setting_name, mode, value, setting_id)
            else:
                result = self.dat_editor.add_setting(self, setting_name, mode, value)
                
        self.scene.edit("Add setting to {}".format(self.name), _object_add_setting, _internal_edit=True)
        return result
        



class PyBehaviour(PyGuid):
    """A wrapper for Cascadeur Behaviours"""
    
    def __init__(self, *args, **kwargs):
        super(PyBehaviour, self).__init__(*args, **kwargs)
        
        self._property_types = {name:self._get_property_type(name) for name in self.get_property_names()}     
        self._name = self.get_name()
        self.is_dynamic = self._name == 'Dynamic'
         
        for key, value in self._property_types.items():
            print("'{}.{}': {}".format(self._name, key, value))

        
    @property
    def name(self):
        """The name of the behaviour
        
        Dynamic behaviours will return the behaviourName property
        """
        return self._get_dynamic_name()

            
    @property
    def object(self):
        """Returns the object the behaviour is a part of"""
        return self.get_owner()
    
    
    def _get_dynamic_name(self):
        #Make sure force comes first, because this will be called
        #before self.is_dynamic or self._name is defined.
        if not self.is_dynamic:
            return self._name
        else:
            data_prop = self.get_property('behaviourName')
            #newly created behaviour's won't have a name assigned yet.
            if data_prop.get() is None:
                return ''
            
            data_prop.name = 'behaviourName'
            return self.dat_viewer.get_data_value(data_prop)
        
    #def _get_data(self, prop_name):
        #try:
            ##The CscWrapper returns a SettingProperty without the name
            #dat_attr = self.get_data(prop_name)
            #dat_attr.name = prop_name
            #return dat_attr
        #except:
            #try:
                #data_list = self.get_data_range(prop_name)
                #return DataProperty(prop_name, data_list, self)
            #except:
                #pass
                
        #return None
        

    #def _get_setting(self, prop_name):
        #try:
            ##The CscWrapper returns a SettingProperty without the name
            #setting_attr = self.get_setting(prop_name)
            #setting_attr.name = prop_name
            #return setting_attr
        #except:
            #try:
                #settings_list = self.get_settings_range(prop_name)
                #return SettingProperty(prop_name, settings_list, self)
            #except:
                #pass
        
        #return None          

                
    #def _get_object(self, prop_name):
        #try:
            #result_object = self.get_object(prop_name)
            #return ObjectProperty(prop_name, result_object, self)
        #except:
            #try:
                #object_list = self.get_objects_range(prop_name)
                #return ObjectProperty(prop_name, object_list, self)
            #except:
                #pass
                        
        #return None
        
        
    #def _get_reference(self, prop_name):
        #try:
            #result_ref = self.get_reference(prop_name)
            #return ReferenceProperty(prop_name, result_ref, self)
        #except:
            #try:
                #ref_list = self.get_reference_range(prop_name)
                #return ReferenceProperty(prop_name, ref_list, self)
            #except:
                #pass
                
        #return None
        
            
    def _get_data(self, prop_name, is_range):
        default = None
        
        if is_range:
            default = DataProperty(prop_name, [], self)
            value = self.get_data_range(prop_name)
        else:
            default = DataProperty(prop_name, None, self)
            value = self.get_data(prop_name)
    
        if value is not None:
            default = DataProperty(prop_name, value, self)
                
        return default  
        
        
    def _get_setting(self, prop_name, is_range):
        default = None
        
        if is_range:
            default = SettingProperty(prop_name, [], self)
            value = self.get_settings_range(prop_name)
        else:
            default = SettingProperty(prop_name, None, self)
            value = self.get_setting(prop_name)
            
        if value is not None:
            default = SettingProperty(prop_name, value, self)
                
        return default        
              
         
    def _get_object(self, prop_name, is_range):
        default = None
        
        if is_range:
            default = ObjectProperty(prop_name, [], self)
            value = self.get_objects_range(prop_name)
        else:
            default = ObjectProperty(prop_name, None, self)
            value = self.get_object(prop_name)
            
        if value:
            default = ObjectProperty(prop_name, value, self)

        return default          
                 
        
    def _get_reference(self, prop_name, is_range):
        default = None
        
        if is_range:
            default = ReferenceProperty(prop_name, [], self)
            value = self.get_reference_range(prop_name)
        else:
            default = ReferenceProperty(prop_name, None, self)
            value = self.get_reference(prop_name)
            
        if value:
            default = ReferenceProperty(prop_name, value, self)
                
        return default
            
            
    def __getattr__(self, attr):
        prop = self.get_property(attr)
        if prop is None:
            raise PropertyError(self.name, attr)
        
        return prop
        
        #result = self._get_data(attr)
        #if result:
            #return result
        
        #result = self._get_object(attr)
        #if result:
            #return result
        
        #result = self._get_reference(attr)
        #if result:
            #return result
        
        #result = self._get_setting(attr)
        #if result:
            #return result
        
        #raise PropertyError(self.name, attr) 
        
        
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
        
        property_type = self.get_property_type(name)         
        if property_type is None:
            return None
        
        if PropertyType.DATA in property_type:
            prop = self._get_data(name, PropertyType.RANGE in property_type)
            
        elif PropertyType.SETTING in property_type:
            prop = self._get_setting(name, PropertyType.RANGE in property_type)
            
        elif PropertyType.REFERENCE in property_type:
            prop = self._get_reference(name, PropertyType.RANGE in property_type)
            
        elif PropertyType.OBJECT in property_type:
            prop = self._get_object(name, PropertyType.RANGE in property_type)
        
        return prop
    
    
    def _get_property_type(self, name):
        """Used to build the internal self._property_types mapping"""
        try:
            self.get_data(name)
            return PropertyType.DATA
        except:
            pass
        
        try:
            self.get_data_range(name)
            return PropertyType.DATA_RANGE
        except:
            pass
        
        try:
            self.get_setting(name)
            return PropertyType.SETTING
        except:
            pass
        
        try:
            self.get_settings_range(name)
            return PropertyType.SETTING_RANGE
        except:
            pass
        
        try:
            self.get_object(name)
            return PropertyType.OBJECT
        except:
            pass
        
        try:
            self.get_objects_range(name)
            return PropertyType.OBJECT_RANGE
        except:
            pass
        
        try:
            self.get_reference(name)
            return PropertyType.REFERENCE
        except:
            pass
        
        try:
            self.get_reference_range(name)
            return PropertyType.REFERENCE_RANGE
        except:
            pass
        
        raise PropertyError(self.name, name)
    
        
    
    def get_property_type(self, name) -> PropertyType | None:
        """Return the type of data a behaviour property maps to"""
        
        if name not in self._property_types:
            return None
        
        return self._property_types[name]
        

#----wrapped behaviour viewer functions----------------------        
    def get_name(self) -> str:
        """Returns the name of the behaviour
        
        For Dynamic behaviours this will return 'Dynamic'. Rather than Using
        this method consider using PyBehaviour.name property if you want the
        display name of a Dynamic behaviour.
        """
        return self.beh_viewer.get_behaviour_name(self)
        
    def get_owner(self) -> PyObjectId | None:
        """Returns the object holds the current behaviour"""
        return self.beh_viewer.get_behaviour_owner(self)

    def get_data(self, name) -> csc.model.DatatId:
        """Returns a csc.model.DatatId instance for the given property name"""
        return self.beh_viewer.get_behaviour_data(self, name)
    
    def get_data_range(self, name) -> typing.List[csc.model.DatatId]:
        """Returns a csc.model.DatatId list for the given property name"""
        return self.beh_viewer.get_behaviour_data_range(self, name)
    
    def get_setting(self, name) -> csc.model.SettingId:
        """Returns a csc.model.SettingId instance for the given property name"""
        return self.beh_viewer.get_behaviour_setting(self, name)
    
    def get_settings_range(self, name) -> typing.List[csc.model.SettingId]:
        """Returns a csc.model.SettingId list for the given property name"""
        return self.beh_viewer.get_behaviour_settings_range(self, name)    

    def get_object(self, name) -> PyObjectId:
        """Returns a PyObject instance for the given property name"""
        return self.beh_viewer.get_behaviour_object(self, name)
    
    def get_objects_range(self, name) -> typing.List[PyObjectId]:
        """Returns a ObjectProperty list for the given property name"""
        return self.beh_viewer.get_behaviour_objects_range(self, name)
        
    def get_reference(self, name) -> PyBehaviour:
        """Returns a PyBehaviour for the given property name"""
        return self.beh_viewer.get_behaviour_reference(self, name)
    
    def get_reference_range(self, name) -> typing.List[PyBehaviour]:
        """Returns a PyBehaviour list for the given property name"""
        return self.beh_viewer.get_behaviour_reference_range(self, name)
    
    def is_hidden(self) -> bool:
        return self.beh_viewer.is_hidden(self)
    
    def get_property_names(self):
        """Returns a list of all the property names for this behaviour"""
        return self.beh_viewer.get_behaviour_property_names(self)
    
#----wrapped behaviour editor functions----------------------
    def _run_edit(self, func, *args, **kwargs):
        result = None
        def _behaviour_edit():
            nonlocal result
            result = func(*args, **kwargs)
            
        self.scene.edit(func.__name__, _behaviour_edit, _internal_edit=True)
        return result

    def add_data_to_range(self, prop_name, data_id):
        func =  self.beh_editor.add_behaviour_data_to_range
        return self._run_edit(func, self, prop_name, data_id)
    
    def add_model_object_to_range(self, prop_name, model_id):
        func =  self.beh_editor.add_behaviour_model_object_to_range
        return self._run_edit(func, self, prop_name, model_id)
  
    def add_reference_to_range(self, prop_name, ref_id):
        func =  self.beh_editor.add_behaviour_reference_to_range
        return self._run_edit(func, self, prop_name, ref_id)
    
    def add_setting_to_range(self, prop_name, setting_id):
        func =  self.beh_editor.add_behaviour_setting_to_range
        return self._run_edit(func, self, prop_name, setting_id)
    
    def delete_self(self):
        func = self.beh_editor.delete_behaviour
        return self._run_edit(func, self)
        
    def erase_data_from_range(self, prop_name, data_id):
        func =  self.beh_editor.erase_behaviour_data_from_range
        return self._run_edit(func, self, prop_name, data_id)
    
    def erase_model_object_from_range(self, prop_name, model_id):
        func =  self.beh_editor.erase_behaviour_model_object_from_range
        return self._run_edit(func, self, prop_name, model_id)
  
    def erase_reference_from_range(self, prop_name, ref_id):
        func =  self.beh_editor.erase_behaviour_reference_from_range
        return self._run_edit(func, self, prop_name, ref_id)
    
    def erase_setting_from_range(self, prop_name, setting_id):
        func =  self.beh_editor.erase_behaviour_setting_from_range
        return self._run_edit(func, self, prop_name, setting_id)
    
    def hide(self, hidden=True):
        func =  self.beh_editor.hide_behaviour
        return self._run_edit(func, self, hidden)
    
    def set_data(self, prop_name, data_id):
        func =  self.beh_editor.set_behaviour_data
        return self._run_edit(func, self, prop_name, data_id)
    
    def set_data_to_range(self, prop_name, inserted_ids: typing.List[csc.model.DataId]):
        func =  self.beh_editor.set_behaviour_data_to_range
        return self._run_edit(func, self, prop_name, inserted_ids) 
    
    def set_model_object(self, prop_name, model_id):
        func =  self.beh_editor.set_behaviour_model_object
        return self._run_edit(func, self, prop_name, model_id)
    
    def set_model_objects_to_range(self, prop_name, inserted_ids: typing.List[csc.model.ObjectId]):
        func =  self.beh_editor.set_behaviour_model_objects_to_range
        return self._run_edit(func, self, prop_name, inserted_ids)  
  
    def set_reference(self, prop_name, ref_id):
        func =  self.beh_editor.set_behaviour_reference
        return self._run_edit(func, self, prop_name, ref_id)
    
    def set_references_to_range(self, prop_name, inserted_ids: typing.List[csc.model.Guid]):
        func =  self.beh_editor.set_behaviour_reference
        return self._run_edit(func, self, prop_name, inserted_ids)
    
    def set_setting(self, prop_name, setting_id):
        func =  self.beh_editor.set_behaviour_setting
        return self._run_edit(func, self, prop_name, setting_id)
    
    def set_settings_to_range(self, prop_name, setting_id):
        func =  self.beh_editor.set_behaviour_settings_to_range
        return self._run_edit(func, self, prop_name, setting_id)
    
    def set_string(self, prop_name: str, value: str):
        func =  self.beh_editor.set_behaviour_string
        return self._run_edit(func, self, prop_name, value)
    
    def set_field_value(self, prop_name: str, value: str):
        func = self.beh_editor.set_behaviour_field_value
        return self._run_edit(func, self, prop_name, value)
        
        
        
        

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
    def behaviour(self) -> PyBehaviour:
        return self.creator
    
    
    def get_content(self):
        content = self.unwrap()
        if content is None or hasattr(content, 'is_null') and content.is_null():
            return None
        
        return content
    
   
  
class DataProperty(Property):
    """Represents behaviour.properties that == csc.model.DataId(s)"""

    def __init__(self, *args, **kwargs):
        super(DataProperty, self).__init__( *args, **kwargs)   

        self.__data = None
        if self.get_content():
            self.__data = self.dat_viewer.get_data(self)
    
        #try:
            ##this will fail when we have null content
            #self._data = self.dat_viewer.get_data(self)
        #except:
            #self._data = None
            
    
    def is_animateable(self):
        return self._data is not None and self._data.mode == csc.model.DataMode.Animation
    
    
    def get(self, frame = -1):
        content = self.get_content()
        if content is None:
            return None            
        
        elif self.is_animateable():
            if frame < 0:
                frame = self.domain_scene.get_current_frame()
                
            return self.dat_viewer.get_data_value(self, frame) 
        else:
            return self.dat_viewer.get_data_value(self)
        
        
    def get_default_value(self):
        return self.dat_viewer.get_behaviour_default_data_value(self.behaviour, self.name)
    
    
    def add_data(self, name: str, mode: csc.model.DataMode, value, data_id=None, group_name=None):
        """Create a new csc.model.Data and assign it to the property"""
        added = False
        def _property_add_data():
            nonlocal added
            self._data = self.behaviour.object.add_data(name, mode, value, data_id=data_id, group_name=group_name)
            self.replace_data(self._data.id)
            added = self.behaviour.set_data(self.name, self)
           
        self.scene.edit("Add data to {}".format(self.name), _property_add_data, _internal_edit=True)
        return added
        
        
        
class SettingProperty(Property):
    """Represents behaviour.properties that == csc.model.SettingId(s)"""
    
    def __init__(self, *args, **kwargs):
        super(SettingProperty, self).__init__( *args, **kwargs)
        
        self.__data = None
        if self.get_content():
            self.__data = self.dat_viewer.get_data(self)
            
            
    def is_animateable(self):
        return self.__data is not None and self.__data.mode == csc.model.SettingMode.Animation


    def get(self, frame = -1):
        content = self.get_content()
        if content is None:
            return None        
        
        elif self.is_animateable():
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
        return PyObjectId(value, self.scene)


    def get(self) -> PyObjectId | typing.List[PyObjectId] | None:
        """returns the PyObject stored by the property
        
        When self.is_range() returns True, a list of results is returned.        
        """
        
        content = self.get_content()
        if content is None:
            return None  
        elif isinstance(content, list):
            return [self.__get(value) for value in content]
        else:
            return self.__get(content)
        

    def set(self, value: PyObjectId|None):
        if value is None:
            value = PyObjectId(csc.model.ObjectId.null(), self.scene)        

        def _set():
            self.beh_editor.set_behaviour_model_object(self.behaviour, self.name, value)
        
        title = "Set {}.{}".format(self.behaviour.name, self.name)
        self.scene.edit(title, _set, _internal_edit=True)     
    
    
    
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
        
        content = self.get_content()
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
    
    
class LayersEditor(GuidMapper):
    guid_class = PyLayer
    
    
class BehaviourViewer(GuidMapper):
    guid_class = PyBehaviour
    
    
class BehaviourEditor(GuidMapper):
    guid_class = PyBehaviour
       
           
class ModelViewer(GuidMapper):
    guid_class = None
          
        
class DataViewer(GuidMapper):
    guid_class = None
        

class DomainScene(GuidMapper):
    guid_class = None
    
    
class UpdateEditor(SceneElement):
    def create_object_node(self, name) -> PyObjectNode:
        root_group = self.update_editor.root()
        new_object = root_group.create_object(name)
        #self.scene_updater.generate_update()
        return new_object
    
        
        
if __name__ == '__main__':
    pass

    scene_manager = csc.app.get_application().get_scene_manager()
    scene = scene_manager.current_scene()
    current_scene: PyScene = PyScene.wrap(scene, None)
    current_scene.create_object('MyObject')
    
