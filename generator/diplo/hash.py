import qrcode
from PIL import Image, ImageDraw, ImageFont



def generateHash(text, key):
    nHash = ""
    for i in range(len(text)):
        nHash += chr((((ord(text[i]) - 48) + (ord(key[i % len(key)]) - 97)) % 26) + 97)
    return nHash


def decryptHash(hash_text, key):
    nText = ""
    for i in range(len(hash_text)):
        nText += chr(((ord(hash_text[i]) - ord(key[i % len(key)])) % 26) + 48)
    return nText


key = "hashotnursa"


def func(number, ):
    if number <= 9:
        number = "0" + str(number)
    return str(number)



text = "020807551167"
generatedHash = generateHash(text, key)
decryptedHash = str(decryptHash(generatedHash, key))
print(generatedHash)
# Add QR code
qr_size = int(1080 * (1.6 / 23))

qr = qrcode.QRCode(box_size=1)
qr.add_data(f'https://app.ediploma.kz/3' + generatedHash)  # do after we do portal
qr.make(fit=True)

img_qr = qr.make_image(fill_color="black", back_color="white").resize((qr_size, qr_size))
margin = int(1080 * (0.5 / 23))
qr_pos = (1080 - qr_size - margin, 1080 - qr_size - margin)

img_qr.save('some_qr.png', 'png')