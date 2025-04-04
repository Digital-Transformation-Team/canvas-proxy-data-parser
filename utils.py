import numpy as np
import os
import pandas as pd

from constants import GEN_DATA_FOLDER, MATCHED_DATA_FILE, NO_GF_DATA_FILE
from models import Student


def initialize():
    if not os.path.exists(GEN_DATA_FOLDER):
        os.mkdir(GEN_DATA_FOLDER)


def replace_kazakh_chars(text: str) -> str:
    replacements = {
        "Ә": "А",
        "ә": "а",
        "Ғ": "Г",
        "ғ": "г",
        "Қ": "К",
        "қ": "к",
        "Ң": "Н",
        "ң": "н",
        "Ө": "О",
        "ө": "о",
        "Ұ": "У",
        "ұ": "у",
        "Ү": "У",
        "ү": "у",
        "Һ": "Х",
        "һ": "х",
        "І": "И",
        "і": "и",
    }

    return "".join(replacements.get(char, char) for char in text)


def save_unmatched_to_excel(no_gf_images, no_gf_students):
    """Сохраняет ненайденные изображения и студентов в один Excel-файл на разные листы"""

    df_images = pd.DataFrame({"Image Name": no_gf_images})
    df_students = pd.DataFrame({"Student Name": list(no_gf_students)})

    with pd.ExcelWriter(NO_GF_DATA_FILE, engine="xlsxwriter") as writer:
        df_images.to_excel(writer, sheet_name="no gf images", index=False)
        df_students.to_excel(writer, sheet_name="no gf students", index=False)


def save_students_to_excel(students: list[Student], path: str = MATCHED_DATA_FILE):
    """Сохраняет ненайденные изображения и студентов в один Excel-файл на разные листы"""

    df_students = pd.DataFrame(
        {
            "Origin Name": [student.origin_name for student in students],
            "Image ID": [student.image_id for student in students],
            "Image Vector": [student.image_vector for student in students],
            "Canvas Name": [student.canvas_name for student in students],
            "Canvas Login": [student.canvas_login for student in students],
            "Canvas ID": [student.canvas_id for student in students],
        }
    )

    with pd.ExcelWriter(path, engine="xlsxwriter") as writer:
        df_students.to_excel(writer, sheet_name="Student data", index=False)


def retrieve_students_from_excel() -> list[Student]:
    df = pd.read_excel(MATCHED_DATA_FILE)

    students = []
    for _, row in df.iterrows():
        image_vector = row.get("Image Vector")
        if isinstance(image_vector, str):
            try:
                image_vector = image_vector.strip("[]")
                image_vector = np.fromstring(image_vector, sep=" ")
            except Exception as e:
                raise e

        student = Student(
            name=row["Origin Name"],
            origin_name=row["Origin Name"],
            canvas_name=row["Canvas Name"],
            canvas_login=row["Canvas Login"],
            canvas_id=row["Canvas ID"],
            image_id=row.get("Image ID"),
            image_vector=image_vector,
        )
        students.append(student)

    return students
