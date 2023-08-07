import os
import tempfile


print("loading stuff")

def command_name():
    return "Guru.Run Temp Code"


def run(scene):
    """Get the temp file of a cascadeur pigeon and execute it"""
    #import wingedcarrier.pigeons
    #temp_path = wingedcarrier.pigeons.CascadeurPigeon.get_temp_filepath()
    #wingedcarrier.pigeons.CascadeurPigeon.read_file(temp_path)    

    try:
        import wingedcarrier.pigeons
        temp_path = wingedcarrier.pigeons.CascadeurPigeon.get_temp_filepath()
        wingedcarrier.pigeons.CascadeurPigeon.read_file(temp_path)
    except Exception as e:
        scene.error('Reading temp file failed. Exception {}'.format(e))