# diploma_kaznu.py
import datetime
import os
import random
import re
import string
import textwrap
import traceback
import zipfile
from dataclasses import dataclass, field
from pprint import pprint
from typing import Dict, List, Tuple

import bcrypt
import numpy as np
import pandas as pd
import psycopg2
import qrcode
from PIL import Image, ImageDraw, ImageFont

import json


def parse_complex_excel(file_path):
    """
    Парсит сложный Excel файл с объединенными ячейками и пропусками колонок
    """
    # Читаем Excel файл без заголовков, чтобы контролировать mapping вручную
    df = pd.read_excel(file_path, header=None)

    # Определяем mapping колонок по буквам Excel (A, B, C, ...)
    # Создаем словарь соответствия: номер_колонки -> название_поля
    column_mapping = {
        0: 'number',  # A - №
        1: 'university_name',  # B - Наименование ВУЗа
        2: 'registration_number',  # C - Регистрационный номер
        3: 'full_name_kz',  # D - ФИО выпускника каз
        4: 'full_name_ru',  # E - ФИО выпускника рус
        5: 'full_name_en',  # F - ФИО выпускника англ
        6: 'protocol_date_number_kz',  # G - Дата и номер протокола каз
        7: 'protocol_date_number_ru',  # H - Дата и номер протокола рус
        8: 'protocol_date_number_en',  # I - Дата и номер протокола англ
        9: 'degree_qualification_kz',  # K - Степень и квалификация каз
        10: 'speciality_kz',  # K - Степень и квалификация каз
        11: 'degree_qualification_ru',  # M - Степень и квалификация рус
        12: 'speciality_ru',  # M - Степень и квалификация рус
        13: 'degree_qualification_en',  # O - Степень и квалификация англ
        14: 'speciality_en',  # O - Степень и квалификация англ
        15: 'with_honors_kz',  # Q - с отличием каз
        16: 'with_honors_ru',  # R - с отличием рус
        17: 'with_honors_en',  # S - с отличием англ
        18: 'specialty',  # T - Специальность
        19: 'gpa',  # U - GPA
        20: 'iin',  # V - ИИН
        21: 'diploma_region',  # W - Регион
        22: 'email',  # X - email
        23: 'diploma_phone',  # Y - моб.тел
        24: 'residence'  # Z - Место проживания
    }

    # Находим строку с заголовками (обычно первая строка с данными)
    header_row = find_header_row(df)
    print(f"Заголовки найдены в строке: {header_row}")

    # Создаем новый DataFrame с правильными колонками
    parsed_data = []

    # Проходим по строкам данных (после заголовка)
    for idx in range(header_row + 2, len(df)):
        row = df.iloc[idx]
        parsed_row = {}

        for col_idx, field_name in column_mapping.items():
            if col_idx < len(row):
                parsed_row[field_name] = row[col_idx]
            else:
                parsed_row[field_name] = None

        # Проверяем, что строка не пустая
        if not is_empty_row(parsed_row):
            parsed_data.append(parsed_row)

    result_df = pd.DataFrame(parsed_data)

    # Очищаем данные
    result_df = clean_data(result_df)
    # return df as dict list
    return result_df


def find_header_row(df):
    """
    Находит строку с заголовками в DataFrame
    """
    for idx in range(min(10, len(df))):  # Проверяем первые 10 строк
        row = df.iloc[idx]
        # Ищем строку, содержащую ключевые слова заголовков
        row_text = ' '.join([str(cell) for cell in row if pd.notna(cell)])
        if any(keyword in row_text for keyword in ['Наименование ВУЗа', 'ФИО выпускника', 'Регистрационный номер']):
            return idx
    return 0  # Если не нашли, используем первую строку


def is_empty_row(row_dict):
    """
    Проверяет, является ли строка пустой
    """
    if type(row_dict['full_name_kz']) is float or str(row_dict['full_name_kz']) == 'nan':
        return True
    values = [v for v in row_dict.values() if v is not None and str(v).strip() != '']
    return len(values) == 0


