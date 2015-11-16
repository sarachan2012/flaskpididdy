import pytesseract,requests
from PIL import Image
from PIL import ImageFilter
from StringIO import StringIO

def process_image(url):
    image = _get_image(url)
    image.filter(ImageFilter.SHARPEN)
    return pytesseract.image_to_string(image).encode('utf-8')

def _get_image(url):
    return Image.open(StringIO(requests.get(url).content))