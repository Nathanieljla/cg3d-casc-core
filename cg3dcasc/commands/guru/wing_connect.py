


def command_name():
    return "Guru.Connect to Wing"


def run(scene):
    try:
        import wingedcarrier.wingdbstub
        wingedcarrier.wingdbstub.Ensure()
    except:
        scene.error('Connection to wing failed.') 