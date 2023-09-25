# run command # nohup python3 -m flask --app diploma_final.py run &

import os
import re
import textwrap

import json
import openpyxl
import psycopg2
import qrcode
import hashlib
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, send_file, request, redirect
import warnings

# Suppress DeprecationWarning for ANTIALIAS in Pillow
warnings.filterwarnings("ignore", category=DeprecationWarning)


def generate_short_hash(text):
    # Create a SHA-256 hash object
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


def parseData(file, id):
    # Load the Excel file
    connection, cursor = connectDatabase()
    if connection is None or cursor is None:
        return {"error": "Error connecting to the database."}
    else:
        createTableIfNotExists(cursor)

    workbook = openpyxl.load_workbook(file)

    sheet = workbook.active

    # Load template
    template = Image.open('./diploma_template.png')

    # Set the fonts/ #Need to download them and make a way to them
    font1 = ImageFont.truetype('./miamanueva.ttf', size=30)
    font2 = ImageFont.truetype('./Alice-Regular.ttf', size=23)
    font3 = ImageFont.truetype('./Alice-Regular.ttf', size=15)
    font4 = ImageFont.truetype('./Alice-Regular.ttf', size=22)
    font5 = ImageFont.truetype('./Alice-Regular.ttf', size=22)  ##2a4a62
    imagesDiploma = {}

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

    fullMetadata = "["
    # Iterate through rows and columns starting from row 3
    for row in sheet.iter_rows(min_row=3, values_only=True):
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

    # Gain all values separately
    counter = 1
    for i in range(len(names_kaz)):
        number = str(numbers[i]).strip()
        name_kz = str(names_kaz[i]).strip()
        name_ru = str(names_rus[i]).strip()
        name_en = str(names_eng[i]).strip()
        protocol_kz = str(protocols_kaz[i]).strip().replace("№", "#")
        protocol_ru = str(protocols_rus[i]).strip().replace("№", "#")
        protocol_en = str(protocols_eng[i]).strip().replace("№", "#")
        degree_kz = str(degrees_kaz[i]).upper().strip()
        degree_ru = str(degrees_rus[i]).upper().strip()
        degree_en = str(degrees_eng[i]).upper().strip()
        qualification_kz = str(qualifications_kaz[i]).upper().strip()
        qualification_ru = str(qualifications_rus[i]).upper().strip()
        qualification_en = str(qualifications_eng[i]).upper().strip()
        distinction_kz = str(with_distinctions_kaz[i]).upper().strip()
        distinction_ru = str(with_distinctions_rus[i]).upper().strip()
        distinction_en = str(with_distinctions_eng[i]).upper().strip()

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

        # Save the diploma as a new image file.
        diploma.save(f'./Diplomas/{name_file}.jpeg', 'JPEG')
        metadata = {
            "description": f"KBTU 2023 Graduate {name_file}",
            "image": f"http://generator.ediploma.kz/get-image/{name_file}.jpeg",
            "name": name_en,
            "counter": counter,
            "attributes": [
                {
                    "name": "name_kz",
                    "value": name_kz
                },
                {
                    "name": "name_ru",
                    "value": name_ru
                },
                {
                    "name": "name_en",
                    "value": name_en
                },
                {
                    "name": "protocol_en",
                    "value": protocol_en
                },
                {
                    "name": "degree_ru",
                    "value": degree_ru
                },
                {
                    "name": "degree_en",
                    "value": degree_en
                },
                {
                    "name": "qualification_kz",
                    "value": qualification_kz
                },
                {
                    "name": "qualification_ru",
                    "value": qualification_ru
                },
                {
                    "name": "qualification_en",
                    "value": qualification_en
                }
            ]
        }
        imagesDiploma[name_en] = f"http://generator.ediploma.kz/get-image/{name_file}.jpeg"

        # Convert the dictionary into a JSON string
        metadata_json = json.dumps(metadata)
        fullMetadata += metadata_json + ("," if i < len(names_kaz) - 1 else "")
        # Create a new file with the JSON data
        filename = f"./Diplomas/json/{counter}.json"
        counter += 1
        with open(filename, "w", encoding="utf-8") as f:
            f.write(metadata_json)
        # break
        # Insert metadata into the database
        try:
            shorthash = generate_short_hash(name_en + str(counter - 1))
            # Check if the record exists in the database
            cursor.execute("SELECT id FROM upload_diplomas WHERE hash_id = %s AND deleted_at IS NULL", (shorthash,))
            existing_record = cursor.fetchone()

            if existing_record:
                # If the record exists, update it
                cursor.execute(
                    "UPDATE upload_diplomas SET value = %s, university_id = %s WHERE hash_id = %s AND deleted_at IS NULL",
                    (metadata_json, id, shorthash)
                )
            else:
                cursor.execute(
                    "INSERT INTO upload_diplomas (value, university_id, hash_id) VALUES (%s, %s, %s)",
                    (metadata_json, id, shorthash)
                )
            connection.commit()
        except psycopg2.Error as e:
            print("Error inserting data into the database:", e)

    fullMetadata += "]"
    with open("fullMetadata.json", "w") as f:
        f.write(fullMetadata)
    image_path = os.path.join('./', "fullMetadata.json")
    # Check if the image file exists
    if os.path.isfile(image_path):
        # Return the image file
        return send_file(image_path)


