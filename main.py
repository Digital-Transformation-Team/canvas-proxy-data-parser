from typing import Optional
import pandas as pd
from dataclasses import dataclass
import io
import os.path
import tempfile
from googleapiclient.http import MediaIoBaseDownload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


@dataclass
class Image:
    name: str
    id: str


@dataclass
class Student:
    name: str
    canvas_name: str
    canvas_id: int
    image_id: Optional[str] = None

    def __repr__(self):
        return f"Student {self.canvas_id}: {self.name}"


def process_students() -> list[Student]:
    file_path = "students.xls"
    # Читаем Excel файл в pandas DataFrame
    df = pd.read_excel(file_path)

    # Создаем список объектов Student, маппируя данные из DataFrame
    students = []
    for _, row in df.iterrows():
        # Замаппим данные из столбцов на атрибуты Student
        student = Student(
            name=f"{row['Фамилия']} {row['Имя']} {row['Отчество']}",
            canvas_name=row["Канвас"],
            canvas_id=int(row["ID"]),  # Преобразуем в целое число
        )
        students.append(student)

    return students


def process_image(image_id, service):
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


def get_folder_id(service, folder_name):
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


def get_photos_in_folder(service, folder_id) -> list[Image]:
    """Получает список фотографий в папке"""
    query = f"'{folder_id}' in parents and mimeType contains 'image/'"
    results = (
        service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    )
    photos = results.get("files", [])

    if not photos:
        print("📂 В папке нет изображений.")
        return

    print("🖼 Список фотографий в папке:")
    image_ids = []
    for photo in photos:
        image = Image(name=photo["name"], id=photo["id"])
        image_ids.append(image)
    return image_ids


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


def get_student_image(student: Student, images: list[Image]) -> Image:
    for image in images:
        if image.name.lower() == student.name.lower():
            return image
    return None


if __name__ == "__main__":
    service = get_service()
    folder_id = get_folder_id(service, "gen_photos")
    images = get_photos_in_folder(service, folder_id)
    print(f"Найдено {len(images)} фото")
    students = process_students()
    print(f"Найдено {len(students)} студентов")

    # Compare images and students
    counter = 0
    for student in students:
        # Find image for this student
        image: Image = get_student_image(student, images)
        if image is not None:
            counter += 1
        # student.image_id = image.id
    print(f"Found images for {counter} students. Total students: {len(students)}")

    # for image_id in image_ids:
    #     result = process_image(service=service, image_id=image_id)
