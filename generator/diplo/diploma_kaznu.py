# diploma_kaznu.py
import datetime
import os
import re
import textwrap
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import qrcode
from PIL import Image, ImageDraw, ImageFont

import json


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
    output_dir: str = "Diplomas"
    fields_left: Dict[str, TextField] = field(default_factory=dict)
    fields_right: Dict[str, TextField] = field(default_factory=dict)
    qr_enabled: bool = True
    qr_x_percent: float = 10.0
    qr_y_percent: float = 80.0
    qr_size_percent: float = 12
    qr_base_url: str = "https://app.ediploma.kz"


# ==================== КООРДИНАТЫ ПО КРАСНЫМ КВАДРАТАМ ====================
# Изображение ~970x686 px


class DiplomaGenerator:
    """Генератор дипломов"""

    def __init__(self, config: TemplateConfig):
        self.config = config
        self.template = Image.open(config.template_path).convert('RGBA')
        self.width, self.height = self.template.size
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

    def parse_protocol_date(self, protocol_str: str) -> dict:
        """
        Парсинг строки протокола: "27.09.2025 №1" -> {day, month, year, number}
        """
        result = {"day": "", "month": "", "year": "", "number": ""}

        if not protocol_str:
            return result

        protocol_str = str(protocol_str).strip()

        # Ищем номер протокола
        number_match = protocol_str.split(' №')[-1]
        if number_match:
            result["number"] = number_match

        # Ищем дату в формате DD.MM.YYYY или DD/MM/YYYY
        date_match = re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{4})', protocol_str)
        if date_match:
            result["day"] = date_match.group(1)
            result["month"] = self._month_to_name(date_match.group(2), "ru")
            result["year"] = date_match.group(3)

        return result

    def parse_issue_date(self, issue_str: str) -> dict:
        """
        Парсинг строки протокола: "27.09.2025 №1" -> {day, month, year, number}
        """
        result = {"day": "", "month": "", "year": "", "number": ""}

        if not issue_str:
            return result

        issue_str = str(issue_str).strip()

        # Ищем номер протокола
        number_match = issue_str.split(' №')[-1]
        if number_match:
            result["number"] = number_match

        # Ищем дату в формате DD.MM.YYYY или DD/MM/YYYY
        date_match = re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{4})', issue_str)
        if date_match:
            result["day"] = date_match.group(1)
            result["month"] = self._month_to_name(date_match.group(2), "ru")
            result["year"] = date_match.group(3)

        return result

    def parse_issue_date_en(self, issue_str: str) -> dict:
        """
        Парсинг строки протокола: "27.09.2025 №1" -> {day, month, year, number}
        """
        result = {"day": "", "month": "", "year": "", "number": ""}

        if not issue_str:
            return result

        issue_str = str(issue_str).strip()

        # Ищем номер протокола
        number_match = issue_str.split(' №')[-1]
        if number_match:
            result["number"] = number_match

        # Ищем дату в формате DD.MM.YYYY или DD/MM/YYYY
        date_match = re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{4})', issue_str)
        if date_match:
            result["day"] = date_match.group(1)
            result["month"] = self._month_to_name(date_match.group(2), "ru")
            result["year"] = date_match.group(3)

        return result

    def parse_protocol_date_en(self, protocol_str: str) -> dict:
        """Парсинг для английской версии"""
        result = {"day": "", "month": "", "year": "", "number": ""}

        if not protocol_str:
            return result

        protocol_str = str(protocol_str).strip()

        number_match = protocol_str.split(' №')[-1]
        if number_match:
            result["number"] = number_match

        date_match = re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{4})', protocol_str)
        if date_match:
            result["day"] = date_match.group(1)
            result["month"] = self._month_to_name(date_match.group(2), "en")
            result["year"] = date_match.group(3)

        return result

    def _month_to_name(self, month_num: str, lang: str) -> str:
        """Конвертация номера месяца в название"""
        months_ru = {
            "01": "января", "02": "февраля", "03": "марта",
            "04": "апреля", "05": "мая", "06": "июня",
            "07": "июля", "08": "августа", "09": "сентября",
            "10": "октября", "11": "ноября", "12": "декабря",
            "1": "января", "2": "февраля", "3": "марта",
            "4": "апреля", "5": "мая", "6": "июня",
            "7": "июля", "8": "августа", "9": "сентября",
        }
        months_en = {
            "01": "January", "02": "February", "03": "march",
            "04": "April", "05": "May", "06": "june",
            "07": "July", "08": "August", "09": "september",
            "10": "October", "11": "November", "12": "december",
            "1": "January", "2": "February", "3": "march",
            "4": "April", "5": "May", "6": "june",
            "7": "July", "8": "August", "9": "september",
        }

        months = months_ru if lang == "ru" else months_en
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

    def generate(self, data: dict, counter: int, qr_data: Optional[str] = None) -> dict:
        """Генерация диплома"""
        diploma = self.template.copy()
        draw = ImageDraw.Draw(diploma)
        university_id = 8
        hash_value = uuid.uuid4().hex
        # Парсим даты протоколов
        protocol_ru = self.parse_protocol_date(data.get("protocol_date_number_ru", ""))
        protocol_en = self.parse_protocol_date_en(data.get("protocol_date_number_en", ""))
        issue_date_ru = self.parse_protocol_date(datetime.date.today().strftime("%d.%m.%Y"))
        issue_date_en = self.parse_protocol_date_en(datetime.date.today().strftime("%d.%m.%Y"))
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
            "specialty": self._extract_specialty(data.get("specialty", ""), "ru"),
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
            "specialty": self._extract_specialty(data.get("specialty", ""), "en"),
            "degree_qualification": data.get("degree_qualification_en", ""),
            "form_of_training": "FULL-TIME",
            "issue_day": issue_date_en["day"],  # Заполняется вручную
            "issue_month": issue_date_en["month"],
            "issue_year": issue_date_en["year"],
            "rector_name": rector_name_en,
        }

        # Рисуем левую сторону
        for field_name, field_config in self.config.fields_left.items():
            text = left_data.get(field_name, "")
            self.draw_text(draw, text, field_config)

        # Рисуем правую сторону
        for field_name, field_config in self.config.fields_right.items():
            text = right_data.get(field_name, "")
            self.draw_text(draw, text, field_config)

        # QR код
        if self.config.qr_enabled:
            qr_url = qr_data or f"{self.config.qr_base_url}/{university_id}/{hash_value}"
            self.add_qr_code(diploma, qr_url)

        # Имя файла
        name_en = data.get("full_name_en", f"graduate_{counter}")
        number = data.get("number", counter)
        filename = self.sanitize_filename(f"{name_en.replace(' ', '_')}_{number}")

        # Сохраняем
        output_path = f"{self.config.output_dir}/{filename}.webp"
        diploma.save(output_path, 'WEBP', lossless=False, quality=30)

        # Метаданные
        metadata = {
            "id": counter,
            "filename": f"{filename}.webp",
            "path": output_path,
            "name_ru": data.get("full_name_ru", ""),
            "name_en": data.get("full_name_en", ""),
            "degree_ru": data.get("degree_qualification_ru", ""),
            "degree_en": data.get("degree_qualification_en", ""),
            "specialty": data.get("specialty", ""),
            "university": data.get("university_name", ""),
            "registration_number": data.get("registration_number", ""),
            "iin": data.get("iin", ""),
            "gpa": data.get("gpa", ""),
        }

        json_path = f"json/{counter}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        print(f"✓ Generated: {output_path}")
        return metadata

    def generate_batch(self, data_list: List[dict]) -> List[dict]:
        """Генерация пакета дипломов"""
        all_metadata = []

        for i, data in enumerate(data_list, start=1):
            try:
                metadata = self.generate(data, counter=i)
                all_metadata.append(metadata)
            except Exception as e:
                print(f"✗ Error generating diploma {i}: {e}")

        with open("fullMetadata.json", "w", encoding="utf-8") as f:
            json.dump(all_metadata, f, ensure_ascii=False, indent=2)

        print(f"\n{'=' * 50}")
        print(f"Generated {len(all_metadata)} diplomas")

        return all_metadata

# ==================== ТЕСТ ============
