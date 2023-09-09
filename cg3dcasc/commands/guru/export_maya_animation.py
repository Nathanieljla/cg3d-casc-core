def command_name():
    return "Guru.Maya.Export Animation"


def run(scene):
    import wingedcarrier.pigeons
    
    maya =  wingedcarrier.pigeons.MayaPigeon()
    command = 'print("this worked"); print("Howard")'
    maya.send_python_command(command)