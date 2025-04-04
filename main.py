from difflib import SequenceMatcher
import pandas as pd
from constants import (
    EXCEL_DATA_FILE,
    IMAGE_DATA_FILE,
    NO_VECTORS_MATCHED_DATA_FILE,
)
from google_service import get_service, retrieve_single_photo_path
import ml
import ml.face_encoder
from models import Student, Image
from utils import (
    initialize,
    replace_kazakh_chars,
    save_students_to_excel,
    save_unmatched_to_excel,
)


def process_students() -> list[Student]:
    df = pd.read_excel(EXCEL_DATA_FILE)

    students = []
    for _, row in df.iterrows():
        name = f"{row['Фамилия'].lower()} {row['Имя'].lower()} {row['Отчество'].lower() if isinstance(row['Отчество'], str) else ''}"
        student = Student(
            name=replace_kazakh_chars(name),
            origin_name=name,
            canvas_name=row["Канвас"],
            canvas_login=row["Логин"],
            canvas_id=int(row["ID"]),
        )
        students.append(student)

    return students


def get_images_from_file(size: int = None) -> list[Image]:
    images = []
    with open(IMAGE_DATA_FILE, "r") as file:
        lines = file.readlines()
        if size is None:
            for line in lines:
                images.append(Image.from_str(line))
        else:
            for i in range(size):
                images.append(Image.from_str(lines[i]))
    return images


def search_student_image(
    student: Student, images: list[Image], prev_student_name: str = None
) -> Image:
    student_parts = set(student.name.lower().split())
    best_match = None
    best_match_score = 0

    for image in images:
        image_parts = set(image.name.lower().split())

        if image.name.lower() == student.name.lower():
            return image

        common_parts = student_parts & image_parts
        uncommon_parts = student_parts ^ image_parts
        if len(common_parts) >= 2 and not uncommon_parts:
            return image

        similarity_score = SequenceMatcher(
            None, image.name.lower(), student.name.lower()
        ).ratio()
        if similarity_score > best_match_score:
            best_match = image
            best_match_score = similarity_score

    if best_match_score < 0.8 and prev_student_name:
        for image in images:
            similarity_score = SequenceMatcher(
                None, image.name.lower(), prev_student_name.lower()
            ).ratio()
            if similarity_score > best_match_score:
                best_match = image
                best_match_score = similarity_score

    return best_match


def match_students_with_images(
    images: list[Image], students: list[Student]
) -> list[Student]:
    print("Matching Started!")
    print(f"Найдено {len(images)} фото")
    print(f"Найдено {len(students)} студентов")
    # Compare images and students
    image_student = {
        k: v
        for k, v in zip(
            [image.origin_name for image in images], [None for _ in range(len(images))]
        )
    }
    matched_students: list[Student] = []
    print(f"Found uniq {len(image_student.keys())} names")
    for i, student in enumerate(students):
        # Find image for this student
        progress = round(((i + 1) * 100) / len(students), 2)
        print(f"Processing...: {progress}%")
        image: Image = search_student_image(student, images)
        if image is not None:
            if image_student[image.origin_name] is None:
                image_student[image.origin_name] = student.origin_name
                student.image_id = image.id
                matched_students.append(student)

    # print(f"Found images for {counter} students. Total students: {len(students)}")
    no_gf_images = []
    no_gf_students = set([student.origin_name for student in students])
    for image, student in image_student.items():
        if student is None:
            no_gf_images.append(image)
        else:
            no_gf_students.remove(student)
    save_unmatched_to_excel(no_gf_images=no_gf_images, no_gf_students=no_gf_students)
    print(
        f"Images with no gf: {len(no_gf_images)}. Total images: {len(images)}. With GF: {len(images) - len(no_gf_images)}"
    )
    print(
        f"Students with no gf: {len(no_gf_students)}. Total students: {len(students)}. With GF: {len(students) - len(no_gf_students)}"
    )
    print(f"Matching Completed! Result: {len(matched_students)}")
    return matched_students


def get_image_vectors(service, students: list[Student]) -> list[Student]:
    print("Vectorization Started with:", len(students))
    with ml.initialize():
        # Open image in tmp file
        for i, student in enumerate(students):
            progress = round(((i + 1) * 100) / len(students), 2)
            print(f"Processing...: {progress}%")
            with retrieve_single_photo_path(service, student.image_id) as photo_path:
                vector = ml.face_encoder.get_image_embedding(
                    image_path=photo_path, content_type=".jpg"
                )
                student.image_vector = vector
            # img_path = retrieve_single_photo_path(image_id=img_id)
            # image_embed = ml.get_image_embedding(image_path=image_path, content_type=image_content_type)
    print("Vectorization Completed! The result:", len(students))
    return students


if __name__ == "__main__":
    initialize()
    service = get_service()
    # folder_id = get_target_folder_id(service, "gen_photos")
    # images = retrieve_photos(service, folder_id)
    images = get_images_from_file(size=None)
    students = process_students()
    matched_students = match_students_with_images(images, students)
    save_students_to_excel(students=matched_students, path=NO_VECTORS_MATCHED_DATA_FILE)
    students_with_vectors = get_image_vectors(
        service=service, students=matched_students
    )
    save_students_to_excel(students=students_with_vectors)
