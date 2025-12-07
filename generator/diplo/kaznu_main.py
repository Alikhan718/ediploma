from diplo.test import inspect_excel_structure, parse_complex_excel
from diploma_kaznu import DiplomaGenerator, TemplateConfig, TextField

# Данные выпускника
# data = {
#     "full_name_ru": "Куанова Гаухар Еркинбаевна",
#     "full_name_en": "Kuanova Gaukhar",
#     "full_name_kz": "Kuanova Gaukhar Kaz",
#     "protocol_date_number_ru": "27.09.2025 №1",
#     "protocol_date_number_en": "27.09.2025 №1",
#     "protocol_date_number_kz": "27.09.2025 №1",
#     "degree_qualification_ru": "Доктор делового администрирования (DBA)",
#     "degree_qualification_en": "Doctor of Business Administration (DBA)",
#     "degree_qualification_kz": "Doctor of Business Administration (DBA)",
#     "specialty": "8D04112-Денсаулық сақтаудағы іскерлік әкімшілендіру / 8D04112-Деловое администрирование в здравоохранении / 8D04112-Business administration in healthcare",
# }

# Генерация
# generator.generate(data, counter=1)

file_path = "sample_data_kaznu.xlsx"  # Укажите путь к вашему файлу

# Сначала инспектируем структуру
inspect_excel_structure(file_path)

# Парсим данные
print("\n=== ПАРСИНГ ДАННЫХ ===")
graduates_df = parse_complex_excel(file_path)
generator = DiplomaGenerator(KAZNU_BACHELOR)
graduates_arr = graduates_df.to_dict(orient='records')
generator.generate_batch(graduates_arr)
