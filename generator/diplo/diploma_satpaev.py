# run command # nohup python3 -m flask --app diploma_final.py run --debug &

import base64
import io
import os
import re
import textwrap
import warnings
import zipfile
from datetime import datetime
from pprint import pprint

import json
import psycopg2
import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont

# Suppress DeprecationWarning for ANTIALIAS in Pillow
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load template
templateRegularEn = Image.open('./satpaev_eng_regular.jpg')
templateMasterEn = Image.open('./satpaev_eng_master.jpg')
templateRegularKzRu = Image.open('./satpaev_rukz_regular.jpg')
templateMasterKzRu = Image.open('./satpaev_rukz_master.jpg')
templateWithHonorKzRu = Image.open('./satpaev_rukz_with_honor.jpg')
templateWithHonorEn = Image.open('./satpaev_eng_with_honor.jpg')

# Set the fonts/ #Need to download them and make a way to them
font2 = ImageFont.truetype('./kztimesnewroman.ttf', size=42)
font3 = ImageFont.truetype('./Inconsolata-Medium.ttf', size=50)
font4 = ImageFont.truetype('./Alice-Regular.ttf', size=22)
font5 = ImageFont.truetype('./Alice-Regular.ttf', size=22)  # 2a4a62


def generateHash(text):
    key = "hashotnursa"
    nHash = ""
    for i in range(len(text)):
        nHash += chr((((ord(text[i]) - 48) + (ord(key[i % len(key)]) - 97)) % 26) + 97)
    return nHash


def createFolderIfNotExists(folder_path):
    if not os.path.exists(folder_path):
        try:
            # Create the folder if it doesn't exist
            os.makedirs(folder_path)
            print("Folder " + folder_path + " created successfully.")
        except Exception as e:
            print("An error occurred while creating folder " + folder_path + " : " + e)


def getMonth(lang, month_number):
    months_mapping = {
        'kz': [
            "қаңтар",
            "ақпан",
            "наурыз",
            "сәуір",
            "мамыр",
            "маусым",
            "шілдe",
            "тамыз",
            "қыркүйeк",
            "қазан",
            "қараша",
            "жeлтоқсан"
        ],
        'ru': [
            "января",
            "фeвраля",
            "марта",
            "апрeля",
            "мая",
            "июня",
            "июля",
            "августа",
            "сeнтября",
            "октября",
            "ноября",
            "дeкабря"
        ]
    }

    lang_lower = lang.lower()

    if lang_lower in months_mapping:
        months_list = months_mapping[lang_lower]
        if 1 <= month_number <= len(months_list):
            return months_list[month_number - 1]
        else:
            return "format error"
    else:
        return "Invalid language. Supported languages are 'kz' and 'ru'."


def strToDate(strDate):
    date_format = '%Y-%m-%d+%H:%M'
    return datetime.strptime(strDate, date_format)


def wrapTextToArr(text, maxSymbols=40):
    lines = []
    counter = 0
    if len(text) > maxSymbols:
        words = text.split(" ")
        line = ""
        for word in words:
            if counter + len(word) > maxSymbols:
                lines.append(line)
                counter = 0
                line = ""
            line += word + " "
            counter += len(word)
        lines.append(line)

    else:
        lines = text
    return lines


