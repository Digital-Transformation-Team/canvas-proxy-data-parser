import cv2
import numpy as np

from ml import ml_model

MIME_TYPE_TO_FORMAT = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/bmp": ".bmp",
    "image/tiff": ".tiff",
    "image/webp": ".webp",
}


def preprocess_image(image: bytes) -> np.ndarray:
    img_array = np.frombuffer(image, dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (112, 112))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32)
    img = (img - 127.5) / 128.0
    img = np.expand_dims(img, axis=0)
    return img


def get_face_embedding(image: bytes) -> np.ndarray:
    img = preprocess_image(image)
    interpreter, input_details, output_details = (
        ml_model["interpreter"],
        ml_model["input_details"],
        ml_model["output_details"],
    )
    interpreter.set_tensor(input_details[0]["index"], img)
    interpreter.invoke()
    encoding = interpreter.get_tensor(output_details[0]["index"])
    return np.squeeze(encoding)


def image_to_bytes_cv2(image_path: str, content_type: str) -> bytes:
    img = cv2.imread(image_path)

    format_ext = MIME_TYPE_TO_FORMAT.get(content_type)
    if format_ext is None:
        raise ValueError(f"Unsupported content-type: {content_type}")

    _, buffer = cv2.imencode(format_ext, img)
    return buffer.tobytes()


def image_to_bytes(image_path: str) -> bytes:
    with open(image_path, "rb") as f:
        return f.read()

def get_image_embedding(image_path: str, content_type: str) -> np.ndarray:
    b = image_to_bytes(image_path=image_path)
    return get_face_embedding(image=b)
