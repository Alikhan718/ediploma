# run command # python3 -m flask --app diploma_final.py run --host=0.0.0.0 --debug &

import hashlib
import os
import random
import re
import string
import subprocess
import textwrap
import warnings
import zipfile
from datetime import datetime
from io import BytesIO

import openpyxl
import psycopg2
import qrcode
import requests
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, send_file, request
from flask_cors import CORS
from psycopg2.extras import execute_values

import json
from pinatatest import pin_folder_to_ipfs

users = []
progresses = {}
# base_url = "http://127.0.0.1:5000"
base_url = "https://generator.ediploma.kz"


def zip_folder(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname=arcname)


# Suppress DeprecationWarning for ANTIALIAS in Pillow
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Load template
template = Image.open('./diploma_template.png')

# Set the fonts/ #Need to download them and make a way to them
font1 = ImageFont.truetype('./miamanueva.ttf', size=30)
font2 = ImageFont.truetype('./Alice-Regular.ttf', size=23)
font3 = ImageFont.truetype('./Alice-Regular.ttf', size=15)
font4 = ImageFont.truetype('./Alice-Regular.ttf', size=22)
font5 = ImageFont.truetype('./Alice-Regular.ttf', size=22)  ##2a4a62


def generate_short_hash(text):
    # Create an SHA-256 hash object
    sha256 = hashlib.sha256()

    # Update the hash object with the input text
    sha256.update(text.encode('utf-8'))

    # Get the hexadecimal digest of the hash and take the first 12 characters
    short_hash = sha256.hexdigest()[:12]
    return short_hash


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


app = Flask(__name__)
CORS(app)


# Remove invalid characters
def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|\n\t]', '', filename)


def draw_distinction_text(draw, font, part_x, part_y, text_lines, color):
    filtered_lines = [line for line in text_lines if line != "NONE"]
    text_width, text_height = draw.textsize('\n'.join(filtered_lines), font=font)
    text_x = part_x - text_width // 2
    text_y = part_y - text_height // 2
    for line in filtered_lines:
        line_width, line_height = draw.textsize(line, font=font)
        line_x = text_x + (text_width - line_width) // 2  # Center-align the text
        draw.text((line_x, text_y), line, fill=color, font=font)
        text_y += line_height


def wrap_text_with_newlines(text, width):
    lines = []
    for part in text.split("\n"):
        lines.extend(textwrap.wrap(part, width=width))
    return lines


def createTableIfNotExists(cursor):
    try:
        # Define the SQL statement to create the table if it doesn't exist
        create_table_query = """
                             CREATE TABLE IF NOT EXISTS upload_diplomas
                             (
                                 id            SERIAL PRIMARY KEY,
                                 hash_id       varchar(12),
                                 value JSONB,
                                 university_id INTEGER,
                                 created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                 updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                 deleted_at    TIMESTAMP
                             ) \
                             """
        # Execute the SQL statement
        cursor.execute(create_table_query)
    except psycopg2.Error as e:
        print("Error creating the table:", e)


def createFolderIfNotExists(folder_path):
    if not os.path.exists(folder_path):
        try:
            # Create the folder if it doesn't exist
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' created successfully.")
        except Exception as e:
            print(f"An error occurred while creating folder '{folder_path}': {e}")
    else:
        print(f"Folder '{folder_path}' already exists.")


