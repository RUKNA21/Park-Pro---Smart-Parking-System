import cv2
import os
from openpyxl import Workbook
import pytesseract
from PIL import Image
import numpy as np
from datetime import datetime


current_datetime = datetime.now()

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
harcascade = "model\haarcascade_russian_plate_number.xml"


def number_plate_detection(img):

    def clean2_plate(plate):
        gray_img = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    
        _, thresh = cv2.threshold(gray_img, 110, 255, cv2.THRESH_BINARY)
        if cv2.waitKey(0) & 0xff == ord('q'):
            pass
        num_contours,hierarchy = cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
        if num_contours:
            contour_area = [cv2.contourArea(c) for c in num_contours]
            max_cntr_index = np.argmax(contour_area)
    
            max_cnt = num_contours[max_cntr_index]
            max_cntArea = contour_area[max_cntr_index]
            x,y,w,h = cv2.boundingRect(max_cnt)
    
            if not ratioCheck(max_cntArea,w,h):
                return plate,None
    
            final_img = thresh[y:y+h, x:x+w]
            return final_img,[x,y,w,h]
    
        else:
            return plate,None
    
    def ratioCheck(area, width, height):
        ratio = float(width) / float(height)
        if ratio < 1:
            ratio = 1 / ratio
        if (area < 1063.62 or area > 73862.5) or (ratio < 3 or ratio > 6):
            return False
        return True
    
    def isMaxWhite(plate):
        avg = np.mean(plate)
        if(avg>=115):
            return True
        else:
            return False
    
    def ratio_and_rotation(rect):
        (x, y), (width, height), rect_angle = rect
    
        if(width>height):
            angle = -rect_angle
        else:
            angle = 90 + rect_angle
    
        if angle>15:
            return False
    
        if height == 0 or width == 0:
            return False
    
        area = height*width
        if not ratioCheck(area,width,height):
            return False
        else:
            return True
    
    
    img2 = cv2.GaussianBlur(img, (5,5), 0)
    img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    img2 = cv2.Sobel(img2,cv2.CV_8U,1,0,ksize=3)	
    _,img2 = cv2.threshold(img2,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    
    element = cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=(17, 3))
    morph_img_threshold = img2.copy()
    cv2.morphologyEx(src=img2, op=cv2.MORPH_CLOSE, kernel=element, dst=morph_img_threshold)
    num_contours, hierarchy= cv2.findContours(morph_img_threshold,mode=cv2.RETR_EXTERNAL,method=cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(img2, num_contours, -1, (0,255,0), 1)
    
    
    for i,cnt in enumerate(num_contours):
        min_rect = cv2.minAreaRect(cnt)
        if ratio_and_rotation(min_rect):
            x,y,w,h = cv2.boundingRect(cnt)
            plate_img = img[y:y+h,x:x+w]
            if(isMaxWhite(plate_img)):
                clean_plate, rect = clean2_plate(plate_img)
                if rect:
                    fg=0
                    x1,y1,w1,h1 = rect
                    x,y,w,h = x+x1,y+y1,w1,h1
                    plate_im = Image.fromarray(clean_plate)
                    text = pytesseract.image_to_string(plate_im, lang='eng')
                    return text



def notebook_data():

    folder_path = 'plates'
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'OCR Text'

    sheet['A1'] = 'Authorized Text'
    sheet['B1'] = 'Entry Time'
    sheet['C1'] = 'Unauthorized Text'
    sheet['D1'] = 'Entry Time'

    authorized_row = 2
    unauthorized_row = 2

    with open('myData.text') as f:
        myDataList=f.read().splitlines()

    # print("My data List:")
    # for text in myDataList:
    #     print(text)
    

    for filename in os.listdir(folder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            image_path = os.path.join(folder_path, filename)
            temp_image = Image.open(image_path)
            img_np = np.array(temp_image)
            text = number_plate_detection(img_np)
            if text is not None:
                text = text.strip()
            print(text)

            vehicle_time = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

            if text in myDataList:
                myOutput = 'Authorised'
                sheet[f'A{authorized_row}'] = text
                sheet[f'B{authorized_row}'] = vehicle_time
                authorized_row += 1
                print(myOutput, vehicle_time)
            else:
                myOutput = 'Un-Authorised'
                sheet[f'C{unauthorized_row}'] = text
                sheet[f'D{authorized_row}'] = vehicle_time
                unauthorized_row += 1
                print(myOutput, vehicle_time)

    excel_file_path = 'output.xlsx'
    workbook.save(excel_file_path)