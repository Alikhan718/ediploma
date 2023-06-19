import json
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops
import qrcode
import openpyxl
import textwrap

# Load the Excel file
workbook = openpyxl.load_workbook('generator\diplo\data.xlsx')
sheet = workbook.active
colors = ['red.png', 'blue.png', 'green.png', 'black.png', 'custom.png']

# Set the fonts/ #Need to download them and make a way to them
font1 = ImageFont.truetype('generator\diplo\miamanueva.ttf', size=30)
font2 = ImageFont.truetype('segoeuib', size=25)
font3 = ImageFont.truetype('segoeuib', size=15)
font4 = ImageFont.truetype('segoeuib', size=23)

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

# Iterate through rows and columns starting from row 3
for row in sheet.iter_rows(min_row=3, values_only=True):
    # numbers
    numbers.append(row[2])
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

for name in colors:
    # Load template
    template = Image.open(f'generator\\diplo\\color_temp\\{name}')
    name = name.replace('.png', '')
    # Gain all values separately
    for i in range(len(names_kaz)):
        number = str(numbers[i])
        name_kz = str(names_kaz[i])
        name_ru = str(names_rus[i])
        name_en = str(names_eng[i])
        protocol_kz = str(protocols_kaz[i])
        protocol_ru = str(protocols_rus[i])
        protocol_en = str(protocols_eng[i])
        degree_kz = str(degrees_kaz[i])
        degree_ru = str(degrees_rus[i])
        degree_en = str(degrees_eng[i])
        qualification_kz = f'''{str(qualifications_kaz[i]).upper()}
        БАКАЛАВР ДӘРЕЖЕСІ БЕРІЛДІ'''
        qualification_ru = f"ПРИСУЖДЕНА СТЕПЕНЬ БАКАЛАВРА\n{str(qualifications_rus[i]).upper()}"
        qualification_en = f"THE DEGREE OF BACHELOR\n{str(qualifications_eng[i]).upper()}"
        distinction_kz = str(with_distinctions_kaz[i]).upper()
        distinction_ru = str(with_distinctions_rus[i]).upper()
        distinction_en = str(with_distinctions_eng[i]).upper()

        # Create a copy of the diploma template.
        diploma = template.copy().convert('RGB')
        # Create a draw object for the diploma.
        draw = ImageDraw.Draw(diploma)
        # Make for file name
        name_file = f"{name_en.replace(' ', '_')}_{number}"

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

        # Draw the three parts (optional)
        # draw.line([(part_width, 0), (part_width, canvas_height)], fill='#FFD700', width=2)
        # draw.line([(part_width * 2, 0), (part_width * 2, canvas_height)], fill='#FFD700', width=2)

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
            draw.text((text_x, name_y_kz), line, fill='white', font=font1)
            name_y_kz += name_height_kz + line_spacing

        name_width_ru, name_height_ru = draw.textsize('\n'.join(name_ru_lines), font=font1)
        name_x_ru = part2_x - name_width_ru // 2
        name_y_ru = part2_y - (name_height_ru * len(name_ru_lines) + line_spacing * (len(name_ru_lines) - 1)) // 2
        for line in name_ru_lines:
            text_width, text_height = draw.textsize(line, font=font1)
            text_x = name_x_ru + (name_width_ru - text_width) // 2  # Center-align the text
            draw.text((text_x, name_y_ru), line, fill='white', font=font1)
            name_y_ru += name_height_ru + line_spacing

        name_width_en, name_height_en = draw.textsize('\n'.join(name_en_lines), font=font1)
        name_x_en = part3_x - name_width_en // 2
        name_y_en = part3_y - (name_height_en * len(name_en_lines) + line_spacing * (len(name_en_lines) - 1)) // 2
        for line in name_en_lines:
            text_width, text_height = draw.textsize(line, font=font1)
            text_x = name_x_en + (name_width_en - text_width) // 2  # Center-align the text
            draw.text((text_x, name_y_en), line, fill='white', font=font1)
            name_y_en += name_height_en + line_spacing

        # Add with distinction
        if distinction_ru != "":
            # Calculate the center coordinates for each part
            part1_y = canvas_height * 8.5 // 14
            part2_y = canvas_height * 8.5 // 14
            part3_y = canvas_height * 8.5 // 14

            # Draw the three parts (optional)
            # draw.line([(part_width, 0), (part_width, canvas_height)], fill='#FFD700', width=2)
            # draw.line([(part_width * 2, 0), (part_width * 2, canvas_height)], fill='#FFD700', width=2)

            # Wrap the text if it exceeds the line width
            distinction_kz_lines = textwrap.wrap(distinction_kz, width=20)
            distinction_ru_lines = textwrap.wrap(distinction_ru, width=20)
            distinction_en_lines = textwrap.wrap(distinction_en, width=20)

            # Draw the names in the middle of each part
            distinction_width_kz, distinction_height_kz = draw.textsize('\n'.join(distinction_kz_lines), font=font2)
            distinction_x_kz = part1_x - distinction_width_kz // 2
            distinction_y_kz = part1_y - distinction_height_kz // 2
            for line in distinction_kz_lines:
                text_width, text_height = draw.textsize(line, font=font2)
                text_x = distinction_x_kz + (distinction_width_kz - text_width) // 2  # Center-align the text
                draw.text((text_x, distinction_y_kz), line, fill='white', font=font2)
                distinction_y_kz += distinction_height_kz

            distinction_width_ru, distinction_height_ru = draw.textsize('\n'.join(distinction_ru_lines), font=font2)
            distinction_x_ru = part2_x - distinction_width_ru // 2
            distinction_y_ru = part2_y - distinction_height_ru // 2
            for line in distinction_ru_lines:
                text_width, text_height = draw.textsize(line, font=font2)
                text_x = distinction_x_ru + (distinction_width_ru - text_width) // 2  # Center-align the text
                draw.text((text_x, distinction_y_ru), line, fill='white', font=font2)
                distinction_y_ru += distinction_height_ru

            distinction_width_en, distinction_height_en = draw.textsize('\n'.join(distinction_en_lines), font=font2)
            distinction_x_en = part3_x - distinction_width_en // 2
            distinction_y_en = part3_y - distinction_height_en // 2
            for line in distinction_en_lines:
                text_width, text_height = draw.textsize(line, font=font2)
                text_x = distinction_x_en + (distinction_width_en - text_width) // 2  # Center-align the text
                draw.text((text_x, distinction_y_en), line, fill='white', font=font2)
                distinction_y_en += distinction_height_en

        # Qualifications
        # Calculate the center coordinates for each part
        part1_y = canvas_height // 2
        part2_y = canvas_height // 2
        part3_y = canvas_height // 2

        # Draw the three parts (optional)
        # draw.line([(part_width, 0), (part_width, canvas_height)], fill='#FFD700', width=2)
        # draw.line([(part_width * 2, 0), (part_width * 2, canvas_height)], fill='#FFD700', width=2)

        # Wrap the text if it exceeds the line width
        qualification_kz_lines = textwrap.wrap(qualification_kz, width=35)
        qualification_ru_lines = textwrap.wrap(qualification_ru, width=35)
        qualification_en_lines = textwrap.wrap(qualification_en, width=35)

        # Draw the names in the middle of each part
        qualification_width_kz, qualification_height_kz = draw.textsize('\n'.join(qualification_kz_lines), font=font2)
        qualification_x_kz = part1_x - qualification_width_kz // 2
        qualification_y_kz = part1_y - qualification_height_kz // 2
        for line in qualification_kz_lines:
            text_width, text_height = draw.textsize(line, font=font2)
            text_x = qualification_x_kz + (qualification_width_kz - text_width) // 2  # Center-align the text
            draw.text((text_x, qualification_y_kz), line, fill='white', font=font2)
            qualification_y_kz += text_height

        qualification_width_ru, qualification_height_ru = draw.textsize('\n'.join(qualification_ru_lines), font=font2)
        qualification_x_ru = part2_x - qualification_width_ru // 2
        qualification_y_ru = part2_y - qualification_height_ru // 2
        for line in qualification_ru_lines:
            text_width, text_height = draw.textsize(line, font=font2)
            text_x = qualification_x_ru + (qualification_width_ru - text_width) // 2  # Center-align the text
            draw.text((text_x, qualification_y_ru), line, fill='white', font=font2)
            qualification_y_ru += text_height

        qualification_width_en, qualification_height_en = draw.textsize('\n'.join(qualification_en_lines), font=font2)
        qualification_x_en = part3_x - qualification_width_en // 2
        qualification_y_en = part3_y - qualification_height_en // 2
        for line in qualification_en_lines:
            text_width, text_height = draw.textsize(line, font=font2)
            text_x = qualification_x_en + (qualification_width_en - text_width) // 2  # Center-align the text
            draw.text((text_x, qualification_y_en), line, fill='white', font=font2)
            qualification_y_en += text_height

        # Protocols
        # Calculate the center coordinates for each part
        part1_y = canvas_height // 3.8
        part2_y = canvas_height // 3.8
        part3_y = canvas_height // 3.8

        # Draw the three parts (optional)
        # draw.line([(part_width, 0), (part_width, canvas_height)], fill='#FFD700', width=2)
        # draw.line([(part_width * 2, 0), (part_width * 2, canvas_height)], fill='#FFD700', width=2)

        # Wrap the text if it exceeds the line width
        protocol_kz_lines = textwrap.wrap(protocol_kz, width=35)
        protocol_ru_lines = textwrap.wrap(protocol_ru, width=35)
        protocol_en_lines = textwrap.wrap(protocol_en, width=35)

        # Draw the names in the middle of each part
        protocol_width_kz, protocol_height_kz = draw.textsize('\n'.join(protocol_kz_lines), font=font4)
        protocol_x_kz = part1_x - protocol_width_kz // 2
        protocol_y_kz = part1_y - protocol_height_kz // 2
        for line in protocol_kz_lines:
            text_width, text_height = draw.textsize(line, font=font4)
            text_x = protocol_x_kz + (protocol_width_kz - text_width) // 2  # Center-align the text
            draw.text((text_x, protocol_y_kz), line, fill='white', font=font4)
            protocol_y_kz += protocol_height_kz + 2  # Add a small fixed spacing between lines

        protocol_width_ru, protocol_height_ru = draw.textsize('\n'.join(protocol_ru_lines), font=font4)
        protocol_x_ru = part2_x - protocol_width_ru // 2
        protocol_y_ru = part2_y - protocol_height_ru // 2
        for line in protocol_ru_lines:
            text_width, text_height = draw.textsize(line, font=font4)
            text_x = protocol_x_ru + (protocol_width_ru - text_width) // 2  # Center-align the text
            draw.text((text_x, protocol_y_ru), line, fill='white', font=font4)
            protocol_y_ru += protocol_height_ru + 2  # Add a small fixed spacing between lines

        protocol_width_en, protocol_height_en = draw.textsize('\n'.join(protocol_en_lines), font=font4)
        protocol_x_en = part3_x - protocol_width_en // 2
        protocol_y_en = part3_y - protocol_height_en // 2
        for line in protocol_en_lines:
            text_width, text_height = draw.textsize(line, font=font4)
            text_x = protocol_x_en + (protocol_width_en - text_width) // 2  # Center-align the text
            draw.text((text_x, protocol_y_en), line, fill='white', font=font4)
            protocol_y_en += protocol_height_en + 2  # Add a small fixed spacing between lines

        # Study type
        # Calculate the center coordinates for each part
        part1_y = canvas_height * 2 // 3
        part2_y = canvas_height * 2 // 3
        part3_y = canvas_height * 2 // 3

        # Draw the three parts (optional)
        # draw.line([(part_width, 0), (part_width, canvas_height)], fill='#FFD700', width=2)
        # draw.line([(part_width * 2, 0), (part_width * 2, canvas_height)], fill='#FFD700', width=2)

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
            draw.text((text_x, study_y_kz), line, fill='white', font=font3)
            study_y_kz += text_height

        study_width_ru, study_height_ru = draw.textsize('\n'.join(study_ru_lines), font=font3)
        study_x_ru = part2_x - study_width_ru // 2
        study_y_ru = part2_y - (study_height_ru * len(study_ru_lines)) // 2
        for line in study_ru_lines:
            text_width, text_height = draw.textsize(line, font=font3)
            text_x = study_x_ru + (study_width_ru - text_width) // 2  # Center-align the text
            draw.text((text_x, study_y_ru), line, fill='white', font=font3)
            study_y_ru += text_height

        study_width_en, study_height_en = draw.textsize('\n'.join(study_en_lines), font=font3)
        study_x_en = part3_x - study_width_en // 2
        study_y_en = part3_y - (study_height_en * len(study_en_lines)) // 2
        for line in study_en_lines:
            text_width, text_height = draw.textsize(line, font=font3)
            text_x = study_x_en + (study_width_en - text_width) // 2  # Center-align the text
            draw.text((text_x, study_y_en), line, fill='white', font=font3)
            study_y_en += text_height

        # Add QR code
        qr_size = int(diploma.width * (1.6 / 23))

        # Create a QRCode object with a box size of 1
        qr = qrcode.QRCode(box_size=1)
        qr.add_data(f'ediplomas/kbtu/{name_en}')
        qr.make(fit=True)

        # Create the QR code image with black fill and white background
        img_qr = qr.make_image(fill_color="black", back_color="white").resize((qr_size, qr_size),
                                                                              Image.ANTIALIAS).convert("RGBA")

        # Create mask with rounded corners
        mask = Image.new("L", (qr_size, qr_size), 0)
        draw = ImageDraw.Draw(mask)
        radius = int(qr_size * 0.2)
        rectangle = [(0, 0), (qr_size, qr_size)]
        draw.rounded_rectangle(rectangle, radius=radius, fill=255)

        # Apply mask
        img_qr.putalpha(mask)

        # Calculate the position for the QR code on the diploma
        margin = int(diploma.width * (0.5 / 23))
        qr_pos = (diploma.width - qr_size - margin, diploma.height - qr_size - margin)

        # Paste the QR code onto the diploma image
        diploma.paste(img_qr, qr_pos, img_qr)

        # Save the diploma as a new image file.
        diploma.save(f'generator/diplo/Diplomas/{name_file}_{name}.jpeg', 'JPEG')

        # CREATION OF JSON FILES
        # Create a dictionary with the row data
        row_dict = {
            'name': name_en,
            'image': f'',
            'description': f'KBTU 2023 Graduate {name_file}',
            'name_kz': name_kz,
            'name_ru': name_ru,
            'protocol_kz': protocol_kz,
            'protocol_ru': protocol_ru,
            'protocol_en': protocol_en,
            'degree_kz': degree_kz,
            'degree_ru': degree_ru,
            'degree_en': degree_en,
            'qualification_kz': qualification_kz,
            'qualification_ru': qualification_ru,
            'qualification_en': qualification_en,
            'distinction_kz': distinction_kz,
            'distinction_ru': distinction_ru,
            'distinction_en': distinction_en
        }

        # Convert the dictionary into a JSON string
        row_json = json.dumps(row_dict)

        # Create a new file with the JSON data
        filename = f'generator/diplo/json/{name_file}.json'
        with open(filename, 'w') as f:
            f.write(row_json)
