from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from util import logger, config
import os

drive_service = None
drive_folder_id = None
creds = None
SCOPES = ['https://www.googleapis.com/auth/drive']

is_enabled = config.getboolean('DEFAULT', 'drive_enabled', fallback=False)
if is_enabled:
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

def save_file(filename):
    basename = os.path.basename(filename)
    try:     
        file_id = search_file(basename)
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

def search_file(filename):
    try:
        queryString = "name='%s' and '%s' in parents" %(filename, drive_folder_id)
        response = drive_service.files().list(q=queryString, spaces='drive', fields='files(id, name)').execute()
        for file in response.get('files', []):
            if file.get('name') == filename:
                return file.get('id')
    except HttpError as error:
        logger.error(f'An error occurred: {error}')
    return None