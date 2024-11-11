from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
import os
import pandas as pd

# El alcance necesario para la API de Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def authenticate_google_drive(credential_path):
    """Autentica la cuenta de Google Drive y devuelve el servicio."""
    creds = None
    # Si las credenciales ya fueron guardadas en un archivo token.json, cargarlas.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Si no tenemos credenciales, realizar el flujo de autorización
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)  # Asegúrate de tener el archivo 'credentials.json'
            creds = flow.run_local_server(port=0)  # Abre un navegador para autorizar

        # Guardar las credenciales para futuras ejecuciones
        with open(credential_path, 'w') as token:
            token.write(creds.to_json())

    # Crear el servicio de Google Drive
    service = build('drive', 'v3', credentials=creds)
    return service

def upload_to_drive(service, file_name, folder_id, df):
    """Sube un archivo a Google Drive en una carpeta específica."""
    # Guardar el DataFrame como un archivo CSV
    df.to_csv(file_name, index=False)

    # Subir el archivo CSV a la carpeta de Google Drive
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]  # Usamos el ID de la carpeta existente
    }
    media = MediaFileUpload(file_name, mimetype='text/csv')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    print(f"Archivo '{file_name}' subido a Google Drive con ID: {file['id']}")
