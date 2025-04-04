import io
import os.path
import tempfile
from constants import IMAGE_DATA_FILE
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models import Image
from utils import replace_kazakh_chars

SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_service():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("drive", "v3", credentials=creds)

        return service
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f"An error occurred: {error}")


def retrieve_photos(service, folder_id):
    """Получает список всех фотографий в папке, разбивая на страницы"""
    query = f"'{folder_id}' in parents and mimeType contains 'image/'"
    image_ids = []

    # Открываем файл для записи
    with open(IMAGE_DATA_FILE, "w") as file:
        next_page_token = None

        while True:
            results = (
                service.files()
                .list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType)",
                    pageSize=1000,
                    pageToken=next_page_token,  # Используем токен страницы
                )
                .execute()
            )

            photos = results.get("files", [])
            if not photos:
                break  # Если файлов нет, прекращаем цикл

            for photo in photos:
                name = (
                    photo["name"]
                    .replace(".jpg", "")
                    .replace("NONE", "")
                    .lower()
                    .strip()
                )
                image = Image(
                    origin_name=name,
                    name=replace_kazakh_chars(name),
                    id=photo["id"],
                )
                file.write(image.to_str() + "\n")
                image_ids.append(image)

            # Получаем токен следующей страницы
            next_page_token = results.get("nextPageToken")
            if not next_page_token:
                break  # Если следующей страницы нет, выходим

    print(f"✅ Найдено и записано {len(image_ids)} изображений.")
    return image_ids


def download_and_process_image(image_id, service):
    """Скачивает изображение по ID, обрабатывает его и удаляет временный файл"""

    # Создаем временный файл без открытия его
    with tempfile.NamedTemporaryFile(
        delete=False, mode="wb", suffix=".jpg"
    ) as temp_file:
        temp_file_name = temp_file.name  # Получаем имя временного файла

    # Скачиваем изображение в временный файл
    request = service.files().get_media(fileId=image_id)
    with io.FileIO(temp_file_name, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Загружается: {int(status.progress() * 100)}%")

    print("Обработанное изображение сохранено")

    # Удаляем временные файлы
    os.remove(temp_file_name)  # Удаляем временный файл

    print(f"Временные файлы удалены: {temp_file_name}")


def get_target_folder_id(service, folder_name):
    """Находит ID папки по её названию"""
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get("files", [])

    if not folders:
        print(f"❌ Папка '{folder_name}' не найдена!")
        return None

    folder_id = folders[0]["id"]
    print(f"📂 Найден ID папки '{folder_name}': {folder_id}")
    return folder_id
