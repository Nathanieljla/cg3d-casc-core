def command_name():
    return "Guru.Maya.Export Animation"


def run(scene):
    import wingcarrier.pigeons
    
    maya =  wingcarrier.pigeons.MayaPigeon()
    command = 'print("this worked"); print("Howard")'
    maya.send_python_command(command)