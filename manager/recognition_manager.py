from PIL import Image
from PIL import ImageChops
import math, operator

def compareImage():
    im1 = Image.open("C:/Users/SARA/Desktop/sample/sample5.jpg")
    im2 = Image.open("C:/Users/SARA/Desktop/sample/sample5.jpg")
    # diff = ImageChops.difference(im2, im1).getbbox() is None
    diff = ImageChops.difference(im1, im2)
    h = diff.histogram()
    sq = (value*((idx%256)**2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares/float(im1.size[0] * im1.size[1]))
    nearest_rms = int(math.ceil(rms))
    similarity = 100 - nearest_rms
    return similarity