from contextlib import contextmanager

import os

from ai_edge_litert.interpreter import Interpreter

from ml.model import MlModel

ml_model: MlModel = dict()


@contextmanager
def initialize():
    global ml_model
    # !This model is for 192 dimensions
    model_path = "ml/mobile_face_net.tflite"

    if not os.path.exists(model_path):
        raise Exception(f"Model file '{model_path}' not found! Check path.")

    try:
        ml_model["interpreter"] = Interpreter(model_path=model_path)
        ml_model["interpreter"].allocate_tensors()
        ml_model["input_details"] = ml_model["interpreter"].get_input_details()
        ml_model["output_details"] = ml_model["interpreter"].get_output_details()
        yield
    except Exception as e:
        raise e
    finally:
        ml_model.clear()