def generateDiplomaImage(graduate, counter, university_id):
    number = graduate["number"]
    name_kz = graduate["name_kz"]
    name_ru = graduate["name_ru"]
    name_en = graduate["name_en"]
    protocol_kz = graduate["protocol_kz"]
    protocol_ru = graduate["protocol_ru"]
    protocol_en = graduate["protocol_en"]
    degree_kz = graduate["degree_kz"]
    degree_ru = graduate["degree_ru"]
    degree_en = graduate["degree_en"]
    qualification_kz = graduate["qualification_kz"]
    qualification_ru = graduate["qualification_ru"]
    qualification_en = graduate["qualification_en"]
    distinction_kz = graduate["distinction_kz"]
    distinction_ru = graduate["distinction_ru"]
    distinction_en = graduate["distinction_en"]
    iin = graduate["iin"]
    phone = graduate["phone"]
    email = graduate["email"]
    gpa = graduate["gpa"]
    region = graduate["region"]
    gender = graduate["gender"]
    nationality = graduate["nationality"]
    grant = graduate["grant"]
    faculty = graduate["faculty"]
    diploma_total = graduate["diploma_total"]
    # Create a copy of the diploma template.
    diploma = template.copy().convert('RGB')
    # Create a draw object for the diploma.
    draw = ImageDraw.Draw(diploma)
    # Make for file name
    name_file = f"{name_en.replace(' ', '_')}_{number}"
    # Sanitize the filename
    name_file = sanitize_filename(name_file)

    # Calculate the dimensions of each part
    canvas_width, canvas_height = diploma.size
    part_width = canvas_width // 3
    part_height = canvas_height

    # Calculate the center coordinates for each part
    part1_x = part_width // 2
    part1_y = canvas_height // 2.9

    part2_x = part_width + (part_width // 2)
    part2_y = canvas_height // 2.9

    part3_x = (part_width * 2) + (part_width // 2)
    part3_y = canvas_height // 2.9

    # Define line spacing
    line_spacing = 3

    # Wrap the text if it exceeds the line width
    name_kz_lines = textwrap.wrap(name_kz, width=25)
    name_ru_lines = textwrap.wrap(name_ru, width=25)
    name_en_lines = textwrap.wrap(name_en, width=25)

    # Draw the names in the middle of each part
    name_width_kz, name_height_kz = draw.textsize('\n'.join(name_kz_lines), font=font1)
    name_x_kz = part1_x - name_width_kz // 2
    name_y_kz = part1_y - (name_height_kz * len(name_kz_lines) + line_spacing * (len(name_kz_lines) - 1)) // 2

    for line in name_kz_lines:
        text_width, text_height = draw.textsize(line, font=font1)
        text_x = name_x_kz + (name_width_kz - text_width) // 2  # Center-align the text
        draw.text((text_x, name_y_kz), line, fill='#FFD700', font=font1)
        name_y_kz += name_height_kz + line_spacing

    name_width_ru, name_height_ru = draw.textsize('\n'.join(name_ru_lines), font=font1)
    name_x_ru = part2_x - name_width_ru // 2
    name_y_ru = part2_y - (name_height_ru * len(name_ru_lines) + line_spacing * (len(name_ru_lines) - 1)) // 2
    for line in name_ru_lines:
        text_width, text_height = draw.textsize(line, font=font1)
        text_x = name_x_ru + (name_width_ru - text_width) // 2  # Center-align the text
        draw.text((text_x, name_y_ru), line, fill='#FFD700', font=font1)
        name_y_ru += name_height_ru + line_spacing

    name_width_en, name_height_en = draw.textsize('\n'.join(name_en_lines), font=font1)
    name_x_en = part3_x - name_width_en // 2
    name_y_en = part3_y - (name_height_en * len(name_en_lines) + line_spacing * (len(name_en_lines) - 1)) // 2
    for line in name_en_lines:
        text_width, text_height = draw.textsize(line, font=font1)
        text_x = name_x_en + (name_width_en - text_width) // 2  # Center-align the text
        draw.text((text_x, name_y_en), line, fill='#FFD700', font=font1)
        name_y_en += name_height_en + line_spacing

    # Add with distinction (only if not empty)
    if distinction_ru is not None and distinction_ru.strip() != "":
        # Calculate the center coordinates for each part
        part1_y = canvas_height * 8.5 // 14
        part2_y = canvas_height * 8.5 // 14
        part3_y = canvas_height * 8.5 // 14

        # Wrap the text if it exceeds the line width
        distinction_kz_lines = textwrap.wrap(distinction_kz, width=20)
        distinction_ru_lines = textwrap.wrap(distinction_ru, width=20)
        distinction_en_lines = textwrap.wrap(distinction_en, width=20)

        # Draw the distinction text in the middle of each part
        draw_distinction_text(draw, font2, part1_x, part1_y, distinction_kz_lines, '#5c92c7')
        draw_distinction_text(draw, font2, part2_x, part2_y, distinction_ru_lines, '#5c92c7')
        draw_distinction_text(draw, font2, part3_x, part3_y, distinction_en_lines, '#5c92c7')

    # Qualifications
    # Calculate the center coordinates for each part
    part1_y = canvas_height // 2.5
    part2_y = canvas_height // 2.5
    part3_y = canvas_height // 2.5

    degree_color = "#2a4a62"
    qualification_color = "#5c92c7"

    # Combine the degree and qualification text
    qualification_kz = qualification_kz + "\n" + degree_kz
    qualification_ru = degree_ru + "\n" + qualification_ru
    qualification_en = degree_en + "\n" + qualification_en
    # Wrap the text if it exceeds the line width
    qualification_kz_lines = wrap_text_with_newlines(qualification_kz, width=35)
    qualification_ru_lines = wrap_text_with_newlines(qualification_ru, width=35)
    qualification_en_lines = wrap_text_with_newlines(qualification_en, width=35)

    # Draw the text for the Kazakh language
    y = part1_y
    for line in qualification_kz_lines:
        if line.strip() == degree_kz.strip():
            color = degree_color
        else:
            color = qualification_color
        text_width, text_height = draw.textsize(line, font=font2)
        text_x = part1_x - text_width // 2
        draw.text((text_x, y), line, fill=color, font=font2)
        y += text_height

    # Draw the text for the Russian language
    y = part2_y
    for line in qualification_ru_lines:
        if line.strip() == degree_ru.strip():
            color = degree_color
        else:
            color = qualification_color
        text_width, text_height = draw.textsize(line, font=font2)
        text_x = part2_x - text_width // 2
        draw.text((text_x, y), line, fill=color, font=font2)
        y += text_height

    # Draw the text for the English language
    y = part3_y
    for line in qualification_en_lines:
        if line.strip() == degree_en.strip():
            color = degree_color
        else:
            color = qualification_color
        text_width, text_height = draw.textsize(line, font=font2)
        text_x = part3_x - text_width // 2
        draw.text((text_x, y), line, fill=color, font=font2)
        y += text_height
    # Protocols
    # Calculate the center coordinates for each part
    part1_y = canvas_height // 4.2
    part2_y = canvas_height // 4.2
    part3_y = canvas_height // 4.2

    # Wrap the text if it exceeds the line width
    protocol_kz_lines = textwrap.wrap(protocol_kz, width=45)
    protocol_ru_lines = textwrap.wrap(protocol_ru, width=35)
    protocol_en_lines = textwrap.wrap(protocol_en, width=35)

    # Draw the names in the middle of each part
    protocol_width_kz, protocol_height_kz = draw.textsize('\n'.join(protocol_kz_lines), font=font4)
    protocol_x_kz = part1_x - protocol_width_kz // 2
    protocol_y_kz = part1_y - protocol_height_kz // 2
    for line in protocol_kz_lines:
        text_width, text_height = draw.textsize(line, font=font4)
        text_x = protocol_x_kz + (protocol_width_kz - text_width) // 2  # Center-align the text
        draw.text((text_x, protocol_y_kz), line, fill='#5c92c7', font=font4)
        protocol_y_kz += protocol_height_kz + 2  # Add a small fixed spacing between lines

    protocol_width_ru, protocol_height_ru = draw.textsize('\n'.join(protocol_ru_lines), font=font4)
    protocol_x_ru = part2_x - protocol_width_ru // 2
    protocol_y_ru = part2_y - protocol_height_ru // 2
    for line in protocol_ru_lines:
        text_width, text_height = draw.textsize(line, font=font4)
        text_x = protocol_x_ru + (protocol_width_ru - text_width) // 2  # Center-align the text
        draw.text((text_x, protocol_y_ru), line, fill='#5c92c7', font=font4)
        protocol_y_ru += protocol_height_ru + 2  # Add a small fixed spacing between lines

    protocol_width_en, protocol_height_en = draw.textsize('\n'.join(protocol_en_lines), font=font4)
    protocol_x_en = part3_x - protocol_width_en // 2
    protocol_y_en = part3_y - protocol_height_en // 2
    for line in protocol_en_lines:
        text_width, text_height = draw.textsize(line, font=font4)
        text_x = protocol_x_en + (protocol_width_en - text_width) // 2  # Center-align the text
        draw.text((text_x, protocol_y_en), line, fill='#5c92c7', font=font4)
        protocol_y_en += protocol_height_en + 2  # Add a small fixed spacing between lines
        # Study type
    # Calculate the center coordinates for each part
    part1_y = canvas_height * 2 // 3
    part2_y = canvas_height * 2 // 3
    part3_y = canvas_height * 2 // 3

    # Wrap the text if it exceeds the line width
    study_kz_lines = textwrap.wrap("ОҚЫТУ НЫСАНЫ КҮНДІЗГІ", width=100)
    study_ru_lines = textwrap.wrap("ФОРМА ОБУЧЕНИЯ ОЧНАЯ", width=100)
    study_en_lines = textwrap.wrap("FORM OF TRAINING FULL-TIME", width=100)

    # Draw the names in the middle of each part
    study_width_kz, study_height_kz = draw.textsize('\n'.join(study_kz_lines), font=font3)
    study_x_kz = part1_x - study_width_kz // 2
    study_y_kz = part1_y - (study_height_kz * len(study_kz_lines)) // 2
    for line in study_kz_lines:
        text_width, text_height = draw.textsize(line, font=font3)
        text_x = study_x_kz + (study_width_kz - text_width) // 2  # Center-align the text
        draw.text((text_x, study_y_kz), line, fill='#5c92c7', font=font3)
        study_y_kz += text_height

    study_width_ru, study_height_ru = draw.textsize('\n'.join(study_ru_lines), font=font3)
    study_x_ru = part2_x - study_width_ru // 2
    study_y_ru = part2_y - (study_height_ru * len(study_ru_lines)) // 2
    for line in study_ru_lines:
        text_width, text_height = draw.textsize(line, font=font3)
        text_x = study_x_ru + (study_width_ru - text_width) // 2  # Center-align the text
        draw.text((text_x, study_y_ru), line, fill='#5c92c7', font=font3)
        study_y_ru += text_height

    study_width_en, study_height_en = draw.textsize('\n'.join(study_en_lines), font=font3)
    study_x_en = part3_x - study_width_en // 2
    study_y_en = part3_y - (study_height_en * len(study_en_lines)) // 2
    for line in study_en_lines:
        text_width, text_height = draw.textsize(line, font=font3)
        text_x = study_x_en + (study_width_en - text_width) // 2  # Center-align the text
        draw.text((text_x, study_y_en), line, fill='#5c92c7', font=font3)
        study_y_en += text_height

    # Add QR code
    qr_size = int(diploma.width * (1.6 / 23))

    qr = qrcode.QRCode(box_size=1)
    qr.add_data(f'https://ediploma.kz/')  # do after we do portal
    qr.make(fit=True)

    img_qr = qr.make_image(fill_color="black", back_color="white").resize((qr_size, qr_size), Image.ANTIALIAS)
    margin = int(diploma.width * (0.5 / 23))
    qr_pos = (diploma.width - qr_size - margin, diploma.height - qr_size - margin)

    diploma.paste(img_qr, qr_pos)
    folder_path = f"./storage/images/{university_id}"
    createFolderIfNotExists(folder_path)
    # Save the diploma as a new image file.
    diploma.save(f'./storage/images/{university_id}/{name_file}.jpeg', 'JPEG')
    metadata = {
        "description": f"KBTU 2023 Graduate {name_file}",
        "image": f"https://generator.ediploma.kz/get-file/{name_file}.jpeg",
        "name": name_en,
        "counter": counter,
        "attributes": [
            {"name": "name_kz", "value": name_kz},
            {"name": "name_ru", "value": name_ru},
            {"name": "name_en", "value": name_en},
            {"name": "protocol_kz", "value": protocol_kz},
            {"name": "protocol_ru", "value": protocol_ru},
            {"name": "protocol_en", "value": protocol_en},
            {"name": "degree_kz", "value": degree_kz},
            {"name": "degree_ru", "value": degree_ru},
            {"name": "degree_en", "value": degree_en},
            {"name": "qualification_kz", "value": qualification_kz},
            {"name": "qualification_ru", "value": qualification_ru},
            {"name": "qualification_en", "value": qualification_en},
            {"name": "distinction_kz", "value": distinction_kz},
            {"name": "distinction_ru", "value": distinction_ru},
            {"name": "iin", "value": iin},
            {"name": "phone", "value": phone},
            {"name": "email", "value": email},
            {"name": "gpa", "value": gpa},
            {"name": "region", "value": region},
            {"name": "gender", "value": gender},
            {"name": "nationality", "value": nationality},
            {"name": "grant", "value": grant},
            {"name": "faculty", "value": faculty},
            {"name": "diploma_total", "value": diploma_total},

        ]
    }
    return metadata


def parseData(file, university_id):
    # Load the Excel file
    connection, cursor = connectDatabase()
    if connection is None or cursor is None:
        return {"error": "Error connecting to the database."}
    else:
        createTableIfNotExists(cursor)

    workbook = openpyxl.load_workbook(file)

    sheet = workbook.active

    # Initialize the variables
    # numbers
    numbers = []
    # names
    names_kaz = []
    names_rus = []
    names_eng = []
    # protocols
    protocols_kaz = []
    protocols_rus = []
    protocols_eng = []
    # degrees
    degrees_kaz = []
    degrees_rus = []
    degrees_eng = []
    # qualifications
    qualifications_kaz = []
    qualifications_rus = []
    qualifications_eng = []
    # distinctions
    with_distinctions_kaz = []
    with_distinctions_rus = []
    with_distinctions_eng = []
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
        names_eng.append(row[5])
        # protocols
        protocols_kaz.append(row[6])
        protocols_rus.append(row[7])
        protocols_eng.append(row[8])
        # degrees
        degrees_kaz.append(row[9])
        degrees_rus.append(row[11])
        degrees_eng.append(row[13])
        # qualifications
        qualifications_rus.append(row[12])
        qualifications_kaz.append(row[10])
        qualifications_eng.append(row[14])
        # distinctions
        with_distinctions_kaz.append(row[15])
        with_distinctions_rus.append(row[16])
        with_distinctions_eng.append(row[17])
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
            "name_en": str(names_eng[i]).strip(),

            "protocol_kz": str(protocols_kaz[i]).strip().replace("№", "#"),
            "protocol_ru": str(protocols_rus[i]).strip().replace("№", "#"),
            "protocol_en": str(protocols_eng[i]).strip().replace("№", "#"),

            "degree_kz": str(degrees_kaz[i]).upper().strip(),
            "degree_ru": str(degrees_rus[i]).upper().strip(),
            "degree_en": str(degrees_eng[i]).upper().strip(),

            "qualification_kz": str(qualifications_kaz[i]).upper().strip(),
            "qualification_ru": str(qualifications_rus[i]).upper().strip(),
            "qualification_en": str(qualifications_eng[i]).upper().strip(),

            "distinction_kz": str(with_distinctions_kaz[i]).upper().strip(),
            "distinction_ru": str(with_distinctions_rus[i]).upper().strip(),
            "distinction_en": str(with_distinctions_eng[i]).upper().strip(),

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
        try:
            shorthash = generate_short_hash(graduate["name_en"] + str(counter - 1))
            print("parse/ ", graduate["name_en"], counter - 1, shorthash)

            # Check if the record exists in the database
            cursor.execute("SELECT id FROM upload_diplomas WHERE hash_id = %s AND deleted_at IS NULL", (shorthash,))
            existing_record = cursor.fetchone()

            if existing_record:
                # If the record exists, update it
                cursor.execute(
                    "UPDATE upload_diplomas SET value = %s, university_id = %s WHERE hash_id = %s AND deleted_at IS NULL",
                    (metadata_json, university_id, shorthash)
                )
            else:
                cursor.execute(
                    "INSERT INTO upload_diplomas (value, university_id, hash_id) VALUES (%s, %s, %s)",
                    (metadata_json, university_id, shorthash)
                )
            connection.commit()
        except psycopg2.Error as e:
            print("Error inserting data into the database:", e)

    fullMetadata += "]"
    createFolderIfNotExists(f"storage/jsons/{university_id}")
    with open(f"storage/jsons/{university_id}/fullMetadata.json", "w") as f:
        f.write(fullMetadata)
    # file_path = os.path.join('./', "storage/fullMetadata.json")
    # # Check if the file exists
    # if os.path.isfile(file_path):
    #     # Return the file
    #     return send_file(file_path)
    try:
        createFolderIfNotExists(f"storage/archives")
        zip_folder(folder_path=f"storage/images/{university_id}", zip_path=f"storage/archives/{university_id}.zip")
        return f"https://generator.ediploma.kz/get-file/archives/{university_id}.zip"
    except Exception as e:
        return {"error": str(e)}, 500


def upload_file(file_path, url, headers, parent_cid=None):
    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file)}
        if parent_cid:
            headers['X-IPFS-PATH'] = f'{parent_cid}/'
        response = requests.post(url, files=files, headers=headers)
        if response.status_code == 200:
            data = response.json()
            cid = data['value']['cid']
            print(f"Uploaded {file_path}. CID: {cid}")
            return cid
        else:
            print(f"Error uploading {file_path}. Status Code: {response.status_code}, Response: {response.text}")
            return None


