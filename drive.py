import os
import shutil
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload,MediaIoBaseDownload
from FaceEncoder import FaceEncoding
import io 

class DriveUpload:
    SCOPES = ['https://www.googleapis.com/auth/drive']
    service_account = "data/service_account.json"
    parent_folder_id = "1LIrXQx-imgzCzN2y3AsnmFuTmLF5Q0l2"

    def __init__(self):
        self.saveDirectory = "data/StudentPictures"
        self.obj = FaceEncoding()

    def authenticate(self):
        creds = service_account.Credentials.from_service_account_file(DriveUpload.service_account, scopes=DriveUpload.SCOPES)
        return creds
    
    import shutil

    def uploadPhoto(self, file_path, AridNo):
        print(file_path, "    ", AridNo)
        creds = self.authenticate()
        service = build('drive', 'v3', credentials=creds)

        allowed_extensions = ['.png', '.jpg', '.jpeg']
        file_name = os.path.basename(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()

        if file_extension not in allowed_extensions:
            print(f"Invalid file type: {file_extension}. Only PNG, JPG, and JPEG are allowed.")
            return

        new_file_name = f"{AridNo}{file_extension}"
        new_file_path = os.path.join(self.saveDirectory, new_file_name)

        # Use shutil.move() to handle cross-drive moves
        try:
            shutil.move(file_path, new_file_path)
            print(f"File moved to: {new_file_path}")
        except FileNotFoundError as e:
            print(f"FileNotFoundError: {e}")
            return
        except OSError as e:
            print(f"OSError: {e}")
            return

        if not os.path.exists(new_file_path):
            print(f"File does not exist at {new_file_path}")
            return

        self.obj.StoreEncoding(new_file_name)

        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        mime_type = mime_types.get(file_extension, 'application/octet-stream')

        file_metadata = {
            'name': new_file_name,
            'parents': [DriveUpload.parent_folder_id]
        }

        media = MediaFileUpload(new_file_path, mimetype=mime_type)

        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media
        ).execute()
        
        print(f"File {new_file_name} uploaded to Google Drive with ID: {uploaded_file['id']}")
        return True

    def listFiles(self):
        creds = self.authenticate()
        service = build('drive', 'v3', credentials=creds)

        results = service.files().list(
            q=f"'{DriveUpload.parent_folder_id}' in parents",
            spaces="drive",
            fields='files(id, name)'
        ).execute()

        items = results.get('files', [])
        return items

    def download_photos(self, file_id, file_name):
        creds = self.authenticate()
        service = build('drive', 'v3', credentials=creds)

        request = service.files().get_media(fileId=file_id)
        file_path = os.path.join(self.saveDirectory, file_name)

        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Downloading {file_name}: {int(status.progress() * 100)}%")

    def downloadAll(self):
        items = self.listFiles()
        if items:
            for item in items:
                print(f"Downloading: {item['name']}")
                self.download_photos(item['id'], item['name'])
        else:
            print("No files found in the folder.")
