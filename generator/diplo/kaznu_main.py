from diploma_kaznu import DiplomaGenerator, TemplateConfig, TextField

KAZNU_BACHELOR_RU_EN = TemplateConfig(
    name="kaznu_bachelor_ru_en",
    template_path="kaznu_backelor_ru_en.webp",
    output_dir="Diplomas",

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
            font_size=70, max_width=30, align="center"
        ),
        "specialty": TextField(
            x_percent=29.0, y_percent=54.5,
            font_size=49, max_width=120, align="center"
        ),
        "degree_qualification": TextField(
            x_percent=27.5, y_percent=63.5,
            font_size=49, max_width=120, align="center"
        ),
        "form_of_training": TextField(
            x_percent=28.0 + 7, y_percent=68.0,
            font_size=41, max_width=20
        ),
        "registration_number": TextField(
            x_percent=10.0, y_percent=79.0,
            font_size=41, max_width=10
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
            font_size=70, max_width=30, align="center"
        ),
        "specialty": TextField(
            x_percent=73.5, y_percent=54.5,
            font_size=49, max_width=120, align="center"
        ),
        "degree_qualification": TextField(
            x_percent=73.5, y_percent=63.5,
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

    qr_enabled=True,
)
# Данные выпускника
data = {
    "full_name_ru": "Куанова Гаухар Еркинбаевна",
    "full_name_en": "Kuanova Gaukhar",
    "protocol_date_number_ru": "27.09.2025 №1",
    "protocol_date_number_en": "27.09.2025 №1",
    "degree_qualification_ru": "Доктор делового администрирования (DBA)",
    "degree_qualification_en": "Doctor of Business Administration (DBA)",
    "specialty": "8D04112-Денсаулық сақтаудағы іскерлік әкімшілендіру / 8D04112-Деловое администрирование в здравоохранении / 8D04112-Business administration in healthcare",
}

# Генерация
generator = DiplomaGenerator(KAZNU_BACHELOR_RU_EN)
generator.generate(data, counter=1)
