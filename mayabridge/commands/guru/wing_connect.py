


def command_name():
    return "3D Guru.wing"


def run(scene):
    try:
        import cg3Dguru.utils.wingdbstub
        scene.error('import successful')
    except:
        scene.error('import failed') 