#import os
import json
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import qrcode
#import config
from config import *

#def rk():

    # draw = Image.open("W.png")
    # draw.show()
    # x=int(input('are u satisfied?'))

    # if(x==1):
    #     return 'W.png'
    # else:

    #     Image1=Image.open('B.png')
    #     Image2=Image.open('R.png')
    #     Image3=Image.open('G.png')
    #     Image4=Image.open('C.png')

    #     draw.show()
    #     Image1.show()
    #     Image2.show()
    #     Image3.show()
    #     Image4.show()

    #     z=input('choose template')

    #     if(z=='W'):
    #         return 'W.png'
    #     elif(z=='R'):
    #         return 'R.png'
    #     elif(z=='G'):
    #         return 'G.png'
    #     elif(z=='B'):
    #         return 'B.png'
    #     else:
    #         return 'C.png'




data     = pd.read_excel('generator\data.xlsx')

font_name = ImageFont.truetype(font_path, size=font_size)
font_details = ImageFont.truetype(font_path, size=40)

for index, row in data.iterrows():
    ##CREATION OF JPEG IMAGES
    # Get the student's name and degree information from the Excel data.
    name = row['Name']
    if (bachelor == True):
        degree = 'Bachelor of ' + row['Degree']
    else:
        degree = 'Master of' + row['Degree']

    c = row['Color']

    template = Image.open('generator\\'+str(c)+'.png')

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


    ##CREATION OF JSON FILES
    # Create a dictionary with the row data
    row_dict = row.to_dict()

    # Convert the dictionary into a JSON string
    row_json = json.dumps(row_dict)

    # Create a new file with the JSON data
    filename = f'generator/Diplomas/json/{name}.json'
    with open(filename, 'w') as f:
        f.write(row_json)
