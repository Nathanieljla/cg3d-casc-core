
import csc

def command_name():
    return "3D Guru.connect"


def run(scene):
    try:
        import cg3Dguru

        scene.error('import successful')
    except:
        scene.error('import failed')