@app.route("/nft/upload/<university_id>", methods=["GET"])
def uploadToNFT(university_id, file_directory="storage/images/"):
    file_directory += str(university_id)
    res = pin_folder_to_ipfs(file_directory)

    # Check the response
    if res and res['IpfsHash']:
        return res['IpfsHash']
    return None


# def uploadToNFT(university_id, file_directory="storage/images/"):
#     file_directory += str(university_id)
#     url = "https://api.nft.storage/upload"
#
#     # List all files in the directory
#     file_names = os.listdir(file_directory)
#
#     # Create a dictionary to hold the files
#     files = []
#     for file_name in file_names:
#         file_path = os.path.join(file_directory, file_name)
#         files.append(('file', (file_name, open(file_path, 'rb'))))
#
#     token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweEMxM2ZiNGExNUQxNzkyMjQ0MjcxQ2U5MzY0ZDI5OTdjMUI1NTY1NTciLCJpc3MiOiJuZnQtc3RvcmFnZSIsImlhdCI6MTY5NjA5NTg1NDY2MCwibmFtZSI6Imphc2FpbSJ9.84ZE8_mZ227yn5p4j8F5y67M4_df9afEYNfaJ60B6bg"
#     # Send the request
#     headers = {
#         'Authorization': f'Bearer {token}'
#     }
#
#     response = requests.post(url, files=files, headers=headers)
#
#     # Check the response
#     if response.status_code == 200:
#         data = response.json()
#         cid = data['value']['cid']
#         return cid
#     else:
#         print("Error:", response.status_code, response.text)