def clean_data(df):
    """
    Очищает и преобразует данные
    """
    # Заменяем NaN и None на пустые строки
    df = df.replace([np.nan, None], '')

    # Преобразуем числовые колонки
    if 'gpa' in df.columns:
        df['gpa'] = pd.to_numeric(df['gpa'], errors='coerce')

    if 'number' in df.columns:
        df['number'] = pd.to_numeric(df['number'], errors='coerce')

    # Очищаем строковые колонки
    string_columns = ['university_name', 'registration_number', 'full_name_kz',
                      'full_name_ru', 'full_name_en', 'specialty', 'region',
                      'email', 'mobile_phone', 'residence']

    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    return df


def inspect_excel_structure(file_path, num_rows=5):
    """
    Функция для инспекции структуры Excel файла
    """
    print("=== ИНСПЕКЦИЯ СТРУКТУРЫ EXCEL ===")

    # Читаем без заголовков
    df_raw = pd.read_excel(file_path, header=None)

    print(f"Всего строк: {len(df_raw)}, колонок: {len(df_raw.columns)}")
    print("\nПервые 5 строк сырых данных:")

    for i in range(min(num_rows, len(df_raw))):
        print(f"\n--- Строка {i} ---")
        for j in range(min(15, len(df_raw.columns))):  # Показываем первые 15 колонок
            cell_value = df_raw.iloc[i, j]
            if pd.notna(cell_value) and str(cell_value).strip() != '':
                print(f"  Колонка {j} ({chr(65 + j)}): {cell_value}")


@dataclass
class TextField:
    """Конфигурация текстового поля"""
    x_percent: float
    y_percent: float
    font_size: int = 22
    font_path: str = "timesnewromanpsmt.ttf"
    color: str = "black"
    max_width: int = 120
    align: str = "center"
    uppercase: bool = False


@dataclass
class TemplateConfig:
    """Конфигурация шаблона диплома"""
    name: str
    template_path: str
    template_path_kaz: str
    output_dir: str = "Diplomas"
    fields_left: Dict[str, TextField] = field(default_factory=dict)
    fields_right: Dict[str, TextField] = field(default_factory=dict)
    fields_kaz: Dict[str, TextField] = field(default_factory=dict)
    qr_enabled: bool = True
    qr_x_percent: float = 10.0
    qr_y_percent: float = 80.0
    qr_size_percent: float = 12
    qr_base_url: str = "https://app.ediploma.kz",
    hash: str = "",
    university_id: int = 0,


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


connection, cursor = connectDatabase()


