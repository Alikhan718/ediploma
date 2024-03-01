# run command # nohup python3 -m flask --app diploma_final.py run --debug &

import re
import textwrap
import warnings

import json
import openpyxl
import qrcode
from PIL import Image, ImageDraw, ImageFont
from flask import request

# Suppress DeprecationWarning for ANTIALIAS in Pillow
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load template
template = Image.open('./ib_diploma.png')

# Set the fonts/ #Need to download them and make a way to them
font1 = ImageFont.truetype('./miamanueva.ttf', size=120)
font2 = ImageFont.truetype('./PTSansNarrow-Regular.ttf', size=50)
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


def generateDiplomaImage(graduate, counter, university_id):
    number = graduate["number"]
    text1 = "We certify that · Nouse Certifons que · Certificamos que"
    text2 = "entered by · presente(e) parl'etablissment scolaire denomme · presentado(a) por el colegio deonminado"
    text3 = "has achieved the following results · a obtenu les resultats suivants · ha obtenido los resultados singuientes"

    text4p1 = "Subjects taken at higher level"
    text4p2 = "Materies presentees au niveau superieur"
    text4p3 = "Asignaturas del Nivel Superior"

    text5p1 = "Grades"
    text5p2 = "Notes"
    text5p3 = "Calificaciones"

    text6p1 = "Subjects taken at standard level"
    text6p2 = "Matieres presentees au niveau moyen"
    text6p3 = "Asignatures del Nivel Medio"

    text7p1 = "Grades"
    text7p2 = "Notes"
    text7p3 = "Calificaciones"

    text8p1 = "Additional requirements"
    text8p2 = "Exigences supplementaries"
    text8p3 = "Requistos adicionales"

    text9 = "Points"
    text10 = "All CAS (Creativity-Activity-Service) requirements have been fully satisfied"
    text11 = "Total"

    # subjects = graduate["subjects"]
    subjects = [
        {"title": "M21 ECONOMICS (ENG)", "grade": "6"},
        {"title": "M21 BIOLOGY (ENG)", "grade": "6"},
        {"title": "M21 FILM (ENG)", "grade": "5"},

        {"title": "M21 ECONOMICS A LANG AND LIT", "grade": "4"},
        {"title": "M21 RUSSIAN A LANG AND LIT", "grade": "5"},
        {"title": "M21 MATH ANALYSIS", "grade": "5"},
    ]
    subjectTitles = [subject["title"] for subject in subjects]
    subjectGrades = [subject["grade"] for subject in subjects]
    totalPoints = 0
    for grade in subjectGrades:
        totalPoints += int(grade)

    half_length = len(subjects) // 2

    subjectTitles1 = subjectTitles[:half_length]
    subjectGrades1 = subjectGrades[:half_length]

    subjectTitles2 = subjectTitles[half_length:]
    subjectGrades2 = subjectGrades[half_length:]

    # additionalSubjects = graduate['additional_subjects']
    # additionalPoints = graduate['additional_points']
    additionalPoints = "2"
    additionalSubjects = [
        {"title": "EXTENDED ESSAY BIOLOGY (ENG)", "grade": "C"},
        {"title": "THEORY OF KNOWLEDGE", "grade": "B"},
    ]
    additionalSubjectTitles = [subject["title"] for subject in additionalSubjects]
    additionalSubjectGrades = [subject["grade"] for subject in additionalSubjects]


    totalPoints += int(additionalPoints)
    name = graduate["name"]
    faculty = graduate["faculty"]
    # Create a copy of the diploma template.
    diploma = template.copy().convert('RGB')
    # Create a draw object for the diploma.
    draw = ImageDraw.Draw(diploma)

    # Calculate the dimensions of each part
    canvas_width, canvas_height = diploma.size
    part_width = canvas_width // 3

    line_spacing = 20

    name_y = 1100

    def putTextVertical(text, name_y, font=None, selectedColor=None):
        color = '#0000'
        selectedFont = font2
        if font:
            selectedFont = font
        if selectedColor:
            color = selectedColor
        text_lines = textwrap.wrap(text, width=150)
        name_width, name_height = draw.textsize('\n'.join(text_lines), font=selectedFont)

        for line in text_lines:
            text_x = canvas_width / 15 
            print(text_x, canvas_height, canvas_width)
            draw.text((text_x, name_y), line, fill=color, font=selectedFont)
            name_y += name_height + line_spacing
        return name_y

    name_y = putTextVertical(text1, name_y)
    name_y = putTextVertical(name, name_y, font3)
    name_y = putTextVertical(text2, name_y)
    name_y = putTextVertical(faculty, name_y, font3) + 100
    temp_name_y = putTextVertical(text3, name_y, font2, 'gray') + 20

    # subjects 1 start
    color = '#0000'
    selectedFont = font2
    text_lines = [text4p1, text4p2, text4p3]
    name_width, name_height = draw.textsize('\n'.join(text_lines), font=selectedFont)
    line_spacing = 1

    # default text
    name_y = temp_name_y
    for line in text_lines:
        text_x = canvas_width / 15 
        print(line, text_x, name_y)
        draw.text((text_x, name_y), line, fill=color, font=selectedFont)
        name_y += name_height / 2.5 + line_spacing

    # subject titles
    name_y += 20
    text_lines = subjectTitles1
    for line in text_lines:
        text_x = canvas_width / 15 
        print(line, text_x, name_y)
        draw.text((text_x, name_y), line, fill=color, font=font3)
        name_y += name_height / 3.5 + line_spacing

    # default text
    name_y = temp_name_y
    text_lines = [text5p1, text5p2, text5p3]
    for line in text_lines:
        text_x = canvas_width / 2.65 
        print(line, text_x, name_y)
        draw.text((text_x, name_y), line, fill=color, font=selectedFont)
        name_y += name_height / 2.5 + line_spacing

    # subject grades
    name_y += 20
    text_lines = subjectGrades1
    for line in text_lines:
        text_x = canvas_width / 2.55 
        print(line, text_x, name_y)
        draw.text((text_x, name_y), line, fill=color, font=font3)
        name_y += name_height / 3.5 + line_spacing
    # subjects 1 end

    # subjects 2 start
    # default text
    name_y = temp_name_y
    text_lines = [text6p1, text6p2, text6p3]
    for line in text_lines:
        text_x = canvas_width / 2 
        print(line, text_x, name_y)
        draw.text((text_x, name_y), line, fill=color, font=selectedFont)
        name_y += name_height / 2.5 + line_spacing

    # subject titles
    name_y += 20
    text_lines = subjectTitles2
    for line in text_lines:
        text_x = canvas_width / 2
        print(line, text_x, name_y)
        draw.text((text_x, name_y), line, fill=color, font=font3)
        name_y += name_height / 3.5 + line_spacing

    name_y = temp_name_y
    text_lines = [text7p1, text7p2, text7p3]
    for line in text_lines:
        text_x = canvas_width / 1.25
        print(line, text_x, name_y)
        draw.text((text_x, name_y), line, fill=color, font=selectedFont)
        name_y += name_height / 2.5 + line_spacing

    # subject grades
    name_y += 20
    text_lines = subjectGrades2
    for line in text_lines:
        text_x = canvas_width / 1.22
        print(line, text_x, name_y)
        draw.text((text_x, name_y), line, fill=color, font=font3)
        name_y += name_height / 3.5 + line_spacing
    # subjects 2 end

    # default text
    name_y += 60
    text_lines = [text8p1, text8p2, text8p3]
    for line in text_lines:
        text_x = canvas_width / 15 
        print(line, text_x, name_y)
        draw.text((text_x, name_y), line, fill=color, font=selectedFont)
        name_y += name_height / 2.5 + line_spacing

    # additional subject titles
    name_y += 20
    temp_name_y = name_y
    text_lines = additionalSubjectTitles
    for line in text_lines:
        text_x = canvas_width / 15 
        print(line, text_x, name_y)
        draw.text((text_x, name_y), line, fill=color, font=font3)
        name_y += name_height / 3.5 + line_spacing

    # additional subject grades
    name_y = temp_name_y
    text_lines = additionalSubjectGrades
    for line in text_lines:
        text_x = canvas_width / 2 
        print(line, text_x, name_y)
        draw.text((text_x, name_y), line, fill=color, font=font3)
        name_y += name_height / 3.5 + line_spacing

    text_x = canvas_width / 15 
    print(text9, text_x, name_y)
    draw.text((text_x, name_y), text9, fill=color, font=font3)

    text_x = canvas_width / 2 
    print(additionalPoints, text_x, name_y)
    draw.text((text_x, name_y), additionalPoints, fill=color, font=font3)
    name_y += name_height / 3 + line_spacing + 20

    text_x = canvas_width / 15 
    print(text10, text_x, name_y)
    draw.text((text_x, name_y), text10, fill=color, font=font3)
    name_y += name_height / 3 + line_spacing + 20
    
    text_x = canvas_width / 15 
    print(text11, text_x, name_y)
    draw.text((text_x, name_y), text11, fill=color, font=font3)

    text_x = canvas_width / 7.9
    print(totalPoints, text_x, name_y)
    draw.text((text_x, name_y), str(totalPoints), fill=color, font=font3)
    name_y += name_height / 3 + line_spacing + 20

    diploma.save(f'./storage/images/{university_id}/diploma.jpeg', 'JPEG')


