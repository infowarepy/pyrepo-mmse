#utils
import cv2
import numpy as np
import math
from collections import defaultdict
from keras.models import load_model
from PIL import Image
import itertools
import matplotlib.pyplot as plt

# model=load_model('DigitRecognitionModel.h5')

# step 1
def preprocess_image(image):
    # image = cv2.imread(image_path)

    if image.ndim == 3:  # Color image with multiple channels
        grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:  # Grayscale image with a single channel
        grayscale = image

    blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)

    _, thresholded = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mask = np.zeros_like(grayscale)
    if len(contours) > 0:
        clock_contour = max(contours, key=cv2.contourArea)
        cv2.drawContours(mask, [clock_contour], 0, 255, thickness=cv2.FILLED)

    masked_image = cv2.bitwise_and(grayscale, grayscale, mask=mask)

    return masked_image



#step2
def evaluate_circle_circularity(image):
    # Step 1: Read the image
    # image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Step 2: Apply image processing techniques
    _, thresholded = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Step 3: Find the circular shape within the image
    circularity_values = []
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        area = cv2.contourArea(contour)
        if perimeter != 0:
          circularity = 4 * np.pi * (area / (perimeter * perimeter))
        else:
          circularity = 0

        circularity_values.append(circularity)

    # Step 4: Measure the circularity of the detected shape
    max_circularity = max(circularity_values) if circularity_values else 0
    return min(1,max_circularity)

def detect_circle(image):

    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, dp=1, minDist=100,
                               param1=50, param2=30, minRadius=0, maxRadius=0)

    if circles is not None:
        # Find the largest circle
        circles = np.uint16(np.around(circles))
        largest_circle = circles[0][0]
        center_x, center_y, radius = largest_circle[0], largest_circle[1], largest_circle[2]

        # Calculating circularity
        circularity_score = evaluate_circle_circularity(image)
        print(circularity_score)
        return (center_x, center_y), radius, circularity_score

    return None


#step 3
# Extract Handwritten Numbers starts 

def padding(image):
    top_padding = 20
    bottom_padding = 20
    left_padding = 30
    right_padding = 30

    new_height = image.shape[0] + top_padding + bottom_padding
    new_width = image.shape[1] + left_padding + right_padding

    padded_image = np.ones((new_height, new_width), dtype=np.uint8) * 255

    padded_image[top_padding:top_padding + image.shape[0], left_padding:left_padding + image.shape[1]] = image
    
    return padded_image

def invert_this(image_file, with_plot=False, gray_scale=False):
    image_src = image_file
    image_i = 255 - image_src
    return image_i

# def pred(image,ch):
#     image=padding(image)
#     image=invert_this(image, with_plot=True, gray_scale=True) 
#     plt.imshow(image)
#     image = cv2.resize(image, (28, 28))
#     image = image.astype('float32') / 255.0
#     image = image.reshape((1, 28, 28))
#     return (model.predict(image))

def extract_handwritten_numbers(img):
  dimensions=img.shape
  _, threshold = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY) 
  contours, hierarchy = cv2.findContours(threshold, cv2.CHAIN_APPROX_NONE, cv2.CHAIN_APPROX_SIMPLE)
  result=[]
  dict={}

  # for i, contour in enumerate(contours):
  #     x, y, w, h = cv2.boundingRect(contour)
  #     area = cv2.contourArea(contour)
      
  #     asp_ratio=float(w)/h
  #     max_h=0.133*dimensions[0]
  #     max_w=0.1066*dimensions[0]
  #     if  h>max_h or w>max_w: 
  #         continue
          
  #     roi = threshold[y:y + h, x:x + w]
  #   #   if i==12:
  #   #       cv2.imwrite('output1.jpg', roi)
      
  #   #   cv2.imwrite('output2.jpg', roi)
  #   #   image=cv2.imread('output2.jpg', cv2.IMREAD_GRAYSCALE)
  #     image = roi.copy()
  #     response=pred(image,0)
  #     score=np.max(response)
  #     cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 1)
  #     score=f'{np.max(response):.10f}'
  #     val=response.argmax(axis=1)[0].__str__()
  #     result.append(val)
      
  #     font = cv2.FONT_HERSHEY_SIMPLEX
  #     fontScale = 0.5 
  #     if i==15:
  #         print(val)
  #     color = (255, 0, 0)
  #     thickness = 1
  #     cv2.putText(img, val, (x, y - 5), font, fontScale, color, thickness)
  #     dict[i]=contour

  return set(result)