class DiplomaGenerator:
    """Генератор дипломов"""

    def __init__(self, config: TemplateConfig):
        self.config = config
        self.template = Image.open(config.template_path).convert('RGBA')
        self.template_kaz = Image.open(config.template_path_kaz).convert('RGBA')
        self.width, self.height = self.template.size
        self.width_kaz, self.height_kaz = self.template_kaz.size
        self.fonts_cache: Dict[str, ImageFont.FreeTypeFont] = {}

        os.makedirs(config.output_dir, exist_ok=True)
        os.makedirs("json", exist_ok=True)

    def get_font(self, font_path: str, size: int) -> ImageFont.FreeTypeFont:
        """Получение шрифта с кэшированием"""
        key = f"{font_path}_{size}"
        if key not in self.fonts_cache:
            try:
                self.fonts_cache[key] = ImageFont.truetype(font_path, size=size)
            except OSError:
                print(f"Warning: Font {font_path} not found, using default")
                self.fonts_cache[key] = ImageFont.load_default()
        return self.fonts_cache[key]

    def percent_to_pixels(self, x_percent: float, y_percent: float) -> Tuple[int, int]:
        """Конвертация процентов в пиксели"""
        x = int(self.width * x_percent / 100)
        y = int(self.height * y_percent / 100)
        return x, y

    def draw_text(self, draw: ImageDraw.ImageDraw, text: str, field: TextField):
        """Отрисовка текста"""
        if not text or text.strip() == "" or str(text).upper() == "NONE" or str(text) == "nan":
            return

        text = str(text).strip()
        if field.uppercase:
            text = text.upper()

        font = self.get_font(field.font_path, field.font_size)

        # Wrap текст
        lines = []
        for part in text.split("\n"):
            lines.extend(textwrap.wrap(part, width=field.max_width))

        if not lines:
            return

        center_x, center_y = self.percent_to_pixels(field.x_percent, field.y_percent)

        # Вычисляем размеры
        line_heights = []
        line_widths = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_widths.append(bbox[2] - bbox[0])
            line_heights.append(bbox[3] - bbox[1])

        total_height = sum(line_heights) + (len(lines) - 1) * 3
        max_line_width = max(line_widths) if line_widths else 0

        current_y = center_y - total_height // 2

        for i, line in enumerate(lines):
            line_width = line_widths[i]
            line_height = line_heights[i]

            if field.align == "center":
                line_x = center_x - line_width // 2
            elif field.align == "left":
                line_x = center_x
            else:  # right
                line_x = center_x - line_width

            draw.text((line_x, current_y), line, fill=field.color, font=font)
            current_y += line_height + 3

    def add_qr_code(self, diploma: Image.Image, data: str):
        """Добавление QR кода"""
        if not self.config.qr_enabled:
            return

        qr_size = int(self.width * self.config.qr_size_percent / 100)

        qr = qrcode.QRCode(box_size=1)
        qr.add_data(data)
        qr.make(fit=True)

        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_image = qr_image.resize((qr_size, qr_size), Image.LANCZOS)

        qr_x, qr_y = self.percent_to_pixels(self.config.qr_x_percent, self.config.qr_y_percent)
        qr_x -= qr_size // 2
        qr_y -= qr_size // 2

        diploma.paste(qr_image, (qr_x, qr_y))

    def sanitize_filename(self, filename: str) -> str:
        """Очистка имени файла"""
        return re.sub(r'[\\/*?:"<>|\n\t]', '', filename)

    def parse_protocol_date(self, protocol_str: str, lang: str = 'ru') -> dict:
        """
        Парсинг строки протокола: "27.09.2025 №1" -> {day, month, year, number}
        """
        result = {"day": "", "month": "", "year": "", "number": ""}

        if not protocol_str:
            return result

        protocol_str = str(protocol_str).strip()

        # Ищем номер протокола
        # number_match = protocol_str.split(' №')[-1]
        # if number_match:
        #     result["number"] = number_match

        # Ищем дату в формате DD.MM.YYYY или DD/MM/YYYY
        date_match = re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{4})', protocol_str)
        date_match_2 = protocol_str.split(' ')
        if date_match:
            result["day"] = date_match.group(1)
            result["month"] = self._month_to_name(date_match.group(2), lang)
            result["year"] = date_match.group(3)
        if len(date_match_2) == 3:
            result["day"] = date_match_2[0]
            result["month"] = date_match_2[1].capitalize()
            result["year"] = date_match_2[2]

        return result

    def _month_to_name(self, month_num: str, lang: str) -> str:
        """Конвертация номера месяца в название"""
        months_ru = {
            "01": "Января", "02": "Февраля", "03": "Марта",
            "04": "Апреля", "05": "Мая", "06": "Июня",
            "07": "Июля", "08": "Августа", "09": "Сентября",
            "10": "Октября", "11": "Ноября", "12": "Декабря",
            "1": "Января", "2": "Февраля", "3": "Марта",
            "4": "Апреля", "5": "Мая", "6": "Июня",
            "7": "Июля", "8": "Августа", "9": "Сентября",
        }

        months_en = {
            "01": "January", "02": "February", "03": "March",
            "04": "April", "05": "May", "06": "June",
            "07": "July", "08": "August", "09": "September",
            "10": "October", "11": "November", "12": "December",
            "1": "January", "2": "February", "3": "March",
            "4": "April", "5": "May", "6": "June",
            "7": "July", "8": "August", "9": "September",
        }

        months_kz = {
            "01": "Қаңтар", "02": "Ақпан", "03": "Наурыз",
            "04": "Сәуір", "05": "Мамыр", "06": "Маусым",
            "07": "Шілде", "08": "Тамыз", "09": "Қыркүйек",
            "10": "Қазан", "11": "Қараша", "12": "Желтоқсан",
            "1": "Қаңтар", "2": "Ақпан", "3": "Наурыз",
            "4": "Сәуір", "5": "Мамыр", "6": "Маусым",
            "7": "Шілде", "8": "Тамыз", "9": "Қыркүйек",
        }

        if lang == "ru":
            months = months_ru
        elif lang == "en":
            months = months_en
        else:
            months = months_kz
        return months.get(month_num, month_num)

    def _extract_specialty(self, specialty: str, lang: str) -> str:
        """Извлечение специальности на нужном языке"""
        if not specialty:
            return ""

        parts = str(specialty).split("/")

        if lang == "kz" and len(parts) >= 1:
            return parts[0].strip()
        elif lang == "ru" and len(parts) >= 2:
            return parts[1].strip()
        elif lang == "en" and len(parts) >= 3:
            return parts[2].strip()

        return specialty

    def generate(self, data: dict, counter: int) -> dict:
        """Генерация диплома"""
        diploma = self.template.copy()
        draw = ImageDraw.Draw(diploma)
        diploma_kaz = self.template_kaz.copy()
        draw_kaz = ImageDraw.Draw(diploma_kaz)
        university_id = 8
        # Парсим даты протоколов
        protocol_ru = self.parse_protocol_date(data.get("protocol_date_number_ru", ""), 'ru')
        protocol_en = self.parse_protocol_date(data.get("protocol_date_number_en", ""), 'en')
        protocol_kz = self.parse_protocol_date(data.get("protocol_date_number_kz", ""), 'kz')
        issue_date_ru = self.parse_protocol_date(datetime.date.today().strftime("%d.%m.%Y"), 'ru')
        issue_date_en = self.parse_protocol_date(datetime.date.today().strftime("%d.%m.%Y"), 'en')
        issue_date_kz = self.parse_protocol_date(datetime.date.today().strftime("%d.%m.%Y"), 'kz')
        rector_name_kz = "Ж.К. Түймебаев"
        rector_name_ru = "Ж.К. Туймебаев"
        rector_name_en = "Zh.Tuimebayev"
        # ===== ЛЕВАЯ СТОРОНА (РУССКИЙ) =====
        left_data = {
            "protocol_day": protocol_ru["day"],
            "protocol_month": protocol_ru["month"],
            "protocol_year": protocol_ru["year"],
            "protocol_number": protocol_ru["number"],
            "full_name": data.get("full_name_ru", "").upper(),
            "specialty": data.get("speciality_ru", ""),
            "degree_qualification": data.get("degree_qualification_ru", ""),
            "form_of_training": "ОЧНАЯ",  # или из данных
            "registration_number": data.get("registration_number", ""),
            "issue_day": issue_date_ru["day"],  # Заполняется вручную
            "issue_month": issue_date_ru["month"],
            "issue_year": issue_date_ru["year"],
            "rector_name": rector_name_ru,
        }

        # ===== ПРАВАЯ СТОРОНА (АНГЛИЙСКИЙ) =====
        right_data = {
            "protocol_day": protocol_en["day"],
            "protocol_month": protocol_en["month"],
            "protocol_year": protocol_en["year"],
            "protocol_number": protocol_en["number"],
            "full_name": data.get("full_name_en", "").upper(),
            "specialty": data.get("speciality_en", ""),
            "degree_qualification": data.get("degree_qualification_en", ""),
            "form_of_training": "FULL-TIME",
            "issue_day": issue_date_en["day"],  # Заполняется вручную
            "issue_month": issue_date_en["month"],
            "issue_year": issue_date_en["year"],
            "rector_name": rector_name_en,
        }

        # ===== (Казахский) отдельное фото =====
        kaz_data = {
            "protocol_day": protocol_kz["day"],
            "protocol_month": protocol_kz["month"],
            "protocol_year": protocol_kz["year"],
            "protocol_number": protocol_kz["number"],
            "full_name": data.get("full_name_kz", "").upper(),
            "specialty": data.get("speciality_kz", ""),
            "degree_qualification": data.get("degree_qualification_kz", ""),
            "form_of_training": "ТОЛЫҚ",
            "issue_day": issue_date_kz["day"],  # Заполняется вручную
            "issue_month": issue_date_kz["month"],
            "issue_year": issue_date_kz["year"],
            "rector_name": rector_name_kz,
            "registration_number": data.get("registration_number", ""),
        }

        # Рисуем левую сторону
        for field_name, field_config in self.config.fields_left.items():
            text = left_data.get(field_name, "")
            self.draw_text(draw, text, field_config)

        # Рисуем правую сторону
        for field_name, field_config in self.config.fields_right.items():
            text = right_data.get(field_name, "")
            self.draw_text(draw, text, field_config)

        # Рисуем правую сторону
        for field_name, field_config in self.config.fields_kaz.items():
            text = kaz_data.get(field_name, "")
            self.draw_text(draw_kaz, text, field_config)

        # QR код
        if self.config.qr_enabled:
            text = f"{data['iin']}"
            generatedHash = generateHash(text)
            qr_url = f'https://app.ediploma.kz/{university_id}/{generatedHash}'
            # qr_url = qr_data or f"{self.config.qr_base_url}/{university_id}/{hash_value}"
            self.add_qr_code(diploma, qr_url)
            self.add_qr_code(diploma_kaz, qr_url)

        # Имя файла RUS EN
        name_en = data.get("full_name_en", f"graduate_{counter}")
        number = data.get("number", counter)
        filename = self.sanitize_filename(f"{name_en.replace(' ', '_')}_{str(data['iin'])[-2:]}_ru_en")

        # Сохраняем
        output_path = f"{self.config.output_dir}/{filename}.webp"
        diploma.save(output_path, 'WEBP', lossless=False, quality=30)

        # Имя файла KAZ
        filename = self.sanitize_filename(f"{name_en.replace(' ', '_')}_{str(data['iin'])[-2:]}_kz")

        # Сохраняем
        output_path = f"{self.config.output_dir}/{filename}.webp"
        diploma_kaz.save(output_path, 'WEBP', lossless=False, quality=30)

        # Метаданные
        metadata = {
            "id": counter,
            "filename": f"{filename}.webp",
            "path": output_path,
            "name_ru": data.get("full_name_ru", ""),
            "name_en": data.get("full_name_en", ""),
            "name_kz": data.get("full_name_kz", ""),
            "email": data.get("email", ""),
            "degree_ru": data.get("degree_qualification_ru", ""),
            "degree_en": data.get("degree_qualification_en", ""),
            "degree_kz": data.get("degree_qualification_kz", ""),
            "speciality_en": data.get("specialty_en", ""),
            "speciality_kz": data.get("specialty_kz", ""),
            "speciality_ru": data.get("specialty_ru", ""),
            "speciality": {
                "NameEn": data.get("specialty_en", ""),
                "NameKz": data.get("specialty_kz", ""),
                "NameRu": data.get("specialty_ru", ""),
            },
            "year_number": protocol_kz["year"],
            "Number": data.get("registration_number", ""),
            "iin": data.get("iin", ""),
            "gpa": data.get("gpa", ""),
            "phone": data.get("diploma_phone", ""),
            "region": data.get("diploma_region", ""),
        }

        json_path = f"json/{counter}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"✓ Generated: {output_path}")
        return metadata

    def generate_batch(self, data_list: List[dict]) -> List[dict]:
        """Генерация пакета дипломов"""
        all_metadata = []
        cursor.execute(
            f"UPDATE diploma_generations SET progress = 0, max_progress = {len(data_list)} where hash = '{self.config.hash}' and finished_at is null")
        connection.commit()
        for i, data in enumerate(data_list, start=1):
            try:
                metadata = self.generate(data, counter=i)
                diplomaSave(self.config.university_id, self.config.hash, metadata, i)
                all_metadata.append(metadata)
            except Exception as e:
                print(traceback.format_exc())
                print(f"✗ Error generating diploma {i}: {e}")
        createFolderIfNotExists(f"./storage/jsons/{self.config.hash}/")
        createFolderIfNotExists(f"./storage/archives/")
        zip_folder(folder_path=f"./storage/images/{self.config.hash}",
                   zip_path=f"./storage/archives/{self.config.hash}.zip")

        with open(
                f"./storage/jsons/{self.config.hash}/fullMetadata.json",
                "w",
                encoding="utf-8"
        ) as f:
            json.dump(all_metadata, f, ensure_ascii=False, indent=2)
        # cursor.execute(f"UPDATE diploma_generations SET finished_at = now() where hash = '{self.config.hash}'")
        # connection.commit()
        print(f"\n{'=' * 50}")
        print(f"Generated {len(all_metadata)} diplomas")

        return all_metadata


