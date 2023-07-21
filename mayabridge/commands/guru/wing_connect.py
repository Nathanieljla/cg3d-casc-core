


def command_name():
    return "Guru.wing"


def run(scene):
    try:
        import cg3dguru.utils.wingdbstub
        cg3dguru.utils.wingdbstub.Ensure()
    except:
        scene.error('import failed') 