@app.route('/data/parse', methods=['GET', "POST"])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return {'error': 'File required'}
        if 'university_id' not in request.values:
            return {'error': 'No university ID'}
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return {'error': 'No selected file'}
        return parseData(file, request.form.get('university_id'))
    return 'here'


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
                if "name" in data:
                    name_en = data["name"]
                    counter = data["counter"]
                    shorthash = generate_short_hash(name_en + str(counter))
                    # Check if the record exists in the database
                    cursor.execute("SELECT * FROM upload_diplomas WHERE hash_id = %s", (shorthash,))
                    existing_record = cursor.fetchone()

                    if existing_record:
                        # If the record exists, update it
                        existing_data = existing_record[2]  # Assuming 'value' is the second column

                        if existing_data == data:
                            print(f"Diploma for {name_en} is the same; no update needed.")
                        else:
                            cursor.execute(
                                "UPDATE upload_diplomas SET value = %s WHERE hash_id = %s",
                                (json.dumps(data), shorthash)
                            )
                            connection.commit()
                            print(f"Diploma for {name_en} updated successfully.")
                            regenerate_diploma(name_en, counter)
                    else:
                        # If the record doesn't exist, insert a new one
                        cursor.execute(
                            "INSERT INTO upload_diplomas (value, university_id, hash_id) VALUES (%s, %s, %s)",
                            (json.dumps(data), None, shorthash)
                        )
                        connection.commit()
                        print(f"Diploma for {name_en} inserted successfully.")
                else:
                    print("Missing 'name_en' in data:", data)
        except psycopg2.Error as e:
            print("Error updating data in the database:", e)
        finally:
            cursor.close()
            connection.close()
        return 'Updated'
    return None

def regenerate_diploma(name_en, counter):
    connection, cursor = connectDatabase()

    if connection is None or cursor is None:
        return {"error": "Error connecting to the database."}

    try:
        shorthash = generate_short_hash(name_en + str(counter))
        # Check if the record exists in the database
        cursor.execute("SELECT value FROM upload_diplomas WHERE hash_id = %s", (shorthash,))
        existing_data = cursor.fetchone()

        if existing_data:
            existing_data = json.loads(existing_data[0])
            # You can modify the existing data here if needed
            # For example, if you want to update the name in the diploma:
            existing_data["attributes"][2]["value"] = name_en

            # Re-generate the diploma using the updated data
            regenerated_diploma_response = parseData(None, None, existing_data)

            if "image" in regenerated_diploma_response:
                regenerated_image_path = regenerated_diploma_response["image"]
                # Save the regenerated diploma as a new image file
                regenerated_image = Image.open(regenerated_image_path)

                regenerated_filename = f"./Diplomas/{name_en.replace(' ', '_')}_{counter}_regenerated.jpeg"
                regenerated_image.save(regenerated_filename, 'JPEG')

                # Update the database with the regenerated data
                cursor.execute(
                    "UPDATE upload_diplomas SET value = %s WHERE hash_id = %s",
                    (json.dumps(existing_data), shorthash)
                )
                connection.commit()

                print(f"Diploma for {name_en} regenerated and updated successfully.")
                return {
                    "message": f"Diploma for {name_en} regenerated and updated successfully.",
                    "regenerated_image_path": regenerated_filename
                }
            else:
                print("No image found in the regenerated diploma response.")
                return {"error": "No image found in the regenerated diploma response."}
        else:
            print(f"Diploma for {name_en} with counter {counter} not found in the database.")
            return {"error": f"Diploma for {name_en} with counter {counter} not found in the database."}

    except psycopg2.Error as e:
        print("Error regenerating data in the database:", e)
        return {"error": "Error regenerating data in the database."}
    
    finally:
        cursor.close()
        connection.close()

@app.route("/get-image/<image_name>")
def get_image(image_name):
    # Specify the directory where your diploma images are stored
    image_directory = "./Diplomas"

    # Create the full path to the requested image
    image_path = os.path.join(image_directory, f"{image_name}")
    # Check if the image file exists
    if os.path.isfile(image_path):
        # Return the image file
        return send_file(image_path, mimetype="image/jpeg")
    else:
        # Return an error message or a default image if the requested image doesn't exist
        return "Image not found", 404


@app.route("/get-sample", methods=["GET"])
def get_sample_file():
    file_path = "data_bachelor_sample.xlsx"
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return "File not found", 404


if __name__ == "__main__":
    app.run(debug=True)