def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname=arcname)


def diplomaSave(university_id, metadata_hash, item, counter):
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
    flag = False

    image = (f"https://generator.ediploma.kz/get-file/images/{metadata_hash}/"
             + "_".join(item['name_en'].split(" "))
             + f"_{str(item['iin'])[-2:]}_ru_en.webp, https://generator.ediploma.kz/get-file/images/{metadata_hash}/"
             + "_".join(item['name_en'].split(" "))
             + f"_{str(item['iin'])[-2:]}_kz.webp")
    data = {}
    contentFields = {}
    attributes = item

    if item["Number"]:
        contentFields['Number'] = item["Number"]

    data['year'] = item['year_number']
    for key, value in attributes.items():
        if key == 'number':
            continue

        if key in ignoreAttr:
            data[key] = value
        else:
            contentFields[key] = value

    # Construct and execute the SQL query to insert data into
    # the database

    # create user start
    nameArr = item["name_kz"].split(" ")
    last_name = nameArr[0]
    first_name = nameArr[1]
    middle_name = nameArr[2] if len(nameArr) > 2 else ""
    password = generate_random_string(8)
    # password = "12345"
    hashed_password = hash_password(password).decode('utf-8')
    email = item['email'] if (
            'email' in item and item['email'] and len(item['email'])) else f"{'_'.join(nameArr)}@jasaim.kz"
    file_path = f'./storage/jsons/{university_id}/users.json'
    new_value = {
        "name": item["name_kz"].strip(),
        "email": email,
        "password": password,
    }
    if os.path.exists(file_path):
        # Open file and read contents
        with open(file_path, 'r', encoding='utf-8') as file:
            # Check if file is empty
            jsonData = json.load(file)

            # Check if email exists in the array
            for index, user in enumerate(jsonData):
                if user["email"] == new_value["email"]:
                    email = f"{'_'.join(nameArr)}_{counter}@jasaim.kz"
                    new_value['email'] = email
                    break

            # Add new value to array
            jsonData.append(new_value)

        # Write updated jsonData back to file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(jsonData, file, ensure_ascii=False, indent=4)
    else:
        createFolderIfNotExists(f'./storage/jsons/{university_id}')
        # Create file and set empty array with new value
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump([new_value], file, ensure_ascii=False, indent=4)
    query = (
        "INSERT INTO users (name, first_name, last_name, middle_name, email, password, university_id, role_id, email_validated) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
        "RETURNING id"
    )
    cursor.execute(query,
                   (item["name_kz"], first_name, last_name, middle_name, email, hashed_password, university_id, 3,
                    True))
    user_id = cursor.fetchone()[0]
    # create user end
    # print(email, password)

    query = (
        "INSERT INTO diplomas("
        "name_en, name_ru, name_kz, university_id, year, "
        "speciality_en, speciality_ru, speciality_kz, image, gpa, iin, visibility, user_id"
        ") "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        "RETURNING id"
    )
    pprint(item)
    values = (
        item["name_en"], item["name_ru"], item["name_kz"],
        university_id, item["year_number"],
        item["speciality_en"], item["speciality_ru"],
        item["speciality_kz"],
        image,
        item["gpa"],
        item["iin"],
        False,
        user_id
    )
    cursor.execute(query, values)
    diploma_id = cursor.fetchone()[0]
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
    print(f"Counter: {counter}")
    cursor.execute(f"UPDATE diploma_generations SET progress = {counter} where hash = '{metadata_hash}'")
    connection.commit()


