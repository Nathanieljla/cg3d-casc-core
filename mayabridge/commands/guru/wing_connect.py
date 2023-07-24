


def command_name():
    return "Guru.Connect to Wing"


def run(scene):
    try:
        import cg3dguru.utils.wingdbstub
        cg3dguru.utils.wingdbstub.Ensure()
    except:
        scene.error('Connection to wing failed.') 