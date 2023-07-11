"""This us used in wing to send commands to Cascadeur.


Directions
Add this file to Wing's preferences > IDE Extension Scripting
then add run-in-maya to preferences > User Interface > Keyboard > Custom keybindings

This is a modified version of
https://github.com/raiscui/wing-scripts/blob/master/wingHotkeys.py

Changes include:
*  unifying highlighted text and sending py files to Maya
*  Reloading and importing py files in the namespace of their package


#starting with Pymel 1.3 we no longer need to worry about adding the completion\pi files
#https://dev.to/chadrik/pymels-new-type-stubs-2die


#The outdated way------------------------------------------
#download the devkit

#add the pi interfaces found here:
#devkitBase\devkit\other\pymel\extras\completion\pi

#Note: Maya 2023 is missing the other folder, so download Maya 2022 devkit and copy the other folder into
#the 2023 devkit

#to wing
#This can be added to the Source Analysis > Advanced > Interface File Path preference in Wing.
"""


import wingapi
import socket
import os,time #,locale
#import codecs

from pathlib import Path


###https://github.com/raiscui/wing-scripts/blob/master/wingHotkeys.py###

def getWingText():
	"""
	Based on the Wing API, get the selected text, and return it
	"""
	editor = wingapi.gApplication.GetActiveEditor()
	if editor is None:
		return ''
	doc = editor.GetDocument()
	start, end = editor.GetSelection()
	txt = doc.GetCharRange(start, end)
	return txt

	
def __Add_Parent_Module(name, path):
	found = False
	parent_module = os.path.join(path.parent, '__init__.py')
	
	if os.path.exists(parent_module):
		path = path.parent
		name = os.path.basename(path) + "." + name
		found = True

	return (found, name, path)


def get_module_info():
	"""
	returns the module namespace and the path to the file.
	"""
	editor = wingapi.gApplication.GetActiveEditor()
	if editor is None:
		return ''
	
	doc = editor.GetDocument()
	full_path = doc.GetFilename()

	name = os.path.basename(full_path).split('.')[0]
	path = Path(full_path)
	loop = True
	count = 0
	while loop and count < 20:
		count += 1
		loop, name, path = __Add_Parent_Module(name, path)

	#special case for when someone executes an __init__ file
	if (name.endswith(".__init__")):
		name = name.removesuffix(".__init__")

	return (name, full_path)


"""
Takes a string and sends to to maya over the commandline.  The string is converted by bytes on send
"""
def send_to_csc(sendCode):	
	# The commandPort you opened in cg3Dguru.com.server.py Make sure this matches!
	commandPort = 50000

	#mSocket = socket.socket(af, socktype, proto)
	mSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	print(sendCode)
	
	# Now ping csc over the command-port
	try:
		# Make our socket-> Maya connection: There are different connection ways
		# which vary between machines, so sometimes you need to try different
		# solutions to get it to work... :-S
		#mSocket.connect(("127.0.0.1", commandPort))
		#mSocket.connect(("::1",commandPort)) #works!
		mSocket.connect(("127.0.0.1", commandPort))
	
		# Send our code to Maya:
		mSocket.send( sendCode.encode() )
		
	except Exception as e:
		print ("Send to Cascadeur fail:", e)
	
	time.sleep(0.3)
	mSocket.close()



def write_temp_file(language):
	"""
	Send the selected code to be executed in Maya

	language : string : either 'mel' or 'python'
	"""


	if language != "mel" and language != "python":
		raise ValueError("Expecting either 'mel' or 'python'")

	# Save the text to a temp file. If we're dealing with mel, make sure it
	# ends with a semicolon, or Maya could become angered!
	txt = getWingText()
	if language == 'mel':
		if not txt.endswith(';'):
			txt += ';'
	tempFile = os.path.join(os.environ['TMP'], 'wingData.txt')
	f = open(tempFile, "wb")
	
	print(tempFile)
	#txt_unicode = uni(txt,'utf-8')
	#txt_u8 = txt_unicode.encode('utf-8')
	#f.write(txt_u8)
	
	f.write ( txt.encode() )

	f.close()


#=============------------ myself mod ------------ =============#
def highlight_to_csc():
	"""auto to maya"""
	editor = wingapi.gApplication.GetActiveEditor()
	doc = editor.GetDocument()
	doctype = doc.GetMimeType()
	
	if 'text/x-python' in str(doctype):
		write_temp_file('python')
		sendCode = u'python("import cg3D.utils.execute_wing_code; cg3D.utils.execute_wing_code.main(\'python\')")' 
		
	send_to_csc( sendCode )
#=============------------ myself mod ------------ =============#


def import_in_csc():
	"""
	Sends a mel command to Maya telling it to execute the embedded python code.
	"""
	doc_name, file_path = get_module_info()
	file_path = file_path.replace("\\", "/") #mel doesn't like \
	if doc_name:
		send_code = u'python("import cg3D.utils.execute_wing_code; cg3D.utils.execute_wing_code.import_and_run(\'{0}\', file_path=\'{1}\')")'.format( doc_name, file_path)
		print(send_code)
		send_to_csc( send_code )
	
	
def run_in_csc():
	highlighted_text = getWingText()
	if highlighted_text:
		highlight_to_csc()
	else:
		import_in_csc()


def test_script():
	app = wingapi.gApplication
	v = "Product info is: " + str(app.GetProductInfo())
	doc = app.GetCurrentFiles()
	dira = app.GetStartingDirectory()
	v += "\nAnd you typed: %s" % doc
	v += "\nAnd you typed: %s" % dira
	wingapi.gApplication.ShowMessageDialog("Test Message", v)


def open_folder():
	app = wingapi.gApplication
	folder = app.GetStartingDirectory()
	app.OpenURL(folder)