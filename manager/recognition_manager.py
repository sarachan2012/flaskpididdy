from PIL import Image
from PIL import ImageChops
import math, operator, requests
from StringIO import StringIO

def compare_image_exact(image1, image2):
    # im1 = Image.open("C:/Users/SARA/Desktop/sample/sample5.jpg")
    # im2 = Image.open("C:/Users/SARA/Desktop/sample/sample5.jpg")
    im1 = Image.open(StringIO(requests.get(image1).content))
    im2 = Image.open(StringIO(requests.get(image2).content))
    return ImageChops.difference(im2, im1).getbbox() is None

def compare_image_rms(image1, image2):
    # im1 = Image.open("C:/Users/SARA/Desktop/sample/sample5.jpg")
    # im2 = Image.open("C:/Users/SARA/Desktop/sample/sample5.jpg")
    im1 = Image.open(StringIO(requests.get(image1).content))
    im2 = Image.open(StringIO(requests.get(image2).content))
    black_im1 = im1.convert('L')
    black_im2 = im2.convert('L')
    # print 'image 1: ' + image1
    # print 'image 2: ' + image2
    # diff = ImageChops.difference(im1, im2)
    diff = ImageChops.difference(black_im1, black_im2)
    h = diff.histogram()
    sq = (value*((idx%256)**2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares/float(im1.size[0] * im1.size[1]))
    nearest_rms = int(math.ceil(rms))
    return nearest_rms

def get_images_exact_similarity(image1, image2):
    diff = compare_image_exact(image1, image2)
    return 100 - int(math.ceil(diff))

def get_images_rms_similarity(image1, image2):
    diff = compare_image_rms(image1, image2)
    return 100 - int(math.ceil(diff))