# def uploadToNFT(university_id, file_directory="storage/images/"):
#     file_directory += str(university_id)
#     url = "https://api.nft.storage/upload"
#     token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweEMxM2ZiNGExNUQxNzkyMjQ0MjcxQ2U5MzY0ZDI5OTdjMUI1NTY1NTciLCJpc3MiOiJuZnQtc3RvcmFnZSIsImlhdCI6MTY5NjA5NTg1NDY2MCwibmFtZSI6Imphc2FpbSJ9.84ZE8_mZ227yn5p4j8F5y67M4_df9afEYNfaJ60B6bg"  # Replace with your actual API token
#     headers = {'Authorization': f'Bearer {token}'}
#
#     # List all files in the directory
#     file_names = os.listdir(file_directory)
#
#     # Upload the first file and get the CID
#     first_file_path = os.path.join(file_directory, file_names[0])
#     first_cid = upload_file(first_file_path, url, headers)
#
#     if first_cid:
#         # Upload the remaining files using the first CID in parallel
#         with ThreadPoolExecutor() as executor:
#             futures = [executor.submit(upload_file, os.path.join(file_directory, file_name), url, headers,
#                                        parent_cid=first_cid) for file_name in file_names[1:]]
#
#         # Wait for all tasks to complete
#         wait(futures)
#
#         # Return the common CID
#         return first_cid
#
#     # Return None if the upload of the first file fails
#     return None


# def uploadToNFT(university_id, file_directory="storage/images/"):
#     file_directory += str(university_id)
#     url = "https://api.nft.storage/upload"
#
#     # List all files in the directory
#     file_names = os.listdir(file_directory)
#
#     # Create a dictionary to hold the files
#     files = []
#     for file_name in file_names:
#         file_path = os.path.join(file_directory, file_name)
#         files.append(('file', (file_name, open(file_path, 'rb'))))
#
#     token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkaWQ6ZXRocjoweEMxM2ZiNGExNUQxNzkyMjQ0MjcxQ2U5MzY0ZDI5OTdjMUI1NTY1NTciLCJpc3MiOiJuZnQtc3RvcmFnZSIsImlhdCI6MTY5NjA5NTg1NDY2MCwibmFtZSI6Imphc2FpbSJ9.84ZE8_mZ227yn5p4j8F5y67M4_df9afEYNfaJ60B6bg"
#     # Send the request
#     headers = {
#         'Authorization': f'Bearer {token}'
#     }
#
#     response = requests.post(url, files=files, headers=headers)
#
#     # Check the response
#     if response.status_code == 200:
#         data = response.json()
#         cid = data['value']['cid']
#         return cid
#     else:
#         print("Error:", response.status_code, response.text)
#


