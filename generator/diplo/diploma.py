import json
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
import config
from config import *
from mtranslate import translate
import openpyxl

# Read the Excel data
data = pd.read_excel('data.xlsx')
template = Image.open('diploma_template.png')
workbook = openpyxl.load_workbook('reestr.xlsx')
sheet = workbook['Бакалавриат']

# Set the fonts
font1 = ImageFont.truetype('times', size=35)
font2 = ImageFont.truetype('times', size=18)
font3 = ImageFont.truetype('times', size=11)

# Iterate over each row in the data
for index, row in data.iterrows():
    # Create a copy of the diploma template.
    diploma = template.copy()

    # Create a draw object for the diploma.
    draw = ImageDraw.Draw(diploma)

    # Get the student's name and degree information from the Excel data.
    name = row['ФИО'].upper()
    study_time_ru = row['Форма обучения']

    # Translate study time values
    if study_time_ru == "Очная":
        study_time_ru = "ФОРМА ОБУЧЕНИЯ ОЧНАЯ"
        study_time_kz = "ОҚЫТУ НЫСАНЫ КҮНДІЗГІ"
        study_time_en = "FORM OF TRAINING FULL-TIME"
    else:
        study_time_ru = "ФОРМА ОБУЧЕНИЯ ЗАОЧНАЯ"
        study_time_kz = "ОҚЫТУ НЫСАНЫ СЫРТТАЙ ОҚУ"
        study_time_en = "FORM OF TRAINING PART-TIME"

    # Get the degree information from the corresponding columns in the Excel sheet
    degree_ru = row['Специальность']
    degree_en = ""
    degree_kz = ""
    for i in sheet.iter_rows(min_row=2, values_only=True):
        if i[0] == degree_ru:
            degree_en = i[2].upper()  # English value in column C
            degree_kz = i[1].upper()  # Kazakh value in column B
            degree_ru = degree_ru.upper()
            break

    text_height = int(diploma.height * (0.5))
    # Calculate the positions for degree texts
    text_1_pos = (diploma.width // 6, int(diploma.height * (0.47)))
    text_2_pos = (diploma.width // 2, text_height)
    text_3_pos = (diploma.width * 5 // 6, text_height)


    text_1_pos = (text_1_pos[0] - draw.textsize(degree_kz, font=font2)[0] // 2, text_1_pos[1])
    text_2_pos = (text_2_pos[0] - draw.textsize(degree_ru, font=font2)[0] // 2, text_2_pos[1])
    text_3_pos = (text_3_pos[0] - draw.textsize(degree_en, font=font2)[0] // 2, text_3_pos[1])

    # Draw the degree texts on the diploma with the fixed height
    draw.text(text_1_pos, degree_kz, font=font2, fill='#5c92c7')
    draw.text(text_2_pos, degree_ru, font=font2, fill='#5c92c7')
    draw.text(text_3_pos, degree_en, font=font2, fill='#5c92c7')

    # Calculate the position for the name
    name_width, name_height = draw.textsize(name, font=font1)
    name_pos = ((diploma.width - name_width) // 2, diploma.height // 3 - name_height // 2)




    # Draw the name on the diploma
    draw.text(name_pos, name, font=font1, fill='#0f3f5a')


    # Add text for high GPA if applicable
    text_height = int(diploma.height * (8 / 14))
    if row['GPA'] >= 3.5:
        text_1_pos = (diploma.width // 6, text_height)
        text_2_pos = (diploma.width // 2, text_height)
        text_3_pos = (diploma.width * 5 // 6, text_height)

        text_1_pos = (text_1_pos[0] - draw.textsize("ҮЗДІК", font=font2)[0] // 2, text_1_pos[1])
        text_2_pos = (text_2_pos[0] - draw.textsize("С ОТЛИЧИЕМ", font=font2)[0] // 2, text_2_pos[1])
        text_3_pos = (text_3_pos[0] - draw.textsize("WITH HONORS", font=font2)[0] // 2, text_3_pos[1])

        draw.text(text_1_pos, "ҮЗДІК", font=font2, fill='#5c92c7')
        draw.text(text_2_pos, "С ОТЛИЧИЕМ", font=font2, fill='#5c92c7')
        draw.text(text_3_pos, "WITH HONORS", font=font2, fill='#5c92c7')

    # Add study time texts
    text_height_2 = int(diploma.height * (2 / 3))
    text_width = int(diploma.width * (22 / 23))

    text_1_pos = (text_width // 6, text_height_2)
    text_2_pos = (diploma.width // 2, text_height_2)
    text_3_pos = (diploma.width * 5 // 6, text_height_2)

    study_time_kz_width, study_time_kz_height = draw.textsize(study_time_kz, font=font3)
    text_1_pos = (text_1_pos[0] - study_time_kz_width // 2, text_1_pos[1])

    study_time_ru_width, study_time_ru_height = draw.textsize(study_time_ru, font=font3)
    text_2_pos = (text_2_pos[0] - study_time_ru_width // 2, text_2_pos[1])

    study_time_en_width, study_time_en_height = draw.textsize(study_time_en, font=font3)
    text_3_pos = (text_3_pos[0] - study_time_en_width // 2, text_3_pos[1])

    draw.text(text_1_pos, study_time_kz, font=font3, fill='#5c92c7')
    draw.text(text_2_pos, study_time_ru, font=font3, fill='#5c92c7')
    draw.text(text_3_pos, study_time_en, font=font3, fill='#5c92c7')

    # Add QR code
    qr_size = int(diploma.width * (1.6 / 23))

    qr = qrcode.QRCode(box_size=1)
    qr.add_data(f'ediplomas/kbtu/{name}') # do after we do portal
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white").resize((qr_size, qr_size), Image.ANTIALIAS)
    margin = int(diploma.width * (0.5 / 23))
    qr_pos = (diploma.width - qr_size - margin, diploma.height - qr_size - margin)

    diploma.paste(img_qr, qr_pos)

    # Save the diploma as a new image file.
    diploma.save(f'Diplomas/{name}_diploma.jpeg')

    # CREATION OF JSON FILES
    # Create a dictionary with the row data
    row_dict = row.to_dict()

    # Convert the dictionary into a JSON string
    row_json = json.dumps(row_dict)

    # Create a new file with the JSON data
    filename = f'json/{name}.json'
    with open(filename, 'w') as f:
        f.write(row_json)
