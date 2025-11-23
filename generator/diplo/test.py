import pandas as pd
import numpy as np

def parse_complex_excel(file_path):
    """
    Парсит сложный Excel файл с объединенными ячейками и пропусками колонок
    """
    # Читаем Excel файл без заголовков, чтобы контролировать mapping вручную
    df = pd.read_excel(file_path, header=None)

    # Определяем mapping колонок по буквам Excel (A, B, C, ...)
    # Создаем словарь соответствия: номер_колонки -> название_поля
    column_mapping = {
        0: 'number',                           # A - №
        1: 'university_name',                  # B - Наименование ВУЗа
        2: 'registration_number',              # C - Регистрационный номер
        3: 'full_name_kz',                     # D - ФИО выпускника каз
        4: 'full_name_ru',                     # E - ФИО выпускника рус
        5: 'full_name_en',                     # F - ФИО выпускника англ
        6: 'protocol_date_number_kz',          # G - Дата и номер протокола каз
        7: 'protocol_date_number_ru',          # H - Дата и номер протокола рус
        8: 'protocol_date_number_en',          # I - Дата и номер протокола англ
        # 9: ПРОПУСК (J) - пустая колонка
        10: 'degree_qualification_kz',         # K - Степень и квалификация каз
        # 11: ПРОПУСК (L) - пустая колонка
        12: 'degree_qualification_ru',         # M - Степень и квалификация рус
        # 13: ПРОПУСК (N) - пустая колонка
        14: 'degree_qualification_en',         # O - Степень и квалификация англ
        # 15: ПРОПУСК (P) - пустая колонка
        16: 'with_honors_kz',                  # Q - с отличием каз
        17: 'with_honors_ru',                  # R - с отличием рус
        18: 'with_honors_en',                  # S - с отличием англ
        19: 'specialty',                       # T - Специальность
        20: 'gpa',                             # U - GPA
        21: 'iin',                             # V - ИИН
        22: 'region',                          # W - Регион
        23: 'email',                           # X - email
        24: 'mobile_phone',                    # Y - моб.тел
        25: 'residence'                        # Z - Место проживания
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
                print(f"  Колонка {j} ({chr(65+j)}): {cell_value}")

# Основные функции для работы с данными
def search_graduates(df, **kwargs):
    """Поиск выпускников по различным параметрам"""
    result = df.copy()

    if 'iin' in kwargs:
        result = result[result['iin'].astype(str).str.contains(kwargs['iin'])]

    if 'university' in kwargs:
        result = result[result['university_name'].str.contains(kwargs['university'], case=False, na=False)]

    if 'region' in kwargs:
        result = result[result['region'].str.contains(kwargs['region'], case=False, na=False)]

    if 'specialty' in kwargs:
        result = result[result['specialty'].str.contains(kwargs['specialty'], case=False, na=False)]

    return result

def export_data(df, output_file):
    """Экспорт данных в CSV"""
    df.to_csv(output_file, index=False, encoding='utf-8-sig', sep=';')
    print(f"Данные экспортированы в {output_file}")

# Пример использования
if __name__ == "__main__":
    file_path = "sample_data_kaznu.xlsx"  # Укажите путь к вашему файлу

    # Сначала инспектируем структуру
    inspect_excel_structure(file_path)

    # Парсим данные
    print("\n=== ПАРСИНГ ДАННЫХ ===")
    graduates_df = parse_complex_excel(file_path)

    print(f"Успешно распарсено записей: {len(graduates_df)}")

    if len(graduates_df) > 0:
        print("\nПервые 3 записи:")
        print(graduates_df.head(3))

        # Экспортируем результат
        export_data(graduates_df, "parsed_graduates.csv")

        # Пример поиска
        # found = search_graduates(graduates_df, university="технический")
        # print(f"\nНайдено выпускников: {len(found)}")