@app.route("/nft/generate/<university_id>", methods=["GET"])
def generateIPFS(university_id):
    # Upload images
    if int(university_id) < 3:
        imagesCid = uploadToNFT(university_id, "storage/images/")
        print(f"Uploaded images: {imagesCid}")

        # Update metadata with the image CID
        updateMetaData(university_id, imagesCid)

        # Upload metadata
        metaDataCid = uploadToNFT(university_id, "storage/jsons/")
    else:
        try:
            connection, cursor = connectDatabase()
            cursor.execute(
                "SELECT university_id, hash, id from diploma_generations where finished_at is null order by id desc")

            diploma_generations_record = cursor.fetchone()
            if not diploma_generations_record:
                return {"error": "Error uploading to IPFS"}, 500
            metadata_hash = diploma_generations_record[1]

            # Upload metadata
            metaDataCid = uploadToNFT(metadata_hash, "storage/jsons/")
        except Exception as e:
            print(e)
            return {"error": "Error uploading to IPFS"}, 500
    print(f"Uploaded metadata: {metaDataCid}")

    # Save metadata CID
    saveMetaDataCid(university_id, metaDataCid)
    print(f"CID saved: {metaDataCid}")
    if int(university_id) < 3:
        # Save diploma
        diplomaSave(metaDataCid, university_id)
        print(f"Inserted diplomas to database ")

    return {
        "cid": metaDataCid,
        "university_id": university_id,
        "name": "KBTU",
        "symbol": "KBTU24"
    }, 200


@app.route("/123/<university_id>/<cid>", methods=["GET"])
def updateMetaData(university_id, images_cid):
    try:
        fullMetaData = None
        file_path = f"storage/jsons/{university_id}/fullMetadata.json"
        with open(file_path, "r") as f:
            fullMetaData = json.loads(f.read())
            f.close()
        for i in range(len(fullMetaData)):
            temp = fullMetaData[i]['image']
            temp = temp.split('get-file/')
            if len(temp) > 1:
                temp = temp[1]
                link = f"https://ipfs.io/ipfs/{images_cid}/{temp}"
                fullMetaData[i]['image'] = link
        with open(file_path, "w") as f:
            f.write(json.dumps(fullMetaData))
            f.close()

        return file_path
    except Exception as e:
        return {"error": str(e)}, 500


def saveMetaDataCid(university_id, metadata_cid):
    try:
        connection, cursor = connectDatabase()
        cursor.execute("SELECT * FROM universities WHERE id = %s", (university_id,))
        existing_record = cursor.fetchone()

        if existing_record:
            # If the record exists, update it
            existing_data = existing_record[3]
            existing_data.append(metadata_cid)
            cursor.execute(
                "UPDATE universities SET cids = %s, publish_amount = %s WHERE id = %s",
                (existing_data, existing_record[4] - 1, university_id,)
            )
            connection.commit()
            return True
        else:
            return {"error": "No query results for " + university_id}

    except Exception as e:
        return {"error": str(e)}, 500


@app.route('/diploma/save/<cid>/<university_id>')
def diplomaSave(cid, university_id):
    url = f"https://ipfs.io/ipfs/{cid}/fullMetadata.json"
    response = requests.get(url)

    # Check the response
    if response.status_code == 200:
        body = response.json()

        requiredAttr = [
            "name_en",
            "name_ru",
            "name_kz",
            "university_id",
            "year",
            "qualification_en",
            "qualification_kz",
            "qualification_ru"
        ]
        dataList = []
        fieldsList = []
        try:
            connection, cursor = connectDatabase()
            diploma_id = -1
            for item in body:

                data = {'image': item['image']}
                contentFields = {}
                attributes = item['attributes']

                data['year'] = 2023
                for attr in attributes:
                    if attr['name'] == 'number':
                        continue

                    # if attr['name'] == 'protocol_kz':

                    if attr['name'] in requiredAttr:
                        data[attr['name']] = attr['value']
                    else:
                        contentFields[attr['name']] = attr['value']

                dataList.append(data)
                fieldsList.append(contentFields)

                # Construct and execute the SQL query to insert data into
                # the database
                query = (
                    "INSERT INTO diplomas("
                    "name_en, name_ru, name_kz, university_id, year, "
                    "speciality_en, speciality_ru, speciality_kz, image"
                    ") "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) "
                    "RETURNING id"
                )
                values = (
                    data["name_en"], data["name_ru"], data["name_kz"],
                    university_id, data["year"],
                    data["qualification_en"], data["qualification_ru"],
                    data["qualification_kz"],
                    data["image"]
                )

                cursor.execute(query, values)

                # Retrieve the ID of the inserted record
                diploma_id = cursor.fetchone()[0]
                connection.commit()

                # inserting additional fields
                for key, val in contentFields.items():
                    query = (
                        "INSERT INTO content_fields(type, value, content_id) "
                        "VALUES (%s, %s, %s)"
                    )
                    values = ("diploma_" + key, val, diploma_id)

                    cursor.execute(query, values)

                connection.commit()

        except Exception as e:
            return {"error": str(e)}, 500
    else:
        print("Error:", response.status_code, response.text)
    return {"message": "success"}, 200


def removeFolder(folder_path):
    try:
        # List all files in the folder
        files = os.listdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), folder_path))
        print(files)
        # Iterate over the files and delete each one
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)

            os.remove(file_path)
            print(f"File '{folder_path}' has been successfully deleted.")

        print(f"All files in the folder '{folder_path}' have been deleted.")
    except OSError as e:
        print(f"Error: {e}")


