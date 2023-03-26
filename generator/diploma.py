#import os
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
#import config
from config import *

data = pd.read_excel(excel_file)
template = Image.open(diploma_template)
font_name = ImageFont.truetype(font_path, size=font_size)
font_details = ImageFont.truetype(font_path, size=40)

# Create a folder for saving the diploma images
# os.makedirs('Diplomas', exist_ok=True)
for index, row in data.iterrows():
    # Get the student's name and degree information from the Excel data.
    name = row['Name']
    if (bachelor == True):
        degree = 'Bachelor of ' + row['Degree']
    else:
        degree = 'Master of' + row['Degree']

    # Create a copy of the diploma template.
    diploma = template.copy()

    # Create a draw object for the diploma.
    draw = ImageDraw.Draw(diploma)

    # Draw the student's name and degree information on the diploma.
    text_width, text_height = draw.textsize(name, font_name)
    x = (diploma.width - text_width) / 2
    draw.text((x, 550), name, font=font_name, fill=font_color)

    text_width, text_height = draw.textsize(degree, font_details)
    x = (diploma.width - text_width) / 2
    draw.text((x, 850), degree, font=font_details, fill=font_color)

    #Convert image mode to RGB
    if diploma.mode != 'RGB':
        diploma = diploma.convert('RGB')

    #Generate QR Code
    qr = qrcode.QRCode(box_size=8)
    qr.add_data(name)
    qr.make()
    img_qr = qr.make_image()
    pos = (diploma.size[0] - img_qr.size[0], diploma.size[1] - img_qr.size[1])
    diploma.paste(img_qr, pos)

    # Save the diploma as a new image file.
    diploma.save(f'generator/Diplomas/images/{name}_diploma.jpeg')
