from __future__ import print_function
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import font
import configparser
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

config = configparser.ConfigParser()
config.read('wordprocessor.ini')
fgcolor = config.get('DEFAULT', 'foreground_color', fallback='#ffffff')
bgcolor = config.get('DEFAULT', 'background_color', fallback='#0099ff')
fontfamily = config.get('DEFAULT', 'font_family', fallback='Courier New')
fontsize = config.getint('DEFAULT', 'font_size', fallback=14)
drive_enabled = config.getboolean('DEFAULT', 'drive_enabled', fallback=False)

SCOPES = ['https://www.googleapis.com/auth/drive']
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

class WordProcessor(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry('800x600')
        self.title("Word Processor")
        self.menubar = tk.Menu(self)
        self.filemenu = tk.Menu(self.menubar)
        self.filemenu.add_command(label='New', command=self.new_file)
        self.filemenu.add_command(label='Open', command=self.open_file)
        self.filemenu.add_command(label='Save', command=self.save_file)
        self.filemenu.add_command(label='Save as', command=self.save_file_as)
        self.filemenu.add_command(label='Close tab', command=self.close_tab)
        self.filemenu.add_command(label='Exit', command=self.exit)
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        self.colormenu = tk.Menu(self.menubar)
        self.colormenu.add_command(label='Select foreground', command=self.select_fgcolor)
        self.colormenu.add_command(label='Select background', command=self.select_bgcolor)
        self.menubar.add_cascade(label='Colors', menu=self.colormenu)
        self.cloudmenu = tk.Menu(self.menubar)
        self.cloudmenu.add_command(label='Save to Google Drive', command=self.save_to_google_drive)
        self.menubar.add_cascade(label='Cloud', menu=self.cloudmenu)
        self.config(menu=self.menubar)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill='both')
        self.notebook.bind('<<NotebookTabChanged>>', self.handle_tab_changed)
        self.refresh_menu_items()
        self.font = font.Font(family=fontfamily, size=fontsize)
        if drive_enabled:
            setup = self.setup_google_drive('WordProcessor')
            if setup:
                print('Setup Google Drive')

    def new_file(self):
        text = tk.Text(self.notebook, fg=fgcolor, bg=bgcolor, font=self.font)
        self.notebook.add(text, text='Untitled')
        self.notebook.select(self.notebook.tabs()[-1])
        self.refresh_menu_items()

    def open_file(self):
        filename = filedialog.askopenfilename()
        text = tk.Text(self.notebook, fg=fgcolor, bg=bgcolor, font=self.font)
        text.pack(expand=True, fill='both')
        self.notebook.add(text, text=filename)
        with open(filename, 'r') as f:
            contents = f.read()
            text.insert('1.0', contents)
        self.notebook.select(self.notebook.tabs()[-1])
        self.refresh_menu_items()

    def save_file(self):
        tabid = self.notebook.select()
        filename = self.notebook.tab(tabid, "text")
        text = self.notebook.nametowidget(tabid)
        contents = text.get('1.0', 'end')
        with open(filename, 'w') as f:
            f.write(contents)

    def save_file_as(self):
        tabid = self.notebook.select()
        filename = filedialog.asksaveasfilename()
        if filename:
            self.notebook.tab(tabid, text=filename)
            self.save_file()
            self.refresh_menu_items()

    def close_tab(self):
        self.notebook.forget("current")

    def exit(self):
        self.quit()

    def refresh_menu_items(self):
        tabid = self.notebook.select()
        if tabid and self.notebook.tab(tabid, "text") != 'Untitled':
            self.filemenu.entryconfig("Save", state="active")
            self.colormenu.entryconfig("Select foreground", state="active")
            self.colormenu.entryconfig("Select background", state="active")
            self.cloudmenu.entryconfig("Save to Google Drive", state="active")
        elif tabid:
            self.filemenu.entryconfig("Save", state="disabled")
            self.colormenu.entryconfig("Select foreground", state="active")
            self.colormenu.entryconfig("Select background", state="active")
            self.cloudmenu.entryconfig("Save to Google Drive", state="disabled")
        else:
            self.filemenu.entryconfig("Save", state="disabled")
            self.colormenu.entryconfig("Select foreground", state="disabled")
            self.colormenu.entryconfig("Select background", state="disabled")
            self.cloudmenu.entryconfig("Save to Google Drive", state="disabled")

    def handle_tab_changed(self, *args):
        self.refresh_menu_items()

    def select_fgcolor(self):
        color = colorchooser.askcolor()
        tabid = self.notebook.select()
        text = self.notebook.nametowidget(tabid)
        text.configure(fg=color[1])

    def select_bgcolor(self):
        color = colorchooser.askcolor()
        tabid = self.notebook.select()
        text = self.notebook.nametowidget(tabid)
        text.configure(bg=color[1])

    def save_to_google_drive(self):
        if drive_enabled:
            tabid = self.notebook.select()
            filename = self.notebook.tab(tabid, "text")
            basename = os.path.basename(filename)
            try:
                drive_service = build('drive', 'v3', credentials=creds)
                response = drive_service.files().list(q="mimeType='application/vnd.google-apps.folder' and name='WordProcessor'",
                                                    spaces='drive',
                                                    fields='files(id, name)').execute()
                for folder in response.get('files', []):
                    if folder.get('name') == 'WordProcessor':
                        folderid = folder.get('id')                        
                        file_metadata = {'name': basename, 'parents': [folderid]}
                        media = MediaFileUpload(filename, mimetype='text/plain')
                        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                        if file:
                            print('Saved %s to the WordProcessor folder in Google Drive' %filename)
            except HttpError as error:
                print(f'An error occurred: {error}')

    def setup_google_drive(self, foldername):
        if drive_enabled:
            try:
                drive_service = build('drive', 'v3', credentials=creds)
                response = drive_service.files().list(q="mimeType='application/vnd.google-apps.folder' and name='WordProcessor'",
                                                    spaces='drive',
                                                    fields='files(id, name)').execute()
                for folder in response.get('files', []):
                    if folder.get('name') == 'WordProcessor':
                        return True
                
                file_metadata = {
                'name': 'WordProcessor',
                'mimeType': 'application/vnd.google-apps.folder'
                }
                file = drive_service.files().create(body=file_metadata, fields='id').execute()
                if file:
                    return True
            except HttpError as error:
                print(f'An error occurred: {error}')
        return False
 
if __name__ == '__main__':
    app = WordProcessor()
    app.mainloop()