def parseData(file, university_id):
    # Load the Excel file
    workbook = openpyxl.load_workbook(file)

    sheet = workbook.active

    # Initialize the variables
    # numbers
    numbers = []
    # names
    names_kaz = []
    names_rus = []
    namesg = []
    # protocols
    protocols_kaz = []
    protocols_rus = []
    protocolsg = []
    # degrees
    degrees_kaz = []
    degrees_rus = []
    degreesg = []
    # qualifications
    qualifications_kaz = []
    qualifications_rus = []
    qualificationsg = []
    # distinctions
    with_distinctions_kaz = []
    with_distinctions_rus = []
    with_distinctionsg = []
    # additional data for analysis
    iin = []
    phone = []
    email = []
    gpa = []
    region = []
    gender = []
    nationality = []
    grant = []
    faculty = []
    diploma_total = []

    fullMetadata = "["
    tempCounter = 0
    # Iterate through rows and columns starting from row 3
    for row in sheet.iter_rows(min_row=1, values_only=True):
        tempCounter += 1
        if tempCounter < 3:
            continue
        # numbers
        numbers.append(row[0])
        # names
        names_kaz.append(row[3])
        names_rus.append(row[4])
        namesg.append(row[5])
        # protocols
        protocols_kaz.append(row[6])
        protocols_rus.append(row[7])
        protocolsg.append(row[8])
        # degrees
        degrees_kaz.append(row[9])
        degrees_rus.append(row[11])
        degreesg.append(row[13])
        # qualifications
        qualifications_rus.append(row[12])
        qualifications_kaz.append(row[10])
        qualificationsg.append(row[14])
        # distinctions
        with_distinctions_kaz.append(row[15])
        with_distinctions_rus.append(row[16])
        with_distinctionsg.append(row[17])
        # additional data for analysis
        iin.append(row[18])
        phone.append(row[19])
        email.append(row[20])
        gpa.append(row[21])
        region.append(row[22])
        gender.append(row[23])
        nationality.append(row[24])
        grant.append(row[25])
        faculty.append(row[26])
        diploma_total.append(row[27])

    # Gain all values separately
    counter = 1
    for i in range(len(names_kaz)):
        graduate = {
            "number": str(numbers[i]).strip(),

            "name_kz": str(names_kaz[i]).strip(),
            "name_ru": str(names_rus[i]).strip(),
            "name": str(namesg[i]).strip(),

            "protocol_kz": str(protocols_kaz[i]).strip().replace("№", "#"),
            "protocol_ru": str(protocols_rus[i]).strip().replace("№", "#"),
            "protocol": str(protocolsg[i]).strip().replace("№", "#"),

            "degree_kz": str(degrees_kaz[i]).upper().strip(),
            "degree_ru": str(degrees_rus[i]).upper().strip(),
            "degree": str(degreesg[i]).upper().strip(),

            "qualification_kz": str(qualifications_kaz[i]).upper().strip(),
            "qualification_ru": str(qualifications_rus[i]).upper().strip(),
            "qualification": str(qualificationsg[i]).upper().strip(),

            "distinction_kz": str(with_distinctions_kaz[i]).upper().strip(),
            "distinction_ru": str(with_distinctions_rus[i]).upper().strip(),
            "distinction": str(with_distinctionsg[i]).upper().strip(),

            "iin": str(iin[i]).strip(),
            "phone": str(phone[i]).strip(),
            "email": str(email[i]).strip(),
            "gpa": float(gpa[i]),
            "region": str(region[i]).strip(),
            "gender": str(gender[i]).strip(),
            "nationality": str(nationality[i]).strip(),
            "grant": str(grant[i]).strip(),
            "faculty": str(faculty[i]).strip(),
            "diploma_total": float(diploma_total[i]),
        }
        metadata = generateDiplomaImage(graduate=graduate, counter=counter, university_id=university_id)
        # Convert the dictionary into a JSON string
        metadata_json = json.dumps(metadata)
        fullMetadata += metadata_json + ("," if i < len(names_kaz) - 1 else "")
        # Create a new file with the JSON data
        filename = f"./json/{counter}.json"
        counter += 1
        with open(filename, "w", encoding="utf-8") as f:
            f.write(metadata_json)
        # break
        # Insert metadata into the database

    fullMetadata += "]"
    with open(f"storage/jsons/{university_id}/fullMetadata.json", "w") as f:
        f.write(fullMetadata)


def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return {'error': 'File required'}
        if 'university_id' not in request.values:
            return {'error': 'No university ID'}

        university_id = request.form.get('university_id')
        try:
            images_folder = f"storage/images/{university_id}"
            archive_folder = f"storage/archives"
            jsons_folder = f"storage/jsons/{university_id}"

        except Exception as e:
            return {"error": str(e)}, 500
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return {'error': 'No selected file'}
        return parseData(file, university_id)
    return 'here'


excluded_paths = ['storage', 'json']


def should_reload(filename):
    # Check if the file is in an excluded path
    for excluded_path in excluded_paths:
        if filename.startswith(excluded_path):
            return False
    return True


graduate = {
    "number": 12312312,
    "name": "Syrym Serikov",
    "faculty": "Nazarbaev Intellectual School in Nur-Sultan"
}
generateDiplomaImage(graduate, 1, 1)
