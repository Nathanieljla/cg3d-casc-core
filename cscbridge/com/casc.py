import winreg

#Computer\HKEY_LOCAL_MACHINE\SOFTWARE\Classes\Cascadeur\shell\open\command
#Computer\HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Cascadeur
#Computer\HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Nekki Limited\Cascadeur
#Computer\HKEY_CLASSES_ROOT\Cascadeur\shell\open\command
#


def get_exe_path():
    casc_path = None
    try:
        access_registry = winreg.ConnectRegistry(None,winreg.HKEY_CLASSES_ROOT)
        access_key = winreg.OpenKey(access_registry, r"Cascadeur\shell\open\command")
        casc_path = winreg.QueryValue(access_key, None)
    except Exception as e:
        print("Couldn't find the EXE in winreg. Let's look at this case! Error:{}".format(e))
        
    return casc_path




if __name__ == '__main__':
    app = get_exe_path()
    
    #C:\Users\natha\AppData\Local\Temp\maya_to_casc.fbx
    
    #C:\Users\natha\AppData\Local\Temp\hik_to_.qrigcasc
    
    
    print(app)