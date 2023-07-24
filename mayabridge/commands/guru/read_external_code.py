import os
import tempfile


def command_name():
    return "Guru.Run Temp Code"


def run(scene):
    """runs code from os.path.join(tempfile.gettempdir(), 'cascadeur_code.txt')"""
    try:
        import cg3dguru.utils.execute_wing_code
        cg3dguru.utils.execute_wing_code.read_file()
    except:
        scene.error('Connection to wing failed.') 