# Extract Handwritten Numbers Ends



# step4
def detect_lines_in_circle(image, center):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresholded = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresholded, cv2.CHAIN_APPROX_NONE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        contour = np.squeeze(contour)
        if contour.shape[0] == 2:
            continue
        distances = np.linalg.norm(contour - center, axis=1)
        threshold_distance = image.shape[0]*0.1067
        if np.any(distances <= threshold_distance):
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            l1_a = tuple(approx[0][0])
            l1_b = tuple(approx[1][0])
            l2_a = tuple(approx[-2][0])
            l2_b = tuple(approx[-1][0])
            return [[l1_a,l1_b],[l2_a,l2_b]]
    return None



#step5

def determine_numbers(lines):
    allNums = {}
    if lines is None:
        return allNums
    for line in lines:
        print(line)
        l1_a, l1_b = line
        dx = l1_b[0] - l1_a[0]
        dy = l1_b[1] - l1_a[1]
        slope = dy/dx 
        angle_in_radians = math.atan(slope)
        angle_deg = angle_in_radians * 180 / math.pi
        if angle_deg < 0:
          angle_deg = 180 - abs(angle_deg)
        print(angle_deg)
        numbers = []
        if angle_deg <= 15:
            numbers.extend([3, 9])
        elif angle_deg > 15 and angle_deg <= 45:
            numbers.extend([2, 8])
        elif angle_deg > 45 and angle_deg <= 75:
            numbers.extend([1, 7])
        elif angle_deg > 75 and angle_deg <= 105:
            numbers.extend([12, 6])
        elif angle_deg > 105 and angle_deg <= 135:
            numbers.extend([11, 5])
        elif angle_deg > 135 and angle_deg <= 165:
            numbers.extend([10, 4])
        else:
            numbers.extend([9, 3])
        allNums[tuple(numbers)] = 1
    
    return allNums


#step6
def generate_timings(number_lists):
    number_pairs = list(itertools.product(*number_lists))  # Generating all possible pairs from different lists
    # Generate reverse order pairs
    reversed_pairs = [(pair[1], pair[0]) if len(pair) > 1 else pair for pair in number_pairs]
    # Combine original pairs and reversed pairs
    number_pairs = number_pairs + reversed_pairs
    number_pairs = set(number_pairs)
    timings = []
    for pair in number_pairs:
        try:
            hour = pair[0]
            minute = pair[1] * 5  # Each number represents 5 minutes

            if minute >= 60:  # Adjusting hour and minute if minute exceeds 60
                hour += 1
                minute -= 60

            timings.append((hour, minute))
        except IndexError:
            # lol
            pass

    return timings



def calculate_score(actual_time, predicted_time):
    actual_hours, actual_minutes = map(int, actual_time.split(':'))
    predicted_hours, predicted_minutes = map(int, predicted_time.split(':'))

    # Calculate the absolute difference in hours and minutes
    hours_diff = abs(actual_hours - predicted_hours)
    minutes_diff = abs(actual_minutes - predicted_minutes)

    # Calculate the maximum possible difference in hours and minutes
    max_hours_diff = 12  # Assuming 12-hour format
    max_minutes_diff = 59

    # Calculate the normalized score for hours and minutes
    hours_score = 1 - (hours_diff / max_hours_diff)
    minutes_score = 1 - (minutes_diff / max_minutes_diff)

    # Calculate the overall score as the average of hours and minutes score
    overall_score = (hours_score + minutes_score) / 2

    return overall_score
