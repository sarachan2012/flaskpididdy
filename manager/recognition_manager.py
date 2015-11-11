from PIL import Image
from PIL import ImageChops
import math, operator

def compare_image_exact():
    im1 = Image.open("C:/Users/SARA/Desktop/sample/sample5.jpg")
    im2 = Image.open("C:/Users/SARA/Desktop/sample/sample5.jpg")
    return ImageChops.difference(im2, im1).getbbox() is None

def compare_image_rms():
    im1 = Image.open("C:/Users/SARA/Desktop/sample/sample5.jpg")
    im2 = Image.open("C:/Users/SARA/Desktop/sample/sample5.jpg")

    diff = ImageChops.difference(im1, im2)
    h = diff.histogram()
    sq = (value*((idx%256)**2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares/float(im1.size[0] * im1.size[1]))
    nearest_rms = int(math.ceil(rms))
    return nearest_rms

def get_images_similarity(diff):
    return 100 - int(math.ceil(diff))