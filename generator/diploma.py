import pandas as pd
from PIL import Image, ImageDraw, ImageFont
#import os

data = pd.read_excel('generator/data.xlsx')
template = Image.open('generator/diploma_template.png')
font = ImageFont.truetype('arial', size=45)
# Create a folder for saving the diploma images
# os.makedirs('Diplomas', exist_ok=True)
for index, row in data.iterrows():
    # Get the student's name and degree information from the Excel data.
    name = row['Name']
    degree = 'Bachelor of ' + row['Degree']

    # Create a copy of the diploma template.
    diploma = template.copy()

    # Create a draw object for the diploma.
    draw = ImageDraw.Draw(diploma)

    # Draw the student's name and degree information on the diploma.
    draw.text((850, 600), name, font=font, fill='black')
    draw.text((580, 830), degree, font=font, fill='black')

    # Save the diploma as a new image file.
    diploma.save(f'generator/Diplomas/{name}_diploma.jpeg')
