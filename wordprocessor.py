import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import colorchooser
from tkinter import font
import os
import configparser
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# Get configuration options from file
config = configparser.ConfigParser()
config.read('wordprocessor.ini')
fgcolor = config.get('DEFAULT', 'foreground_color', fallback='#ffffff')
bgcolor = config.get('DEFAULT', 'background_color', fallback='#0099ff')
fontfamily = config.get('DEFAULT', 'font_family', fallback='Courier New')
fontsize = config.getint('DEFAULT', 'font_size', fallback=14)
drive_enabled = config.getboolean('DEFAULT', 'drive_enabled', fallback=False)

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s;%(module)s;%(funcName)s;%(levelname)s;%(message)s")
logger.propagate = False
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
HOME_DIR = os.environ['HOME']
LOG_DIR = HOME_DIR + '/Logs'
LOG_FILE = LOG_DIR + '/pyword.log'
try:
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
except OSError as error:
    logger.error(f'An error occurred: {error}')
except:
    logger.error('Error creating log file')
logger.info("Setup logging")

# Setup Google Drive support
drive_service = None
drive_folder_id = None
creds = None
SCOPES = ['https://www.googleapis.com/auth/drive']
if drive_enabled:
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        queryString = "mimeType='application/vnd.google-apps.folder' and name='WordProcessor'"
        response = drive_service.files().list(q=queryString, spaces='drive', fields='files(id, name)').execute()
        for folder in response.get('files', []):
            if folder.get('name') == 'WordProcessor':
                drive_folder_id = folder.get('id')
                break
        if not drive_folder_id:             
            file_metadata = {'name': 'WordProcessor', 'mimeType': 'application/vnd.google-apps.folder'}
            folder = drive_service.files().create(body=file_metadata, fields='id').execute()
            if folder:
                drive_folder_id = folder.get('id')
    except HttpError as error:
        logger.error(f'An error occurred: {error}')

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
        with open(filename, mode='r', encoding='utf-8') as f:
            contents = f.read()
            text.insert('1.0', contents)
        self.notebook.select(self.notebook.tabs()[-1])
        self.refresh_menu_items()

    def save_file(self):
        tabid = self.notebook.select()
        filename = self.notebook.tab(tabid, "text")
        text = self.notebook.nametowidget(tabid)
        contents = text.get('1.0', 'end')
        with open(filename, mode='w', encoding='utf-8') as f:
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
                file_id = self.search_file_on_drive(basename)
                if file_id:
                    media = MediaFileUpload(filename, mimetype='text/plain')
                    file = drive_service.files().update(fileId=file_id, media_body=media).execute()
                    if file:
                        logger.info('Updated %s in the WordProcessor folder on Google Drive' %filename)
                else:                                
                    file_metadata = {'name': basename, 'parents': [drive_folder_id]}
                    media = MediaFileUpload(filename, mimetype='text/plain')
                    file = drive_service.files().create(body=file_metadata, media_body=media).execute()
                    if file:
                        logger.info('Saved %s to the WordProcessor folder on Google Drive' %filename)
            except HttpError as error:
                logger.error(f'An error occurred: {error}')

    def search_file_on_drive(self, filename):
        if drive_enabled:
            try:
                queryString = "name='%s' and '%s' in parents" %(filename, drive_folder_id)
                response = drive_service.files().list(q=queryString, spaces='drive', fields='files(id, name)').execute()
                for file in response.get('files', []):
                    if file.get('name') == filename:
                        return file.get('id')
            except HttpError as error:
                logger.error(f'An error occurred: {error}')
        return None
 
if __name__ == '__main__':
    app = WordProcessor()
    app.mainloop()