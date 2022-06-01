# PyWord

## Running the Python app

We can run the Python app with the command:

    python wordprocessor.py

## Configuring the Python app

Configuration options like foreground color, background color, font family, font size, and Google Drive support can be configured in the wordprocessor.ini initialization file.

## Enabling and disabling Google Drive support

To enable Google Drive support, edit the wordprocessor.ini file and put True as a value for the drive_enabled key. To disable Google Drive support, edit the wordprocessor.ini file and put False as a value for the drive_enabled key.

## Installing the Google Drive Python dependencies

We can install the Google Drive Python dependencies with the command:

      pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

More information about the Google Drive Python API can be found [here](https://developers.google.com/drive/api/quickstart/python?hl=en_US).

## Creating a MacOS app

We can create a MacOS app from the Python source code using [py2app](https://py2app.readthedocs.io/en/latest/index.html)

py2app can be installed with the command

    pip install --upgrade py2app

Afterwards we can create an icons.icns icon file for the app by running the icon.sh script

    ./icon.sh

If py2app installed successfully, and the icon.icns file was created successfully, we can proceed with making the MacOS app.

First we create a setup.py file with the command:

    py2applet --make-setup wordprocessor.py icons.icns wordprocessor.ini credentials.json

Please note that the credentials.json file is only needed if you plan to enable Google Drive support. Otherwise you can omit the credentials.json file from the above command.

If the command ran successfully, and you see a setup.py file in your working directory, you can run the command:

    python setup.py py2app -A     

The -A option stands for alias. If you want the resource files to be moved into the MacOS app, you can omit the -A option and run this command instead:

    python setup.py py2app 

After running the setup.py script, you should see a build and a dist folder in your working directory.

Open Finder, navigate to your working directory, and click on the dist folder. Then, double click the wordprocessor.app file. The application should open. Once the application launches and is placed inside your dock, you can right-click the icon, select options, and select "Keep in dock".

The WordProcessor application should now be successfully installed on your hard disk and on your dock.

## The history of Tk

Tk (toolkit) is a graphical tool kit that was created in 1988. 
Tk was originally designed as an extension to the Tcl programming language, providing Tcl with a graphical toolkit. 
Early on a Python binding for Tk was developed. The Python binding is called Tkinter, which stands for Tk interface.
Tkinter is the default graphical toolkit for Python. It works by embedding a Tcl interpreter into the Python application.
The Tkinter commands (written in Python) are translated into Tcl commands and then interpreted by the Tcl interpreter.
The Tk library (and the Tkinter Python binding) allow for easy and rapid development of graphical user interfaces.