def run_python_file_in_background(file_path, log_file='python_script.log',
                                   timeout=None, working_dir=None):
    """
    Запускает Python файл в фоновом режиме - БЕЗОПАСНАЯ версия для systemd
    """
    import subprocess
    import os
    import time
    import tempfile

    # 1. Проверяем файл
    if not os.path.exists(file_path):
        return {"error": f"Файл не найден: {file_path}", "success": False}

    # 2. Создаем безопасный путь для логов в /tmp
    if not log_file.startswith('/'):
        # Используем подпапку в /tmp
        log_dir = f"/tmp/flask_{os.getuid()}_logs"
        os.makedirs(log_dir, exist_ok=True, mode=0o777)
        log_path = os.path.join(log_dir, log_file)
    else:
        log_path = log_file

    # 3. Рабочая директория
    if working_dir is None:
        working_dir = os.path.dirname(file_path) or tempfile.gettempdir()

    # Создаем если нет
    os.makedirs(working_dir, exist_ok=True, mode=0o755)

    try:
        print(f"Запуск: python3 {file_path}")
        print(f"Логи: {log_path}")
        print(f"Рабочая директория: {working_dir}")

        # ОТКРЫВАЕМ лог файл ДО запуска процесса
        with open(log_path, 'a') as log_handle:
            log_handle.write(f"\n{'='*50}\n")
            log_handle.write(f"Запуск в {time.ctime()}\n")
            log_handle.write(f"Команда: python3 {file_path}\n")
            log_handle.flush()

            # ЗАПУСК БЕЗ preexec_fn - это ключевое!
            process = subprocess.Popen(
                ['python3', file_path],
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                cwd=working_dir,
                start_new_session=True,  # Вместо nohup
                shell=False,
                # preexec_fn удален - он вызывает ошибку в systemd!
            )

        pid = process.pid

        # Просто записываем PID в файл (опционально)
        pid_file = f"/tmp/flask_pid_{pid}.txt"
        try:
            with open(pid_file, 'w') as f:
                f.write(str(pid))
                f.write(f"\nLog: {log_path}")
                f.write(f"\nCommand: python3 {file_path}")
                f.write(f"\nStarted: {time.ctime()}")
        except:
            pass  # Не критично

        print(f"✓ Процесс запущен: PID={pid}")

        # Если нужен таймаут
        if timeout:
            import threading
            def kill_timeout():
                time.sleep(timeout)
                try:
                    import signal
                    os.kill(pid, signal.SIGTERM)
                    print(f"Процесс {pid} остановлен по таймауту")
                except:
                    pass

            threading.Thread(target=kill_timeout, daemon=True).start()

        return {
            "success": True,
            "pid": pid,
            "log_file": log_path,
            "pid_file": pid_file,
            "message": "Процесс запущен в фоне"
        }

    except Exception as e:
        error_msg = f"Ошибка: {str(e)}"
        print(f"✗ {error_msg}")

        # Записываем ошибку в лог
        try:
            with open(log_path, 'a') as f:
                f.write(f"\nERROR: {error_msg}\n")
        except:
            pass

        return {
            "success": False,
            "error": error_msg,
            "log_file": log_path
        }


def generate_random_string(length):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))


@app.route('/data/parse', methods=['GET', "POST"])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files \
                and 'type' in request.values \
                and request.form.get('type') != 'api':
            return {'error': 'File required'}
        if 'university_id' not in request.values:
            return {'error': 'No university ID'}
        university_id = request.form.get('university_id')
        generationType = request.form.get('type')
        if int(university_id) < 3 and generationType == 'api':
            return None
        if int(university_id) >= 3:
            try:
                connection, cursor = connectDatabase()

                cursor.execute(
                    "SELECT id, hash FROM diploma_generations WHERE university_id = %s and finished_at is null",
                    (university_id,))
                existing_record = cursor.fetchone()

                if existing_record:
                    # If the record exists, return link to future archive
                    generation_hash = existing_record[1]
                    return f"{base_url}/get-file/archives/{generation_hash}.zip"
                else:
                    generation_hash = generate_random_string(8)
                    cursor.execute(
                        "INSERT into diploma_generations(hash, university_id, progress, max_progress) values (%s, %s, 0, -1)",
                        (generation_hash, university_id,)
                    )
                    connection.commit()
                    generator_path = "/var/www/generator/diploma_satpaev.py"
                    if int(university_id) == 8:
                        generator_path = "/var/www/generator/diploma_kaznu.py"
                    file = request.files['file']
                    # Проверка на пустой файл
                    if file.filename == '':
                        return 'No selected file', 400
                    upload_folder = f"/var/www/generator/storage/files/{generation_hash}"
                    createFolderIfNotExists(upload_folder)
                    # Сохраняем файл
                    file.save(os.path.join(upload_folder, 'data.xlsx'))
                    # Запускаем генерацию в фоне
                    run_python_file_in_background(generator_path,
                                                  log_file=f"/var/www/generator/storage/logs/{generation_hash}.log")
                    return f"{base_url}/get-file/archives/{generation_hash}.zip"

            except Exception as e:
                print(e)
                return "false"
    return "true"
    #     try:
    #         images_folder = f"storage/images/{university_id}"
    #         archive_folder = f"storage/archives"
    #         jsons_folder = f"storage/jsons/{university_id}"
    #         removeFolder(images_folder)
    #         removeFolder(archive_folder)
    #         removeFolder(jsons_folder)
    #         connection, cursor = connectDatabase()
    #
    #         if connection is None or cursor is None:
    #             return {"error": "Error connecting to the database."}
    #         cursor.execute("SELECT publish_amount FROM universities WHERE id = %s", (university_id,))
    #         existing_record = cursor.fetchone()
    #
    #         if existing_record:
    #             publish_amount = existing_record[0]
    #             if publish_amount <= 0:
    #                 return {"error": "Вы исчерпали кол-во генераций"}, 403
    #
    #
    #     except Exception as e:
    #         return {"error": str(e)}, 500
    #     connection.commit()
    #     file = request.files['file']
    #     # If the user does not select a file, the browser submits an
    #     # empty file without a filename.
    #     if file.filename == '':
    #         return {'error': 'No selected file'}
    #     return parseData(file, university_id)
    # return 'here'


@app.route("/transcript/parse/<university_id>", methods=["POST"])
def transcript_parse(university_id):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files \
                and 'type' in request.values \
                and request.form.get('type') != 'api':
            return {"success": False, 'error': 'Файл не загружен'}

        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return {'error': 'No selected file'}
        return parseTranscriptData(file, university_id)
    return {"success": True}


