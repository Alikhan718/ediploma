import json
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
import config
from config import *
from mtranslate import translate

data = pd.read_excel('data.xlsx')
template = Image.open('diploma_template.png')

font1 = ImageFont.truetype('arial', size=35)
font2 = ImageFont.truetype('arial', size=20)
font3 = ImageFont.truetype('arial', size=13)

for index, row in data.iterrows():
    # Get the student's name and degree information from the Excel data.
    name = row['ФИО']

    degree_en = row['Специальность']
    degree_ru = translate(degree_en, to_language="ru")
    degree_kz = translate(degree_en, to_language="kk")

    study_time_ru = row['Форма обучения']
    if study_time_ru == "Очная":
        study_time_kz = "Күндізгі"
        study_time_en = "Full-time"
    else:
        study_time_kz = "Сырттай оқу"
        study_time_en = "Part-time"


    # Create a copy of the diploma template.
    diploma = template.copy()

    # Create a draw object for the diploma.
    draw = ImageDraw.Draw(diploma)

    # Draw the student's name and degree information on the diploma.
    draw.text((390, 290), name, font=font1, fill='#0f3f5a')

    draw.text((820, 400), degree_en, font=font2, fill='#5c92c7')
    draw.text((420, 400), degree_ru, font=font2, fill='#5c92c7')
    draw.text((80, 340), degree_kz, font=font2, fill='#5c92c7')

    draw.text((220, 490), study_time_kz, font=font3, fill='#5c92c7')
    draw.text((593, 490), study_time_ru, font=font3, fill='#5c92c7')
    draw.text((943, 490), study_time_en, font=font3, fill='#5c92c7')

    # Add QR code
    qr = qrcode.QRCode(box_size=8)
    qr.add_data(name)
    qr.make()
    img_qr = qr.make_image()
    pos = (diploma.size[0] - img_qr.size[0], diploma.size[1] - img_qr.size[1])
    diploma.paste(img_qr, pos)

    # Save the diploma as a new image file.
    diploma.save(f'Diplomas/{name}_diploma.jpeg')

    # Create a dictionary with the row data
    row_dict = row.to_dict()

    # Convert the dictionary into a JSON string
    row_json = json.dumps(row_dict)

