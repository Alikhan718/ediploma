# run command # nohup python3 -m flask --app diploma_final.py run --debug &

import base64
import io
import re
import textwrap
import warnings
from datetime import datetime

import json
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

# Set the fonts/ #Need to download them and make a way to them
font2 = ImageFont.truetype('./kztimesnewroman.ttf', size=42)
font3 = ImageFont.truetype('./Inconsolata-Medium.ttf', size=50)
font4 = ImageFont.truetype('./Alice-Regular.ttf', size=22)
font5 = ImageFont.truetype('./Alice-Regular.ttf', size=22)  # 2a4a62


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
            return f"Invalid month number. Please provide a number between 1 and {len(months_list)}."
    else:
        return "Invalid language. Supported languages are 'kz' and 'ru'."


def strToDate(strDate) -> datetime:
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
    # number = graduate["number"]
    diploma = templateRegularEn.copy().convert('RGB')
    type = graduate
    if graduate["with_honor"]:
        diploma = templateWithHonorKzRu.copy().convert('RGB')

    type = graduate["degree"] if graduate["degree"] == "Master" else "Regular"

    if type == "Master":
        text4 = {
            "kz": "МАГИСТРІ",
            "ru": "МАГИСТР"
        }
        diploma = templateMasterKzRu.copy().convert('RGB')

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

    diploma.save(f'./storage/images/{university_id}/{graduate["name_en"].replace(" ", "_")}_en.jpeg', 'JPEG')


