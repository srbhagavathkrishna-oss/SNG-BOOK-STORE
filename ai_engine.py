import easyocr
import cv2

reader = easyocr.Reader(['en'])

def extract_text(image_path):

    results = reader.readtext(image_path)

    text = ""

    for result in results:

        text += result[1] + " "

    return text.strip()