def parseTranscriptData(file, university_id):
    """
    Парсинг Excel файла с транскриптами и сохранение в базу данных

    Формат Excel:
    №	ИИН Студента	ФИО студента	Название предмета - Каз	Название предмета - Рус	Название предмета - Анг	Оценка
    """
    try:
        # Подключение к базе данных
        connection, cursor = connectDatabase()
        if connection is None or cursor is None:
            return {"error": "Error connecting to the database."}

        # Создаем таблицу если не существует
        createTableIfNotExists(cursor)

        file_content = file.read()

        # Используем BytesIO для работы с файлом в памяти
        excel_file = BytesIO(file_content)
        workbook = openpyxl.load_workbook(excel_file, data_only=True)
        sheet = workbook.active

        # Инициализируем массивы для данных
        numbers = []
        iins = []
        student_names = []
        subjects_kz = []
        subjects_ru = []
        subjects_en = []
        scores = []

        # Парсим данные из Excel
        tempCounter = 0
        for row in sheet.iter_rows(min_row=1, values_only=True):
            tempCounter += 1
            if tempCounter < 2:  # Пропускаем заголовок (предполагаем, что заголовок в первой строке)
                continue

            # Проверяем, что строка не пустая
            if row[0] is None and row[1] is None and row[2] is None:
                continue

            # Сохраняем данные
            numbers.append(row[0])
            iins.append(row[1])
            student_names.append(row[2])
            subjects_kz.append(row[3])
            subjects_ru.append(row[4])
            subjects_en.append(row[5])
            scores.append(row[6])

        # Обрабатываем данные и сохраняем в базу
        transcripts_data = []
        inserted_count = 0
        skipped_count = 0
        error_count = 0

        for i in range(len(iins)):
            try:
                # Очищаем и валидируем данные
                number = clean_value(numbers[i])
                iin = clean_iin(iins[i])
                student_name = clean_value(student_names[i])
                subject_kz = clean_value(subjects_kz[i])
                subject_ru = clean_value(subjects_ru[i])
                subject_en = clean_value(subjects_en[i])
                score = clean_score(scores[i])

                # Проверяем обязательные поля
                if not iin:
                    print(f"⚠️ Строка {i + 1}: пропущена - отсутствует ИИН")
                    error_count += 1
                    continue

                if not subject_en:
                    print(f"⚠️ Строка {i + 1}: пропущена - отсутствует название предмета на английском")
                    error_count += 1
                    continue

                # Проверяем длину ИИН
                if len(iin) != 12:
                    print(f"⚠️ Строка {i + 1}: ИИН '{iin}' имеет некорректную длину ({len(iin)} вместо 12)")
                    error_count += 1
                    continue

                # Проверяем оценку
                if score is not None:
                    try:
                        score_int = int(score)
                        if not (0 <= score_int <= 100):
                            print(f"⚠️ Строка {i + 1}: оценка '{score}' вне диапазона 0-100")
                            score = None  # Устанавливаем None вместо некорректной оценки
                    except (ValueError, TypeError):
                        print(f"⚠️ Строка {i + 1}: некорректная оценка '{score}'")
                        score = None

                # Формируем запись для базы данных
                transcript_record = {
                    'iin': iin,
                    'subject_name_kz': subject_kz,
                    'subject_name_ru': subject_ru,
                    'subject_name_en': subject_en,
                    'score': score,
                    'university_id': university_id
                }

                # Проверяем наличие дубликата в текущей партии
                duplicate_in_batch = any(
                    t['iin'] == iin and t['subject_name_en'] == subject_en
                    for t in transcripts_data
                )

                if duplicate_in_batch:
                    print(f"⚠️ Строка {i + 1}: дубликат в текущей партии - ИИН {iin}, предмет '{subject_en}'")
                    skipped_count += 1
                    continue

                # Проверяем наличие дубликата в базе данных
                cursor.execute(
                    "SELECT id FROM transcripts WHERE iin = %s AND subject_name_en = %s AND university_id = %s",
                    (iin, subject_en, university_id)
                )
                existing_record = cursor.fetchone()

                if existing_record:
                    print(f"⚠️ Строка {i + 1}: дубликат в базе данных - ИИН {iin}, предмет '{subject_en}'")
                    skipped_count += 1
                    continue

                # Добавляем запись в список для вставки
                transcripts_data.append(transcript_record)

            except Exception as e:
                print(f"❌ Ошибка обработки строки {i + 1}: {e}")
                error_count += 1
                continue

        # Массовая вставка данных в базу данных
        if transcripts_data:
            try:
                insert_query = """
                               INSERT INTO transcripts (iin, subject_name_kz, subject_name_ru, subject_name_en, score,
                                                        university_id)
                               VALUES %s
                               ON CONFLICT
                                   (iin, subject_name_en, university_id)
                               DO NOTHING \
                               """

                # Подготавливаем данные для вставки
                data_values = [
                    (
                        t['iin'],
                        t['subject_name_kz'],
                        t['subject_name_ru'],
                        t['subject_name_en'],
                        t['score'],
                        t['university_id']
                    )
                    for t in transcripts_data
                ]

                # Выполняем массовую вставку
                execute_values(cursor, insert_query, data_values)
                inserted_count = cursor.rowcount
                connection.commit()

                print(f"✅ Успешно вставлено записей: {inserted_count}")

            except Exception as e:
                connection.rollback()
                print(f"❌ Ошибка при вставке данных в базу: {e}")
                return {"error": f"Database insertion error: {str(e)}"}

        # Закрываем соединение
        cursor.close()
        connection.close()

        # Создаем JSON файл с результатами
        createFolderIfNotExists(f"storage/jsons/{university_id}/transcripts")

        result_data = {
            "university_id": university_id,
            "file_name": os.path.basename(file.filename),
            "processed_at": datetime.now().isoformat(),
            "statistics": {
                "total_rows": len(iins),
                "inserted": inserted_count,
                "skipped_duplicates": skipped_count,
                "errors": error_count,
                "success_rate": f"{(inserted_count / len(iins) * 100):.1f}%" if len(iins) > 0 else "0%"
            },
            "sample_data": transcripts_data[:5] if transcripts_data else []  # Первые 5 записей для примера
        }

        # Сохраняем результат в JSON файл
        json_filename = f"storage/jsons/{university_id}/transcripts/{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(result_data, f, ensure_ascii=False, indent=2)

        # Возвращаем результат
        return {
            "success": True,
            "message": f"Обработка завершена. Вставлено: {inserted_count}, Пропущено: {skipped_count}, Ошибок: {error_count}",
            "data": result_data,
            "json_file": json_filename
        }

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return {"error": str(e)}