def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


def hash_password(password):
    # Generate salt
    salt = bcrypt.gensalt(10)
    # Hash password with the generated salt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


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


# Парсим данные
print("\n=== ПАРСИНГ ДАННЫХ ===")
cursor.execute(
    "SELECT university_id, hash FROM diploma_generations WHERE university_id = %s and finished_at is null",
    (8,))
existing_record = cursor.fetchone()
generation_hash, university_id = None, None
if existing_record:
    # If the record exists, return link to future archive
    university_id = existing_record[0]
    generation_hash = existing_record[1]
else:
    exit(0)

KAZNU_BACHELOR = TemplateConfig(
    name="kaznu_bachelor_ru_en",
    template_path="kaznu_bachelor_ru_en.webp",
    template_path_kaz="kaznu_bachelor_kz.webp",
    output_dir="./storage/images/" + generation_hash,
    # ===== ЛЕВАЯ СТОРОНА (РУССКИЙ) =====
    fields_left={
        "protocol_day": TextField(
            x_percent=18.5, y_percent=39.8,
            font_size=49, max_width=5
        ),
        "protocol_month": TextField(
            x_percent=23.0, y_percent=40.1,
            font_size=46, max_width=15
        ),
        "protocol_year": TextField(
            x_percent=28.2, y_percent=39.8,
            font_size=49, max_width=10
        ),
        "protocol_number": TextField(
            x_percent=42.0, y_percent=39.8,
            font_size=49, max_width=5
        ),
        "full_name": TextField(
            x_percent=29.0, y_percent=46.0,
            font_size=70, max_width=50, align="center"
        ),
        "degree_qualification": TextField(
            x_percent=29.0, y_percent=54.5,
            font_size=49, max_width=120, align="center"
        ),
        "specialty": TextField(
            x_percent=27.5, y_percent=63,
            font_size=49, max_width=120, align="center"
        ),
        "form_of_training": TextField(
            x_percent=28.0 + 7, y_percent=68.0,
            font_size=41, max_width=20
        ),
        "registration_number": TextField(
            x_percent=5.5, y_percent=92.2,
            font_size=41, max_width=100
        ),
        "issue_day": TextField(
            x_percent=20.5 + 2.8, y_percent=89.8,
            font_size=49, max_width=5
        ),
        "issue_month": TextField(
            x_percent=26.0 + 1.5, y_percent=90,
            font_size=46, max_width=15
        ),
        "issue_year": TextField(
            x_percent=32.5, y_percent=89.8,
            font_size=49, max_width=10
        ),

        "rector_name": TextField(
            x_percent=37, y_percent=79,
            font_size=45, max_width=50
        ),
    },
    # ===== ПРАВАЯ СТОРОНА (АНГЛИЙСКИЙ) =====
    fields_right={
        "protocol_day": TextField(
            x_percent=68.7, y_percent=39.8,
            font_size=49, max_width=5
        ),
        "protocol_month": TextField(
            x_percent=73.3, y_percent=40.1,
            font_size=46, max_width=15
        ),
        "protocol_year": TextField(
            x_percent=79.5, y_percent=39.8,
            font_size=49, max_width=5
        ),
        "protocol_number": TextField(
            x_percent=89.5, y_percent=39.8,
            font_size=49, max_width=5
        ),
        "full_name": TextField(
            x_percent=75.0, y_percent=46.0,
            font_size=70, max_width=50, align="center"
        ),
        "degree_qualification": TextField(
            x_percent=73.5, y_percent=54.5,
            font_size=49, max_width=120, align="center"
        ),
        "specialty": TextField(
            x_percent=73.5, y_percent=63,
            font_size=49, max_width=120, align="center"
        ),
        "form_of_training": TextField(
            x_percent=78.0 + 4, y_percent=68.0,
            font_size=41, max_width=20
        ),
        "issue_day": TextField(
            x_percent=68.5 + 2.8, y_percent=89.8,
            font_size=49, max_width=5
        ),
        "issue_month": TextField(
            x_percent=73.0 + 2.5, y_percent=89.8,
            font_size=46, max_width=15
        ),
        "issue_year": TextField(
            x_percent=80.2, y_percent=89.8,
            font_size=49, max_width=10
        ),
        "rector_name": TextField(
            x_percent=63.1, y_percent=79,
            font_size=45, max_width=50
        ),
    },
    # ===== ПРАВАЯ СТОРОНА (АНГЛИЙСКИЙ) =====
    fields_kaz={
        "protocol_day": TextField(
            x_percent=50.2, y_percent=35.1,
            font_size=55, max_width=5
        ),
        "protocol_month": TextField(
            x_percent=57.2, y_percent=35.2,
            font_size=55, max_width=15
        ),
        "protocol_year": TextField(
            x_percent=40.8, y_percent=35.1,
            font_size=55, max_width=5
        ),
        "protocol_number": TextField(
            x_percent=73.8, y_percent=35.1,
            font_size=55, max_width=5
        ),
        "full_name": TextField(
            x_percent=50.0, y_percent=41.5,
            font_size=70, max_width=50, align="center"
        ),
        "degree_qualification": TextField(
            x_percent=50, y_percent=46.8,
            font_size=55, max_width=120, align="center"
        ),
        "specialty": TextField(
            x_percent=50, y_percent=56.2,
            font_size=55, max_width=120, align="center"
        ),
        "form_of_training": TextField(
            x_percent=53, y_percent=67.3,
            font_size=58, max_width=20
        ),
        "issue_day": TextField(
            x_percent=51, y_percent=89.7,
            font_size=55, max_width=5
        ),
        "issue_month": TextField(
            x_percent=57.3, y_percent=89.6,
            font_size=55, max_width=15
        ),
        "issue_year": TextField(
            x_percent=42, y_percent=89.7,
            font_size=55, max_width=10
        ),
        "rector_name": TextField(
            x_percent=73.5, y_percent=75,
            font_size=50, max_width=50
        ),
        "registration_number": TextField(
            x_percent=5.5, y_percent=92.2,
            font_size=41, max_width=100
        ),
    },
    qr_enabled=True,
    hash=generation_hash,
    university_id=university_id,
)

file_path = f"./storage/files/{generation_hash}/data.xlsx"
# Сначала инспектируем структуру
inspect_excel_structure(file_path)

graduates_df = parse_complex_excel(file_path)
generator = DiplomaGenerator(KAZNU_BACHELOR)
graduates_arr = graduates_df.to_dict(orient='records')
generator.generate_batch(graduates_arr)
