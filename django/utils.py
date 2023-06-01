import json
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
from mtranslate import translate
from .models import Diploma
import io


def generate_diploma(data):
    # Put the diploma generation code here
    # ...
    # Save the diploma as a new image file.
    buffer = io.BytesIO()
    diploma.save(buffer, format='JPEG')
    buffer.seek(0)

    # Create a new Diploma object
    diploma_obj = Diploma(
        name=name,
        degree_en=degree_en,
        degree_ru=degree_ru,
        degree_kz=degree_kz,
        study_time_ru=study_time_ru,
        study_time_en=study_time_en,
        study_time_kz=study_time_kz,
        diploma_image=ImageFile(buffer, name=f"{name}_diploma.jpeg"),
        json_data=row_dict
    )

    return diploma_obj