def clean_value(value):
    """Очистка значения от лишних пробелов и преобразование в строку"""
    if value is None:
        return ""

    if isinstance(value, (int, float)):
        # Для чисел убираем лишние нули после запятой
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    # Для строк
    value_str = str(value).strip()

    # Убираем лишние пробелы и переносы строк
    value_str = re.sub(r'\s+', ' ', value_str)

    return value_str


def clean_iin(iin_value):
    """Очистка ИИН от лишних символов"""
    if iin_value is None:
        return ""

    # Преобразуем в строку и удаляем все нецифровые символы
    iin_str = str(iin_value)
    iin_clean = re.sub(r'\D', '', iin_str)

    return iin_clean


def clean_score(score_value):
    """Очистка и преобразование оценки"""
    if score_value is None:
        return None

    try:
        # Преобразуем в строку и очищаем
        score_str = str(score_value).strip()

        # Удаляем все нецифровые символы
        score_clean = re.sub(r'[^\d.]', '', score_str)

        if not score_clean:
            return None

        # Преобразуем в число
        score_float = float(score_clean)

        # Округляем до целого
        return int(round(score_float))

    except (ValueError, TypeError):
        return None


@app.route("/transcript/<iin>", methods=["GET"])
def get_transcripts_by_iin(iin, university_id=None):
    """Получение транскриптов по ИИН"""
    connection, cursor = connectDatabase()
    if connection is None or cursor is None:
        return {"error": "Error connecting to the database."}

    try:
        if university_id:
            cursor.execute(
                """
                SELECT id, iin, subject_name_kz, subject_name_ru, subject_name_en, score, created_at
                FROM transcripts
                WHERE iin = %s
                  AND university_id = %s
                ORDER BY subject_name_en
                """,
                (iin, university_id)
            )
        else:
            cursor.execute(
                """
                SELECT id,
                       iin,
                       subject_name_kz,
                       subject_name_ru,
                       subject_name_en,
                       score,
                       created_at,
                       university_id
                FROM transcripts
                WHERE iin = %s
                ORDER BY subject_name_en
                """,
                (iin,)
            )

        transcripts = cursor.fetchall()

        result = []
        for transcript in transcripts:
            result.append({
                "id": transcript[0],
                "iin": transcript[1],
                "subject_name_kz": transcript[2],
                "subject_name_ru": transcript[3],
                "subject_name_en": transcript[4],
                "score": transcript[5],
                "created_at": transcript[6].isoformat() if transcript[6] else None,
                "university_id": transcript[7] if len(transcript) > 7 else university_id
            })

        return result

    except Exception as e:
        print(f"Error fetching transcripts: {e}")
        return {"error": str(e)}
    finally:
        cursor.close()
        connection.close()


# @app.route("/")
# def home():
#     return main()


@app.route("/data/update", methods=["POST"])
def update_diploma():
    if request.method == "POST":
        connection, cursor = connectDatabase()

        if connection is None or cursor is None:
            return {"error": "Error connecting to the database."}

        try:
            # Assuming request.data is a list of dictionaries
            for data in request.json:
                metadata = {}
                if "attributes" not in data or len(data["attributes"]) == 0:
                    return {"error": "attributes are required, for: " + data["name"]}, 400
                for i in data["attributes"]:
                    metadata[i["name"]] = None if i["value"] == "NONE" else i["value"]

                name_en = metadata["name_en"].strip()
                counter = data["counter"]
                shorthash = generate_short_hash(name_en + str(counter))
                print("update/ ", name_en, counter, shorthash)
                # Check if the record exists in the database
                cursor.execute("SELECT * FROM upload_diplomas WHERE hash_id = %s", (shorthash,))
                existing_record = cursor.fetchone()

                if existing_record:
                    # If the record exists, update it
                    existing_data = existing_record[2]  # Assuming 'value' is the second column

                    if existing_data == data:
                        pass
                        # print(f"Diploma for {name_en} is the same; no update needed.")
                    else:
                        cursor.execute(
                            "UPDATE upload_diplomas SET value = %s WHERE hash_id = %s",
                            (json.dumps(data), shorthash)
                        )
                        connection.commit()
                        generateDiplomaImage(metadata, counter, 1)
                        print(f"Diploma for {name_en} updated successfully.")
                else:
                    # If the record doesn't exist, insert a new one
                    cursor.execute(
                        "INSERT INTO upload_diplomas (value, university_id, hash_id) VALUES (%s, %s, %s)",
                        (json.dumps(data), None, shorthash)
                    )
                    connection.commit()
                    print(f"Diploma for {name_en} inserted successfully.")

        except psycopg2.Error as e:
            print("Error updating data in the database:", e)
        finally:
            cursor.close()
            connection.close()
        return 'Updated'
    return None


@app.route("/get-file/<path:file_path>")
def get_image(file_path):
    # Specify the directory where your diploma images are stored
    image_directory = "./storage"

    # Create the full path to the requested image
    file_path = os.path.join(image_directory, f"{file_path}")
    # Check if the image file exists
    if os.path.isfile(file_path):
        # Return the image file
        return send_file(file_path)
    else:
        # Return an error message or a default image if the requested image doesn't exist
        return "File not found", 404


@app.route("/generation_status/<university_id>")
def get_status(university_id):
    connection, cursor = connectDatabase()
    cursor.execute(
        "SELECT university_id, hash, progress, max_progress FROM diploma_generations WHERE university_id = %s and finished_at is null",
        (int(university_id),))
    existing_record = cursor.fetchone()
    if existing_record:
        # If the record exists, return link to future archive
        university_id = existing_record[0]
        generation_hash = existing_record[1]
        progress = existing_record[2]
        max_progress = existing_record[3]
        return {
            "university_id": university_id,
            "generation_hash": generation_hash,
            "progress": progress,
            "max_progress": max_progress
        }
    else:
        return {"error": "No ongoing generation"}, 404


@app.route("/get-sample", methods=["GET"])
def get_sample_file():
    file_path = "data_bachelor_sample.xlsx"
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404


excluded_paths = ['storage', 'json', 'diploma_satpaev.py', 'websocket.py']


def should_reload(filename):
    # Check if the file is in an excluded path
    for excluded_path in excluded_paths:
        print(excluded_path)
        if filename.startswith(excluded_path) or filename.endswith(excluded_path):
            return False
    return True


if __name__ == "__main__":
    app.run(debug=True, extra_files=should_reload)
