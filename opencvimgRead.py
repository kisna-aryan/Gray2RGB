import cv2
import os

path3C = "/media/kisna/nano_ti_data1/DL_git/dataset/annotation_test/val3C/thermal_8_bit/"
try:
    os.mkdir(path3C)
except OSError as error:
    print(error)

path = "/media/kisna/nano_ti_data1/DL_git/dataset/annotation_test/val/thermal_8_bit/"
dir_list = os.listdir(path)

print(dir_list[0])

gray_img = cv2.imread(path + dir_list[0], 0)

red_channel = gray_img.copy()
green_channel = gray_img.copy()
blue_channel = gray_img.copy()
result = cv2.merge([red_channel, green_channel, blue_channel])
cv2.imshow('image', result)
cv2.waitKey(0)

for filename in dir_list:
    gray_img = cv2.imread(path + filename, 0)
    red_channel = gray_img.copy()
    green_channel = gray_img.copy()
    blue_channel = gray_img.copy()
    result = cv2.merge([red_channel, green_channel, blue_channel])
    cv2.imwrite(path3C + filename, result)
    print(filename)

# Displaying the image
cv2.imshow('image', result)
cv2.waitKey(0)
