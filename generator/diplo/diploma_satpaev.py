# run command # nohup python3 -m flask --app diploma_final.py run --debug &

import re
import textwrap
import warnings

import json
import openpyxl
import qrcode
from PIL import Image, ImageDraw, ImageFont
from flask import request
from datetime import datetime

# Suppress DeprecationWarning for ANTIALIAS in Pillow
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load template
templateRegularEn = Image.open('./satpaev_eng_regular.jpg')
templateMasterEn = Image.open('./satpaev_eng_master.jpg')
templateRegularKzRu = Image.open('./satpaev_rukz_regular.jpg')
templateMasterKzRu = Image.open('./satpaev_rukz_master.jpg')

# Set the fonts/ #Need to download them and make a way to them
font2 = ImageFont.truetype('./kztimesnewroman.ttf', size=42)
font3 = ImageFont.truetype('./Inconsolata-Medium.ttf', size=50)
font4 = ImageFont.truetype('./Alice-Regular.ttf', size=22)
font5 = ImageFont.truetype('./Alice-Regular.ttf', size=22)  # 2a4a62


def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|\n\t]', '', filename)


def draw_distinction_text(draw, font, part_x, part_y, text_lines, color):
    filtered_lines = [line for line in text_lines if line != "NONE"]
    text_width, text_height = draw.textsize('\n'.join(filtered_lines), font=font)
    text_x = part_x - text_width // 2
    text_y = part_y - text_height // 2
    for line in filtered_lines:
        line_width, line_height = draw.textsize(line, font=font)
        line_x = text_x + (text_width - line_width) // 2
        draw.text((line_x, text_y), line, fill=color, font=font)
        text_y += line_height


def wrap_text_with_newlines(text, width):
    lines = []
    for part in text.split("\n"):
        lines.extend(textwrap.wrap(part, width=width))
    return lines


def getMonth(lang, month_number):
    months_mapping = {
        'kz': [
            "қаңтар",
            "ақпан",
            "наурыз",
            "сәуір",
            "мамыр",
            "маусым",
            "шілде",
            "тамыз",
            "қыркүйек",
            "қазан",
            "қараша",
            "желтоқсан"
        ],
        'ru': [
            "января",
            "февраля",
            "марта",
            "апреля",
            "мая",
            "июня",
            "июля",
            "августа",
            "сентября",
            "октября",
            "ноября",
            "декабря"
        ]
    }

    lang_lower = lang.lower()

    if lang_lower in months_mapping:
        months_list = months_mapping[lang_lower]
        if 1 <= month_number <= len(months_list):
            return months_list[month_number - 1]
        else:
            return f"Invalid month number. Please provide a number between 1 and {len(months_list)}."
    else:
        return "Invalid language. Supported languages are 'kz' and 'ru'."


def strToDate(strDate) -> datetime:
    date_format = '%Y-%m-%d+%H:%M'
    return datetime.strptime(strDate, date_format)