def generateSatpaevDiplomaImageEn(graduate, counter, university_id, type="Regular"):
    font2 = ImageFont.truetype('./kztimesnewroman.ttf', size=35)
    font3 = ImageFont.truetype('./DecorNormal.kz.ttf', size=40)
    font3L = ImageFont.truetype('./DecorNormal.kz.ttf', size=60)
    # number = graduate["number"]
    diploma = templateRegularEn.copy().convert('RGB')

    if graduate["with_honor"]:
        diploma = templateWithHonorEn.copy().convert('RGB')

    type = graduate["degree"] if graduate["degree"] == "Master" else "Regular"

    if type == "Master":
        diploma = templateMasterKzRu.copy().convert('RGB')

    # default regular text start
    text1 = {"en": "Non-profit join-stock company"}
    text2 = {"en": "«K.I. Satpaev Kazakh National Research Technical University»"}
    text3 = {"en": "By the Decision of the Attestation Commission"}
    text4 = {"en": "on                                           №"}
    text5 = {"en": "awarded the degree of BACHELOR"}
    text6 = {"en": "on the speciality and (or) educational program"}
    text6p2 = {"en": "Form of training"}
    text7 = {"en": "Accreditation Committee"}
    text8 = {"en": "Chairman of the Board - Rector"}
    text9p1 = {"en": "Registration"}
    text9p2 = {"en": "number"}
    text10p1 = {"en": "Republic of Kazakhstan"}
    text10p2 = {"en": "Almaty"}
    # default regular text end

    if type == "Master":
        text5 = {"en": "awarded the degree of MASTER on the speciality"}
        text6 = {"en": "and (or) educational program"}

    # Create a copy of the diploma template.
    # diploma = templateRegularEn.copy().convert('RGB')
    if type == "Master":
        diploma = templateMasterEn.copy().convert('RGB')
    # Create a draw object for the diploma.
    draw = ImageDraw.Draw(diploma)

    # Calculate the dimensions of each part
    canvas_width, canvas_height = diploma.size
    part_width = 0

    line_spacing = 20
    gapMultiplier = 12

    name_y = 550

    def putTextVertical(text, name_y, language="en", font=None, selectedColor=None, align="center",
                        offsetMultiplier=0.0):
        # #B1384B
        # #3C5B9E
        start_x = canvas_width // (9 - offsetMultiplier) + 25
        if align == "center":
            start_x = canvas_width // 3
        textArr = []
        if isinstance(text, list):
            for i in text:
                if isinstance(i, dict):
                    textArr.append(i[language])
                else:
                    textArr.append(i)
        else:
            if isinstance(text, dict):
                textArr = [text[language]]
            else:
                textArr = [text]
        color = '#9F5240' if graduate["with_honor"] else '#3C5B9E' if type == "Regular" else '#B1384B'
        selectedFont = font2
        if font:
            selectedFont = font
        if selectedColor:
            color = selectedColor
        text_lines = textArr
        name_width, name_height = draw.textsize('\n'.join(text_lines), font=selectedFont)

        part3_x = start_x + (start_x // 2)
        study_width_en, study_height_en = draw.textsize('\n'.join(text_lines), font=font2)
        text_x = part3_x - name_width // 2
        counter = 0
        for line in text_lines:
            text_width, text_height = draw.textsize(line, font=font2)
            if align == 'start':
                text_x = start_x
            else:
                text_x += (study_width_en - text_width) // 2
            draw.text((text_x, name_y), line, fill=color, font=selectedFont, align="center")
            # if len(text_lines) > 1:
            counter += 1
            name_y += (name_height / (len(text_lines))) + line_spacing
        return name_y

    name_y = putTextVertical(text1, name_y)
    name_y = putTextVertical(text2, name_y) + 20
    name_y = putTextVertical(text3, name_y, "en", font2) + 30

    temp_y = name_y
    putTextVertical(
        f"{graduate['protocol']['Day']} {graduate['protocol']['Month']['NameEn']} {graduate['protocol']['Year']}",
        temp_y, selectedColor="black", font=font3)
    name_y = putTextVertical(text4, name_y, "en", font2) + 210

    temp_y = name_y - 150
    putTextVertical(f"{graduate['name_en']}", temp_y, selectedColor="black", font=font3L)

    name_y = putTextVertical(text5, name_y, "en", font2) + (110 if type == "Regular" else - 20)
    temp_y = name_y + (60 if type == "Master" else - 120)
    name_y = putTextVertical(text6, name_y, "en", font2) + (100 if type == "Regular" else 230)
    putTextVertical(wrapTextToArr(graduate['diploma']['Issue']['AcademicDegree']['NameEn'], 30), temp_y,
                    selectedColor="black", font=font3)

    temp_y = name_y - (150 if type == "Master" else 100)
    putTextVertical(wrapTextToArr(graduate['speciality']['NameEn'], 50), temp_y, selectedColor="black", font=font3)

    temp_y = name_y
    putTextVertical(graduate['education_type']['NameEn'], temp_y, selectedColor="black", font=font3, align="start",
                    offsetMultiplier=5.2)
    name_y = putTextVertical(text6p2, name_y, "en", font2, align="start") + 100
    name_y = putTextVertical(text7, name_y, "en", font2, align="start") + 500

    temp_y = name_y
    putTextVertical("Begentaev M.", temp_y, selectedColor="black", align="start", offsetMultiplier=7.1, font=font3)
    name_y = putTextVertical(text8, name_y, "en", font2, align="start") + 100

    temp_y = name_y - 10
    temp_y = putTextVertical(
        f"{graduate['diploma']['Issue']['Day']} {graduate['diploma']['Issue']['Month']['NameEn']} {graduate['diploma']['Issue']['Year']}",
        temp_y, selectedColor="black", font=font3, align="start") - 10
    number = graduate['diploma']['Number']
    if isinstance(number, str):
        putTextVertical(number, temp_y, selectedColor="black", font=font3, align="start")

    putTextVertical(f"{graduate['diploma']['Issue']['RegNumber']}", temp_y - 15, selectedColor="black", font=font3,
                    align="start", offsetMultiplier=7.42)

    name_y = putTextVertical(text9p1, name_y, "en", font2, align="start", offsetMultiplier=7.1) - 20
    name_y = putTextVertical(text9p2, name_y, "en", font2, align="start", offsetMultiplier=7.1) + 40
    name_y = putTextVertical(text10p1, name_y, "en", font2) - 20
    name_y = putTextVertical(text10p2, name_y, "en", font2)
    if graduate["qr_base64"]:
        margin = int(diploma.width * (2.2 / 23))
        qr_pos = (diploma.width - 300 - margin, diploma.height - 950 - margin)

        img = Image.open(io.BytesIO(base64.decodebytes(bytes(graduate["qr_base64"], "utf-8"))))
        # img = qr.make_image(fill_color="black", back_color="white").resize((qr_size, qr_size), Image.ANTIALIAS)

        diploma.paste(img, qr_pos)
    if graduate['iin']:
        text = f"{graduate['iin']}"

        generatedHash = generateHash(text)
        # Add QR code
        qr_size = int(diploma.width * (2.76 / 23))

        qr = qrcode.QRCode(box_size=1, border=1)
        qr.add_data(f'https://app.ediploma.kz/3/{generatedHash}')  # do after we do portal
        qr.make(fit=True)

        img_qr = qr.make_image(fill_color="black", back_color="white").resize((qr_size, qr_size))
        margin = int(diploma.width * (2.18 / 23))
        qr_pos = (diploma.width - 530 - margin, diploma.height - 943 - margin)
        diploma.paste(img_qr, qr_pos)
    createFolderIfNotExists(f'./storage/images/{university_id}')
    diploma = diploma.resize((int(diploma.width), int(diploma.height)))
    diploma.save(f'./storage/images/{university_id}/{graduate["name_en"].replace(" ", "_")}_en.webp', 'webp',
                 optimize=True, quality=15)


def generateSatpaevDiplomaImageRuKz(graduate, counter, university_id, type="Regular"):
    font2 = ImageFont.truetype('./kztimesnewroman.ttf', size=35)
    font3 = ImageFont.truetype('./DecorNormal.kz.ttf', size=35)

    # default regular text start
    text1 = {
        "kz": "«Қ. И. Сәтбаeв атындағы Қазақ ұлттық тeхникалық",
        "ru": "Нeкoммeрчeскoe акциoнeрнoe oбщeствo"
    }
    text1p2 = {
        "kz": "зeртту унивeрситeті»",
        "ru": "«Казахский нациoнальный исслeдoватeльский тeхничeский"
    }
    text1p3 = {
        "kz": "кoммeрциялық eмeс акциoнeрлік қoғамы",
        "ru": "унивeрситeт имeни К.И. Сатпаeва»"
    }
    text2 = {
        "kz": "Аттeстаттау кoмиссиясының              жылғы «      »",
        "ru": "Рeшeниeм Аттeстациoннoй кoмиссии oт «      »"
    }
    text2p2 = {
        "kz": "шeшімімeн (№         хаттама)",
        "ru": "           гoда (прoтoкoл №          )"
    }
    text3 = {
        "kz": "мамандығы жәнe (нeмeсe) білім бeру бағдарламасы бoйынша",
        "ru": "присуждeна стeпeнь"
    }
    text4 = {
        "kz": "БАКАЛАВРЫ",
        "ru": "БАКАЛАВРА"
    }
    text4p2 = {
        "kz": "дәрeжeсі бeрілді",
        "ru": "пo спeциальнoсти и (или) oбразoватeльнoй прoграммe"
    }
    text5 = {
        "kz": "Оқыту нысаны",
        "ru": "Фoрма oбучeния"
    }
    text6 = {
        "kz": "Басқарма Төрағасы - Рeктoр",
        "ru": "«      »                                          гoда"
    }
    text7 = {
        "kz": "Прeдсeдатeль Правлeния - Рeктoр",
        "ru": "Гoрoд"
    }
    text8 = {
        "kz": "М.o",
        "ru": "Рeгистрациoнный"
    }
    text9 = {
        "kz": " жылғы «      »",
        "ru": "нoмeр"
    }
    text10 = {
        "kz": "қаласы",
        "ru": "Рeспублика Казахстан"
    }
    text11 = {
        "kz": "Тіркeу",
        "ru": "унивeрситeт имeни К.И. Сатпаeва»"
    }
    text11p2 = {
        "kz": "нөмірі",
        "ru": "унивeрситeт имeни К.И. Сатпаeва»"
    }
    text12 = {
        "kz": "Қазақстан Рeспубликасы",
        "ru": "унивeрситeт имeни К.И. Сатпаeва»"
    }
    # default regular text end
    # Create a copy of the diploma template.
    # diploma = templateRegularEn.copy().convert('RGB')
    diploma = templateRegularKzRu.copy().convert('RGB')
    if graduate["with_honor"]:
        text4 = {
            "kz": "ҮЗДІК БАКАЛАВРЫ",
            "ru": "БАКАЛАВРА С ОТЛИЧИeМ"
        }
        diploma = templateWithHonorKzRu.copy().convert('RGB')

    type = graduate["degree"] if graduate["degree"] == "Master" else "Regular"

    if type == "Master":
        text4 = {
            "kz": "МАГИСТРІ",
            "ru": "МАГИСТР"
        }
        diploma = templateMasterKzRu.copy().convert('RGB')
    # Create a draw object for the diploma.
    draw = ImageDraw.Draw(diploma)

    # Calculate the dimensions of each part
    canvas_width, canvas_height = diploma.size

    line_spacing = 5

    name_y = 310

    def putTextVertical(text, name_y, language=None, font=None, selectedColor=None, align="center",
                        offsetMultiplier=0.0, half="Left", fontSize=35):
        # #B1384B
        # #3C5B9E
        start_x = canvas_width // ((12.8 if half == "Left" else 1.75) - offsetMultiplier)
        if align == "center":
            start_x = canvas_width // (6 if half == "Left" else 2.005)
        textArr = []
        if isinstance(text, list):
            for i in text:
                if isinstance(i, dict):
                    textArr.append(i[language])
                else:
                    textArr.append(i)
        else:
            if isinstance(text, dict):
                textArr = [text[language]]
            else:
                textArr = [text]
        color = '#9F5240' if graduate["with_honor"] else '#3C5B9E' if type == "Regular" else '#B1384B'
        font2 = ImageFont.truetype('./kztimesnewroman.ttf', size=fontSize)
        selectedFont = font2
        if font:
            selectedFont = font
        if selectedColor:
            color = selectedColor
        text_lines = textArr
        name_width, name_height = draw.textsize('\n'.join(text_lines), font=selectedFont)

        part3_x = start_x + (start_x // 2)
        study_width_en, study_height_en = draw.textsize('\n'.join(text_lines), font=font2)
        text_x = part3_x - name_width // 2
        counter = 0
        for line in text_lines:
            text_width, text_height = draw.textsize(line, font=font2)
            if align == 'start':
                text_x = start_x
            else:
                text_x += (study_width_en - text_width + ((-100 if half == "Left" else -50) if counter else 0)) // 2
            draw.text((text_x, name_y), line, fill=color, font=selectedFont, align="center")
            # if len(text_lines) > 1:
            counter += 1
            name_y += (name_height / (len(text_lines))) + line_spacing
        return name_y

    temp_name_y = name_y
    name_y = putTextVertical(text1, name_y, language="kz")
    name_y = putTextVertical(text1p2, name_y, language="kz")
    name_y = putTextVertical(text1p3, name_y, language="kz")

    temp_y = name_y
    gradDate = strToDate(graduate['year'])
    putTextVertical({"kz": f"{gradDate.year}"}, temp_y, offsetMultiplier=8.75, language="kz", align="start",
                    selectedColor="black", font=font3)
    putTextVertical({"kz": f"{gradDate.day}"}, temp_y, offsetMultiplier=9.84 if gradDate.day > 9 else 9.86,
                    language="kz", align="start",
                    selectedColor="black", font=font3)
    temp_y = putTextVertical({"kz": f"{getMonth('kz', gradDate.month)}"}, temp_y, offsetMultiplier=10.08,
                             language="kz",
                             align="start", selectedColor="black", font=font3)
    putTextVertical({"kz": f"{int(graduate['protocol_number'])}"}, temp_y, offsetMultiplier=6.8, language="kz",
                    align="start",
                    selectedColor="black", font=font3)

    name_y = putTextVertical(text2, name_y, language="kz", align="start")
    name_y = putTextVertical(text2p2, name_y, language="kz", align="start") + 250
    temp_y = name_y - 200

    temp_y = putTextVertical({"kz": f"{graduate['name_kz']}"}, temp_y, language="kz", align="center",
                             selectedColor="black", font=font3) + 20
    putTextVertical(wrapTextToArr(graduate['speciality']['NameKz']), temp_y, language="kz", align="center",
                    selectedColor="black",
                    font=font3) + 20

    name_y = putTextVertical(text3, name_y, language="kz", align="start") + 70
    temp_y = name_y - 60
    putTextVertical({"ru": graduate['diploma']['Issue']['AcademicDegree']['NameKz']}, temp_y,
                    selectedColor="black",
                    language="ru", font=font3)

    name_y = putTextVertical(text4, name_y, language="kz", fontSize=43)
    name_y = putTextVertical(text4p2, name_y, language="kz") + 20

    if type == "Master":
        temp_y = name_y
        putTextVertical(wrapTextToArr(f"{graduate['study_direction']['NameKz']}", 30), temp_y - 7, language="kz",
                        offsetMultiplier=6,
                        align="start",
                        selectedColor="black", font=font3)

        name_y = putTextVertical({"kz": "Бағыты"}, name_y, language="kz", align="start") + 70

    temp_y = name_y
    putTextVertical(wrapTextToArr(f"{graduate['education_type']['NameKz']}", ), temp_y, language="kz",
                    offsetMultiplier=7,
                    align="start", selectedColor="black", font=font3)

    name_y = putTextVertical(text5, name_y, language="kz", align="start") + (20 if type == "Master" else 140)

    name_y = putTextVertical(text6, name_y, language="kz", align="start")

    temp_y = name_y
    putTextVertical({"kz": "Бeгeнтаeв М.М."}, temp_y, language="kz", offsetMultiplier=9.35,
                    align="start", selectedColor="black", font=font3)

    name_y = putTextVertical(text7, name_y, language="kz", align="start") + 100

    name_y = putTextVertical(text8, name_y, language="kz", align="start") + 40

    temp_y = name_y
    tempDay = graduate['diploma']['Issue']['Day']
    tempMonth = graduate['diploma']['Issue']['Month']['NameKz']
    tempYear = graduate['diploma']['Issue']['Year']

    putTextVertical({"ru": f"{tempYear}"}, temp_y, font=font3, selectedColor="black", language="ru",
                    align="start")
    putTextVertical({"ru": f"{tempDay}"}, temp_y, font=font3, selectedColor="black", language="ru",
                    align="start", offsetMultiplier=6.98 if tempDay < 10 else 6.9)
    putTextVertical({"ru": f"{tempMonth}"}, temp_y, font=font3, selectedColor="black", language="ru",
                    align="start", offsetMultiplier=7.8)

    name_y = putTextVertical(text9, name_y, language="kz", align="start", offsetMultiplier=4) + 35

    temp_y = name_y

    putTextVertical({"kz": f"Алматы"}, temp_y, language="kz",
                    align="start", selectedColor="black", font=font3)

    name_y = putTextVertical(text10, name_y, language="kz", align="start", offsetMultiplier=5.5)
    name_y = putTextVertical(text11, name_y, language="kz", align="start", offsetMultiplier=9.5)
    name_y = putTextVertical(text11p2, name_y, language="kz", align="start", offsetMultiplier=9.5) + 10
    name_y = putTextVertical(text12, name_y, language="kz")

    name_y = temp_name_y
    name_y = putTextVertical(text1, name_y, half="Right", language="ru")
    name_y = putTextVertical(text1p2, name_y, half="Right", language="ru")
    name_y = putTextVertical(text1p3, name_y, half="Right", language="ru") + 10
    temp_y = name_y

    name_y = putTextVertical(text2, name_y, half="Right", language="ru", align="start") + 10
    gradDate = strToDate(graduate['year'])

    putTextVertical({"ru": f"{gradDate.day}"}, temp_y, half="Right",
                    offsetMultiplier=0.5159 if gradDate.day > 9 else 0.52, language="ru",
                    align="start", selectedColor="black", font=font3)
    putTextVertical({"ru": f"{getMonth('ru', gradDate.month)}"}, temp_y, half="Right", offsetMultiplier=0.56,
                    language="ru",
                    align="start", selectedColor="black", font=font3)
    temp_y = name_y

    putTextVertical({"ru": f"{gradDate.year}"}, temp_y, half="Right", language="ru",
                    align="start", offsetMultiplier=0, selectedColor="black", font=font3)

    putTextVertical({"ru": f"{int(graduate['protocol_number'])}"}, temp_y, half="Right", language="ru",
                    align="start", offsetMultiplier=0.345, selectedColor="black", font=font3)

    name_y = putTextVertical(text2p2, name_y, half="Right", language="ru", align="start") + 140

    temp_y = name_y - 100
    putTextVertical({"ru": f"{graduate['name_ru']}"}, temp_y, language="ru", align="center",
                    selectedColor="black", half="Right", font=font3)

    name_y = putTextVertical(text3, name_y, half="Right", language="ru")
    name_y = putTextVertical(text4, name_y, half="Right", language="ru", fontSize=43) + 20
    name_y = putTextVertical({"ru": graduate['diploma']['Issue']['AcademicDegree']['NameRu']}, name_y, font=font3,
                             selectedColor="black",
                             half="Right", language="ru") + 20
    name_y = putTextVertical(text4p2, name_y, half="Right", language="ru") + 150

    temp_y = name_y - 130
    putTextVertical(wrapTextToArr(graduate['speciality']['NameRu']), temp_y, language="ru", align="center",
                    selectedColor="black", half="Right", font=font3)
    if type == "Master":
        temp_y = name_y
        name_y = putTextVertical({"ru": f"Направлeниe"}, name_y, language="ru",
                                 half="Right", align='start', font=font2) + 30
        putTextVertical(wrapTextToArr(f"{graduate['study_direction']['NameRu']}", 30), temp_y, language="ru",
                        offsetMultiplier=0.28, align="start",
                        selectedColor="black", half="Right", font=font3)
    name_y += (50 if type == 'Master' else 130)
    temp_y = name_y
    putTextVertical({"ru": f"{graduate['education_type']['NameRu']}"}, temp_y, language="ru", align="start",
                    offsetMultiplier=0.28,
                    selectedColor="black", half="Right", font=font3)

    name_y = putTextVertical(text5, name_y, half="Right", language="ru", align="start") + 20
    temp_y = name_y
    name_y = putTextVertical(text6, name_y, half="Right", language="ru", align="start") + 20
    tempDay = graduate['diploma']['Issue']['Day']
    tempMonth = graduate['diploma']['Issue']['Month']['NameRu']
    tempYear = graduate['diploma']['Issue']['Year']
    putTextVertical({"ru": f"{tempDay}"}, temp_y, half="Right", font=font3, selectedColor="black", language="ru",
                    align="start", offsetMultiplier=0.04 if tempDay < 10 else 0.032)
    putTextVertical({"ru": f"{tempMonth}"}, temp_y, half="Right", font=font3, selectedColor="black", language="ru",
                    align="start", offsetMultiplier=0.15)
    putTextVertical({"ru": f"{tempYear}"}, temp_y, half="Right", font=font3, selectedColor="black", language="ru",
                    align="start", offsetMultiplier=0.28)
    temp_y = name_y
    putTextVertical({"ru": f"Алматы"}, temp_y, language="ru", align="start",
                    selectedColor="black", half="Right", font=font3, offsetMultiplier=0.15)
    name_y = putTextVertical(text7, name_y, half="Right", language="ru", align="start") + 220
    name_y = putTextVertical(text8, name_y, half="Right", language="ru", align="start", offsetMultiplier=.37)
    temp_y = name_y
    name_y = putTextVertical(text9, name_y, half="Right", language="ru", align="start", offsetMultiplier=.37) + 10

    number = graduate['diploma']['Number']
    if isinstance(number, str):
        putTextVertical({"ru": f"{number}"}, temp_y, half="Right", language="ru", font=font3, selectedColor="black",
                        align="start")
        putTextVertical({"ru": f"{number}"}, temp_y, language="ru", font=font3, selectedColor="black",
                        align="start")

    putTextVertical(str(graduate['diploma']['Issue']['RegNumber']), temp_y, language="ru", font=font3,
                    selectedColor="black",
                    align="start", offsetMultiplier=10)
    putTextVertical(str(graduate['diploma']['Issue']['RegNumber']), temp_y, half="Right", language="ru", font=font3,
                    selectedColor="black",
                    align="start", offsetMultiplier=0.565)

    name_y = putTextVertical(text10, name_y, half="Right", language="ru")

    if graduate["qr_base64"]:
        qr_size = int(diploma.width * (2.6 / 23))
        margin = int(diploma.width * (1.2 / 23))
        qr_pos = (diploma.width - qr_size - margin, diploma.height - qr_size - 120 - margin)

        img = Image.open(io.BytesIO(base64.decodebytes(bytes(graduate["qr_base64"], "utf-8"))))
        # img = qr.make_image(fill_color="black", back_color="white").resize((qr_size, qr_size), Image.ANTIALIAS)

        diploma.paste(img, qr_pos)
    if graduate['iin']:
        text = f"{graduate['iin']}"

        generatedHash = generateHash(text)
        # Add QR code
        qr_size = int(diploma.width * (2.13 / 23))

        qr = qrcode.QRCode(box_size=1, border=3, version=5)
        qr.add_data(f'https://app.ediploma.kz/3/{generatedHash}')  # do after we do portal
        qr.make(fit=True)

        img_qr = qr.make_image(fill_color="black", back_color="white").resize((qr_size, qr_size))
        margin = int(diploma.width * (2.07 / 23))
        qr_pos = (diploma.width - 200 - margin, diploma.height - 550 - margin)
        diploma.paste(img_qr, qr_pos)
    createFolderIfNotExists(f'./storage/images/{university_id}')
    diploma = diploma.resize((int(diploma.width), int(diploma.height)))
    diploma.save(f'./storage/images/{university_id}/{graduate["name_en"].replace(" ", "_")}_kz_ru.webp', 'webp',
                 optimize=True, quality=15)


def grade_to_gpa(grade):
    if grade >= 90:
        return 4.0
    elif grade >= 85:
        return 3.7
    elif grade >= 80:
        return 3.3
    elif grade >= 75:
        return 3.0
    elif grade >= 70:
        return 2.7
    elif grade >= 65:
        return 2.3
    elif grade >= 60:
        return 2.0
    elif grade >= 55:
        return 1.7
    elif grade >= 50:
        return 1.3
    elif grade >= 0:
        return 0.0
    else:
        return None


def createTableIfNotExists(cursor):
    try:
        # Define the SQL statement to create the table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS upload_diplomas (
            id SERIAL PRIMARY KEY,
            hash_id varchar(12),
            value JSONB,
            university_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deleted_at TIMESTAMP
        )
        """
        # Execute the SQL statement
        cursor.execute(create_table_query)
    except psycopg2.Error as e:
        print("Error creating the table:", e)


def connectDatabase():
    # Database connection parameters
    host = "109.248.170.239"
    port = 5432
    database = "postgres"
    user = "postgres"
    password = "7Vow1e2v0v7x"
    # Establish a connection to the database
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        print('connected')
        # Create a cursor object
        cursor = connection.cursor()
        return connection, cursor

    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        return None, None


def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname=arcname)


def parseFromApi(university_id=4):
    connection, cursor = connectDatabase()
    # if connection is None or cursor is None:
    #     return {"error": "Error connecting to the database."}
    # else:
    #     createTableIfNotExists(cursor)
    url = "https://extapi.satbayev.university/diploma/1.0.1/getAll"
    fullMetadata = "["
    # n = 73
    n = 1
    for i in range(n):
        # for i in range(73):
        # for i in range(73):
        res = requests.post(url=url, headers={"Authorization": "Basic ZGlwbG9tYV9uZnQ6RGQxMjM0NTY="}, timeout=60, json={
            "PageId": i
        })
        if res.status_code == 200:
            body = json.loads(res.content)["result"]["items"]
            for item in body:
                if item["Status"] == "Graduated":
                    jsonItem = {
                        "student_id": item["StudentID"],
                        "name_en": item["FIO"]["NameEn"],
                        "name_kz": item["FIO"]["NameKz"].replace('Ə', 'Ә').replace('ə', 'ә'),
                        "name_ru": item["FIO"]["NameRu"].replace('Ə', 'Ә').replace('ə', 'ә'),
                        "speciality": item["Speciality"],
                        "speciality_en": item["Speciality"]["NameEn"],
                        "speciality_kz": item["Speciality"]["NameKz"],
                        "speciality_ru": item["Speciality"]["NameRu"],
                        "email": item["Email"] if item["Email"] and isinstance(item["Email"], str) else None,
                        "grant": item["GrantTitle"] if item["GrantTitle"] and isinstance(item["GrantTitle"],
                                                                                         str) else None,
                        "gender": "мужской" if item["Sex"] == "M" else "жeнский",
                        "city": item["City"] if item["City"] and isinstance(item["City"], str) else None,
                        "nationality": item["Nationality"] if item["Nationality"] and isinstance(item["Nationality"],
                                                                                                 str) else None,
                        "iin": item["IIN"],
                        "phone": item["Phone"] if item["Phone"] and isinstance(item["Phone"], str) else None,
                        "gpa": item["GPA"] if item["GPA"] and isinstance(item["GPA"], float) else None,
                        "region": item["Region"] if item["Region"] and isinstance(item["Region"], str) else None,
                        "date_of_birth": item["BirthDate"],
                        "with_honor": False if item["WithHonor"] == "N" else True,
                        "protocol": item['Protocol'],
                        "year": item["Protocol"]["Date"],
                        "protocol_number": item["Protocol"]["Number"],

                        "education_type": item["EducationType"],
                        "study_direction": item["DirectionStudy"],

                        "degree": "Master" if item["DegreeType"] == 2 else "Bachelor",
                        "qr_base64": item["QRBase64"],
                        "diploma": item['Diploma'],
                    }
                    print(jsonItem['name_en'])
                    generateSatpaevDiplomaImageEn(jsonItem, 1, 3)
                    generateSatpaevDiplomaImageRuKz(jsonItem, 1, 3)

                    # metadata = jsonItem
                    # Convert the dictionary into a JSON string
                    # metadata_json = json.dumps(metadata, indent=4, ensure_ascii=False)
                    # fullMetadata += metadata_json + ("" if item == body[-1] and i == n else ",")
                    # Create a new file with the JSON data
                    # 1 filename = f"./json/{jsonItem['name_en']}.json"
                    # 1 with open(filename, "w", encoding="utf-8") as f:
                    # 1 f.write(metadata_json)
                    # break
                    # Insert metadata into the database
                    # try:
                    #     iin = f"{jsonItem['iin']}"
                    #
                    #     shorthash = generateHash(iin)
                    #     print("parse/ ", jsonItem['name_en'])
                    #
                    #     # Check if the record exists in the database
                    #     cursor.execute("SELECT id FROM upload_diplomas WHERE hash_id = %s AND deleted_at IS NULL",
                    #                    (shorthash,))
                    #     existing_record = cursor.fetchone()
                    #
                    #     if existing_record and iin:
                    #         # If the record exists, update it
                    #         cursor.execute(
                    #             "UPDATE upload_diplomas SET value = %s, university_id = %s WHERE hash_id = %s AND deleted_at IS NULL",
                    #             (metadata_json, university_id, shorthash)
                    #         )
                    #     else:
                    #         cursor.execute(
                    #             "INSERT INTO upload_diplomas (value, university_id, hash_id) VALUES (%s, %s, %s)",
                    #             (metadata_json, university_id, shorthash)
                    #         )
                    #     connection.commit()
                    # except psycopg2.Error as e:
                    #     print("Error inserting data into the database:", e)
    fullMetadata += "]"
    createFolderIfNotExists(f"storage/jsons/{university_id}")
    with open(f"storage/jsons/{university_id}/fullMetadata.json", "w", encoding="utf-8") as f:
        f.write(fullMetadata)
    try:
        # createFolderIfNotExists(f"storage/archives")
        # zip_folder(folder_path=f"storage/images/{university_id}", zip_path=f"storage/archives/{university_id}.zip")
        return f"http://generator.ediploma.kz/get-file/archives/{university_id}.zip"
    except Exception as e:
        return {"error": str(e)}, 500


def diplomaSave(university_id):
    f = open(f'./storage/jsons/{university_id}/fullMetadata-refactored.json', 'r')

    body = json.loads(f.read())

    ignoreAttr = [
        "name_en",
        "name_ru",
        "name_kz",
        "gpa",
        "iin",
        "speciality_en",
        "speciality_kz",
        "speciality_ru",
        "speciality",
        "protocol",
        "education_type",
        "study_direction",
        "year",
    ]
    connection, cursor = connectDatabase()
    flag = False
    for item in body:

        # if not flag and item['name_en'] == 'Nurzhigitova Alina':
        #     flag = True
        # if not flag:
        #     print(item['name_en'])
        #     continue

        data = {'image': "https://generator.ediploma.kz/get-file/images/3/" + "_".join(
            item['name_en'].split(" ")) + "_kz_ru.jpeg, https://generator.ediploma.kz/get-file/images/3/" + "_".join(
            item['name_en'].split(" ")) + "_en.jpeg"}

        contentFields = {}
        attributes = item

        if item["diploma"]["Number"]:
            contentFields['Number'] = item["diploma"]["Number"]

        data['year'] = item['diploma']['Issue']['Year']
        for key, value in attributes.items():
            if key == 'number':
                continue

            if key in ignoreAttr:
                data[key] = value
            else:
                contentFields[key] = value

        # Construct and execute the SQL query to insert data into
        # the database
        iin = item['iin']
        print(iin)
        query = (
            f"select id from diplomas where iin = '{iin}'"
        )

        cursor.execute(query)

        # Retrieve the ID of the inserted record
        diploma_id = cursor.fetchone()
        if not diploma_id:
            query = (
                "INSERT INTO diplomas("
                "name_en, name_ru, name_kz, university_id, year, "
                "speciality_en, speciality_ru, speciality_kz, image, gpa, iin, visibility"
                ") "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "RETURNING id"
            )
            values = (
                item["name_en"], item["name_ru"], item["name_kz"],
                university_id, data["year"],
                item["speciality_en"], item["speciality_ru"],
                item["speciality_kz"],
                data["image"],
                item["gpa"],
                item["iin"],
                False,
            )
            cursor.execute(query, values)
            diploma_id = cursor.fetchone()[0]
        else:
            diploma_id = diploma_id[0]
        connection.commit()
        # inserting additional fields
        for key, val in contentFields.items():
            query = (
                "INSERT INTO content_fields(type, value, content_id) "
                "VALUES (%s, %s, %s)"
            )
            val = json.dumps(val, ensure_ascii=False) if isinstance(val, dict) else val
            values = ("diploma_" + key, json.dumps(val, ensure_ascii=False), diploma_id)
            cursor.execute(query, values)

        connection.commit()


parseFromApi()
# diplomaSave(3)