def generateSatpaevDiplomaImageRuKz(graduate, counter, university_id, type="Regular"):
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
        "kz": "Прeдсeдатeль Правлeния - Рeктoр ____________________",
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
    part_width = 0

    line_spacing = 5
    gapMultiplier = 12

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
                text_x += (study_width_en - text_width + (counter * 90)) // 2
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
    putTextVertical({"kz": f"{gradDate.year}"}, temp_y - 7, offsetMultiplier=8.75, language="kz", align="start",
                    selectedColor="black", font=font3)
    putTextVertical({"kz": f"{gradDate.day}"}, temp_y - 7, offsetMultiplier=9.84 if gradDate.day > 9 else 9.86,
                    language="kz", align="start",
                    selectedColor="black", font=font3)
    temp_y = putTextVertical({"kz": f"{getMonth('kz', gradDate.month)}"}, temp_y - 7, offsetMultiplier=10.08,
                             language="kz",
                             align="start", selectedColor="black", font=font3)
    putTextVertical({"kz": f"{int(graduate['protocol_number'])}"}, temp_y - 7, offsetMultiplier=6.8, language="kz",
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
                    language="ru")

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
    putTextVertical(wrapTextToArr(f"{graduate['education_type']['NameKz']}", ), temp_y - 7, language="kz",
                    offsetMultiplier=7,
                    align="start", selectedColor="black", font=font3)

    name_y = putTextVertical(text5, name_y, language="kz", align="start") + (20 if type == "Master" else 140)

    name_y = putTextVertical(text6, name_y, language="kz", align="start")

    temp_y = name_y
    putTextVertical({"kz": "Бeгeнтаeв М.М."}, temp_y - 7, language="kz", offsetMultiplier=9.35,
                    align="start", selectedColor="black", font=font3)

    name_y = putTextVertical(text7, name_y, language="kz", align="start") + 100

    name_y = putTextVertical(text8, name_y, language="kz", align="start") + 40

    temp_y = name_y
    tempDay = graduate['diploma']['Issue']['Day']
    tempMonth = graduate['diploma']['Issue']['Month']['NameKz']
    tempYear = graduate['diploma']['Issue']['Year']

    putTextVertical({"ru": f"{tempYear}"}, temp_y - 7, font=font3, selectedColor="black", language="ru",
                    align="start")
    putTextVertical({"ru": f"{tempDay}"}, temp_y - 7, font=font3, selectedColor="black", language="ru",
                    align="start", offsetMultiplier=6.98 if tempDay < 10 else 6.9)
    putTextVertical({"ru": f"{tempMonth}"}, temp_y - 7, font=font3, selectedColor="black", language="ru",
                    align="start", offsetMultiplier=7.8)

    name_y = putTextVertical(text9, name_y, language="kz", align="start", offsetMultiplier=4) + 35

    temp_y = name_y

    putTextVertical({"kz": f"Алматы"}, temp_y - 7, language="kz",
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

    putTextVertical({"ru": f"{gradDate.day}"}, temp_y - 7, half="Right",
                    offsetMultiplier=0.5159 if gradDate.day > 9 else 0.52, language="ru",
                    align="start", selectedColor="black", font=font3)
    putTextVertical({"ru": f"{getMonth('ru', gradDate.month)}"}, temp_y - 7, half="Right", offsetMultiplier=0.56,
                    language="ru",
                    align="start", selectedColor="black", font=font3)
    temp_y = name_y

    putTextVertical({"ru": f"{gradDate.year}"}, temp_y - 7, half="Right", language="ru",
                    align="start", offsetMultiplier=0, selectedColor="black", font=font3)

    putTextVertical({"ru": f"{int(graduate['protocol_number'])}"}, temp_y - 7, half="Right", language="ru",
                    align="start", offsetMultiplier=0.345, selectedColor="black", font=font3)

    name_y = putTextVertical(text2p2, name_y, half="Right", language="ru", align="start") + 140

    temp_y = name_y - 100
    putTextVertical({"ru": f"{graduate['name_ru']}"}, temp_y, language="ru", align="center",
                    selectedColor="black", half="Right", font=font3)

    name_y = putTextVertical(text3, name_y, half="Right", language="ru")
    name_y = putTextVertical(text4, name_y, half="Right", language="ru", fontSize=43) + 20
    name_y = putTextVertical({"ru": graduate['diploma']['Issue']['AcademicDegree']['NameRu']}, name_y,
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
        putTextVertical(wrapTextToArr(f"{graduate['study_direction']['NameRu']}", 30), temp_y - 7, language="ru",
                        offsetMultiplier=0.28, align="start",
                        selectedColor="black", half="Right", font=font3)
    name_y += (50 if type == 'Master' else 130)
    temp_y = name_y
    putTextVertical({"ru": f"{graduate['education_type']['NameRu']}"}, temp_y - 7, language="ru", align="start",
                    offsetMultiplier=0.28,
                    selectedColor="black", half="Right", font=font3)

    name_y = putTextVertical(text5, name_y, half="Right", language="ru", align="start") + 20
    temp_y = name_y
    name_y = putTextVertical(text6, name_y, half="Right", language="ru", align="start") + 20
    tempDay = graduate['diploma']['Issue']['Day']
    tempMonth = graduate['diploma']['Issue']['Month']['NameRu']
    tempYear = graduate['diploma']['Issue']['Year']
    putTextVertical({"ru": f"{tempDay}"}, temp_y - 7, half="Right", font=font3, selectedColor="black", language="ru",
                    align="start", offsetMultiplier=0.04 if tempDay < 10 else 0.032)
    putTextVertical({"ru": f"{tempMonth}"}, temp_y - 7, half="Right", font=font3, selectedColor="black", language="ru",
                    align="start", offsetMultiplier=0.15)
    putTextVertical({"ru": f"{tempYear}"}, temp_y - 7, half="Right", font=font3, selectedColor="black", language="ru",
                    align="start", offsetMultiplier=0.28)
    temp_y = name_y
    putTextVertical({"ru": f"Алматы"}, temp_y - 7, language="ru", align="start",
                    selectedColor="black", half="Right", font=font3, offsetMultiplier=0.15)
    name_y = putTextVertical(text7, name_y, half="Right", language="ru", align="start") + 220
    name_y = putTextVertical(text8, name_y, half="Right", language="ru", align="start", offsetMultiplier=.37)
    temp_y = name_y - 30
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

    diploma.save(f'./storage/images/{university_id}/{graduate["name_en"].replace(" ", "_")}_kz_ru.jpeg', 'JPEG')


def parseFromApi():
    url = "https://extapi.satbayev.university/diploma/1.0.1/getAll"
    for i in range(1):
        # for i in range(73):
        # for i in range(73):
        res = requests.post(url=url, headers={"Authorization": "Basic ZGlwbG9tYV9uZnQ6RGQxMjM0NTY="}, json={
            "PageId": i
        })
        if res.status_code == 200:
            body = json.loads(res.content)["result"]["items"]
            for item in body:
                if item["Status"] == "Graduated":
                    jsonItem = {
                        "name_en": item["FIO"]["NameEn"].replace('Ə', 'Ә').replace('ə', 'ә'),
                        "name_kz": item["FIO"]["NameKz"].replace('Ə', 'Ә').replace('ə', 'ә'),
                        "name_ru": item["FIO"]["NameRu"].replace('Ə', 'Ә').replace('ə', 'ә'),
                        "speciality": item["Speciality"],
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
                        "year": item["Protocol"]["Date"],
                        "protocol_number": item["Protocol"]["Number"],

                        "education_type": item["EducationType"],
                        "study_direction": item["DirectionStudy"],

                        "degree": "Master" if item["DegreeType"] == 2 else "Bachelor",
                        "qr_base64": item["QRBase64"],
                        "diploma": item['Diploma'],
                    }

                    generateSatpaevDiplomaImageEn(jsonItem, 3, 1)
                    # generateSatpaevDiplomaImageRuKz(jsonItem, 3, 1)


parseFromApi()