def generateSatpaevDiplomaImageEn(graduate, counter, university_id, type="Regular"):
    # number = graduate["number"]

    # default regular text start
    text1 = {"en": "Non-profit join-stock company"}
    text2 = {"en": "«K.I. Satpaev Kazakh National Research Technical University»"}
    text3 = {"en": "By the Decision of the Attestation Commission"}
    text4 = [
        {"en": "on"},
        "№"
    ]
    text5 = {"en": "awarded the degree of BACHELOR"}
    text6 = {"en": "on the speciality and (or) educational program"}
    text7 = {"en": "Accreditation Committee"}
    text8 = {"en": "Chairman of the Board - Rector ______________"}
    text9p1 = {"en": "Registration"}
    text9p2 = {"en": "number"}
    text10p1 = {"en": "Republic of Kazakhstan"}
    text10p2 = {"en": "Almaty"}
    # default regular text end

    if type == "Master":
        text1 = {"en": "Non-profit join-stock company"}
        text2 = {"en": "«K.I. Satpaev Kazakh National Research Technical University»"}
        text3 = {"en": "By the Decision of the Attestation Commission"}
        text4 = [
            {"en": "on"},
            "№"
        ]
        text5 = {"en": "awarded the degree of MASTER on the speciality"}
        text6 = {"en": "and (or) educational program"}
        text7 = {"en": "Accreditation Committee"}
        text8 = {"en": "Chairman of the Board - Rector ______________"}
        text9p1 = {"en": "Registration"}
        text9p2 = {"en": "number"}
        text10p1 = {"en": "Republic of Kazakhstan"}
        text10p2 = {"en": "Almaty"}

    # Create a copy of the diploma template.
    # diploma = templateRegularEn.copy().convert('RGB')
    diploma = templateRegularEn.copy().convert('RGB')
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
        start_x = canvas_width // (9 - offsetMultiplier)
        if align == "center":
            start_x = canvas_width // 3
        print("length of array: " + str(len(text)))
        textArr = []
        if len(text) > 1:
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
        color = '#3C5B9E' if type == "Regular" else '#B1384B'
        selectedFont = font2
        if font:
            selectedFont = font
        if selectedColor:
            color = selectedColor
        text_lines = textArr
        name_width, name_height = draw.textsize('\n'.join(text_lines), font=selectedFont)

        part3_x = start_x + (start_x // 2)
        study_width_en, study_height_en = draw.textsize(' '.join(text_lines), font=font2)
        text_x = part3_x - name_width // 2 - ((len(text_lines) - 1) * study_width_en * 3)
        for i in range(len(text_lines)):
            line = text_lines[i]
            text_width, text_height = draw.textsize(line, font=font2)
            if len(text_lines) == 1 and align == 'start':
                text_x = start_x
            else:
                text_x += (study_width_en - text_width) // 2 + (i * text_width * gapMultiplier)
            print(line, text_x, canvas_height, canvas_width)
            draw.text((text_x, name_y), line, fill=color, font=selectedFont, align="center")
        name_y += name_height + line_spacing
        return name_y

    name_y = putTextVertical(text1, name_y)
    name_y = putTextVertical(text2, name_y) + 20
    name_y = putTextVertical(text3, name_y, "en", font2) + 30
    name_y = putTextVertical(text4, name_y, "en", font2) + 210

    name_y = putTextVertical(text5, name_y, "en", font2) + (110 if type == "Regular" else - 20)
    name_y = putTextVertical(text6, name_y, "en", font2) + (200 if type == "Regular" else 330)

    name_y = putTextVertical(text7, name_y, "en", font2, align="start") + 450
    name_y = putTextVertical(text8, name_y, "en", font2, align="start") + 100
    name_y = putTextVertical(text9p1, name_y, "en", font2, align="start", offsetMultiplier=7.34) - 20
    name_y = putTextVertical(text9p2, name_y, "en", font2, align="start", offsetMultiplier=7.34) + 40
    name_y = putTextVertical(text10p1, name_y, "en", font2) - 20
    name_y = putTextVertical(text10p2, name_y, "en", font2)

    diploma.save(f'./storage/images/{university_id}/diploma.jpeg', 'JPEG')


def generateSatpaevDiplomaImageRuKz(graduate, counter, university_id, type="Regular"):
    if graduate["with_honor"]:
        type = "Master"
    font2 = ImageFont.truetype('./kztimesnewroman.ttf', size=35)
    font3 = ImageFont.truetype('./kurale-regular.otf', size=35)

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
        "kz": "шeшімімeн (№                 хаттама)",
        "ru": "           гoда (прoтoкoл №                        )"
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
        "kz": "Прeдсeдатeль Правлeния - Рeктoр ______________________",
        "ru": "Гoрoд"
    }
    text8 = {
        "kz": "М.o",
        "ru": "Рeгистрациoнный"
    }
    text9 = {
        "kz": "жылғы «      »",
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

    if type == "Master":
        text4 = {
            "kz": "ҮЗДІК БАКАЛАВРЫ",
            "ru": "БАКАЛАВРА С ОТЛИЧИЕМ"
        }

    # Create a copy of the diploma template.
    # diploma = templateRegularEn.copy().convert('RGB')
    diploma = templateRegularKzRu.copy().convert('RGB')
    if type == "Master":
        diploma = templateMasterKzRu.copy().convert('RGB')
    # Create a draw object for the diploma.
    draw = ImageDraw.Draw(diploma)

    # Calculate the dimensions of each part
    canvas_width, canvas_height = diploma.size
    part_width = 0

    line_spacing = 5
    gapMultiplier = 12

    name_y = 310

    def putTextVertical(text, name_y, language=None, font=None, selectedColor=None, align="center",
                        offsetMultiplier=0.0, half="Left", fontSize=35):
        # #B1384B
        # #3C5B9E
        start_x = canvas_width // ((12.8 if half == "Left" else 1.73) - offsetMultiplier)
        if align == "center":
            start_x = canvas_width // (6 if half == "Left" else 2)
        textArr = []
        if len(text) > 1 and not isinstance(text, dict):
            for i in text:
                if isinstance(i, dict):
                    textArr.append(i[language])
                else:
                    textArr.append(i)
        else:
            print(text)
            if isinstance(text, dict):
                print(text)
                textArr = [text[language]]
            else:
                textArr = [text]
        color = '#3C5B9E' if type == "Regular" else '#B1384B'
        font2 = ImageFont.truetype('./kztimesnewroman.ttf', size=fontSize)
        selectedFont = font2
        if font:
            selectedFont = font
        if selectedColor:
            color = selectedColor
        text_lines = textArr
        name_width, name_height = draw.textsize('\n'.join(text_lines), font=selectedFont)

        part3_x = start_x + (start_x // 2)
        study_width_en, study_height_en = draw.textsize(' '.join(text_lines), font=font2)
        text_x = part3_x - name_width // 2 - ((len(text_lines) - 1) * study_width_en * 3)
        for i in range(len(text_lines)):
            line = text_lines[i]
            text_width, text_height = draw.textsize(line, font=font2)
            if len(text_lines) == 1 and align == 'start':
                text_x = start_x
            else:
                text_x += (study_width_en - text_width) // 2 + (i * text_width * gapMultiplier)
            # print(line, text_x, canvas_height, canvas_width)
            draw.text((text_x, name_y), line, fill=color, font=selectedFont, align="center")
        name_y += name_height + line_spacing
        return name_y

    temp_name_y = name_y
    name_y = putTextVertical(text1, name_y, language="kz")
    name_y = putTextVertical(text1p2, name_y, language="kz")
    name_y = putTextVertical(text1p3, name_y, language="kz")

    temp_y = name_y
    gradDate = strToDate(graduate['year'])
    putTextVertical({"kz": f"{gradDate.year}"}, temp_y - 7, offsetMultiplier=8.75, language="kz", align="start",
                    selectedColor="black", font=font3)
    putTextVertical({"kz": f"{gradDate.day}"}, temp_y - 7, offsetMultiplier=9.86, language="kz", align="start",
                    selectedColor="black", font=font3)
    putTextVertical({"kz": f"{getMonth('kz', gradDate.month)}"}, temp_y - 7, offsetMultiplier=10.08, language="kz",
                    align="start", selectedColor="black", font=font3)

    name_y = putTextVertical(text2, name_y, language="kz", align="start")
    name_y = putTextVertical(text2p2, name_y, language="kz", align="start") + 250
    temp_y = name_y - 200

    temp_y = putTextVertical({"ru": f"{graduate['name_kz']}"}, temp_y, language="ru", align="center",
                             selectedColor="black", font=font3) + 20
    putTextVertical({"ru": f"{graduate['speciality']}"}, temp_y, language="ru", align="center", selectedColor="black",
                    font=font3) + 20

    name_y = putTextVertical(text3, name_y, language="kz", align="start") + 70
    name_y = putTextVertical(text4, name_y, language="kz", fontSize=43)
    name_y = putTextVertical(text4p2, name_y, language="kz") + 20

    temp_y = name_y
    putTextVertical({"ru": f"{graduate['education_type']['NameKz']}"}, temp_y - 7, language="ru", offsetMultiplier=7,
                    align="start", selectedColor="black", font=font3) + 20

    name_y = putTextVertical(text5, name_y, language="kz", align="start") + 140
    name_y = putTextVertical(text6, name_y, language="kz", align="start")
    name_y = putTextVertical(text7, name_y, language="kz", align="start") + 100
    name_y = putTextVertical(text8, name_y, language="kz", align="start") + 40
    name_y = putTextVertical(text9, name_y, language="kz", align="start", offsetMultiplier=4) + 35

    temp_y = name_y

    putTextVertical({"ru": f"Алматы"}, temp_y - 7, offsetMultiplier=0.55, language="ru",
                    align="start", selectedColor="black", font=font3)

    name_y = putTextVertical(text10, name_y, language="kz", align="start", offsetMultiplier=6)
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

    putTextVertical({"ru": f"{gradDate.day}"}, temp_y - 7, half="Right", offsetMultiplier=0.51, language="ru",
                    align="start", selectedColor="black", font=font3)
    putTextVertical({"ru": f"{getMonth('ru', gradDate.month)}"}, temp_y - 7, half="Right", offsetMultiplier=0.55,
                    language="ru",
                    align="start", selectedColor="black", font=font3)
    temp_y = name_y

    putTextVertical({"ru": f"{gradDate.year}"}, temp_y - 7, half="Right", language="ru",
                    align="start", offsetMultiplier=0, selectedColor="black", font=font3)

    name_y = putTextVertical(text2p2, name_y, half="Right", language="ru", align="start") + 150

    temp_y = name_y - 110
    putTextVertical({"ru": f"{graduate['name_ru']}"}, temp_y, language="ru", align="center",
                    selectedColor="black", half="Right", font=font3) + 20

    name_y = putTextVertical(text3, name_y, half="Right", language="ru")
    name_y = putTextVertical(text4, name_y, half="Right", language="ru", fontSize=43) + 50
    name_y = putTextVertical(text4p2, name_y, half="Right", language="ru") + 120

    temp_y = name_y - 100
    putTextVertical({"ru": f"{graduate['speciality']}"}, temp_y, language="ru", align="center",
                    selectedColor="black", half="Right", font=font3)

    temp_y = name_y
    putTextVertical({"ru": f"{graduate['education_type']['NameRu']}"}, temp_y - 7, language="ru", align="start",
                    offsetMultiplier=0.28,
                    selectedColor="black", half="Right", font=font3)

    name_y = putTextVertical(text5, name_y, half="Right", language="ru", align="start") + 20
    name_y = putTextVertical(text6, name_y, half="Right", language="ru", align="start") + 20
    temp_y = name_y
    putTextVertical({"ru": f"Алматы"}, temp_y - 7, language="ru", align="start",
                    selectedColor="black", half="Right", font=font3, offsetMultiplier=0.15)
    name_y = putTextVertical(text7, name_y, half="Right", language="ru", align="start") + 420
    name_y = putTextVertical(text8, name_y, half="Right", language="ru", align="start", offsetMultiplier=.37)
    name_y = putTextVertical(text9, name_y, half="Right", language="ru", align="start", offsetMultiplier=.37) + 10
    name_y = putTextVertical(text10, name_y, half="Right", language="ru")

    diploma.save(f'./storage/images/{university_id}/{graduate["name_en"]}.jpeg', 'JPEG')


graduate = {
    'city': 'с.Ойшилик',
    'date_of_birth': '2002-02-20+00:00',
    'education_type':
        {
            'NameEn': 'Full time',
            'NameKz': 'Күндізгі оқу түрі',
            'NameRu': 'Очная форма обучения'
        },
    'email': 'kagazova1972@mail.ru',
    'gender': 'мужской',
    'gpa': 2.72,
    'grant': 'Государственный грант',
    'iin': '020220550633',
    'name_en': 'Syezgazyuly Sherkhan',
    'name_kz': 'Cьезғазыұлы Шерхан ',
    'name_ru': 'Cьезғазыұлы Шерхан',
    'nationality': 'Казах',
    'phone': None,
    'region': 'Восточно-Казахстанская',
    'speciality': '6B07302 - Строительная инженерия',
    'study_direction':
        {'NameEn': {'@nil': 'true'},
         'NameKz': {'@nil': 'true'},
         'NameRu': {'@nil': 'true'}},
    'with_honor': False,
    'year': '2023-06-08+00:00'}
# generateSatpaevDiplomaImageEn(graduate, 1, 1, type="Master")
generateSatpaevDiplomaImageRuKz(graduate, 1, 1, type="Master")
