import Image as pil
import time
from SimpleCV import Image, Display


img = pil.open("morp/mdj.jpg")
time.sleep(3)
cubic = img.resize((246,110),pil.BICUBIC)
img.save("morp/mdj-2.jpg")


