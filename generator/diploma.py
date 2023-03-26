import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
#import os
from config import *

data = pd.read_excel(excel_file)
template = Image.open(diploma_template)
font = ImageFont.truetype('arial', size=45)
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
    draw.text((850, 600), name, font=font, fill='black')
    draw.text((580, 830), degree, font=font, fill='black')

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