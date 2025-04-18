import cv2 
import mediapipe as mp
import numpy as np 
from time import sleep
import math 
from pynput.keyboard import Controller

mp_hands = mp.solutions.hands
hand_model = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

keyboard_controller = Controller()

camera = cv2.VideoCapture(0)
camera.set(2, 150)

display_text = ""
temp_text = ""

class KeyButton():
    def __init__(self, position, label, dimensions=[70, 70]):
self.position = position
self.dimensions = dimensions
self.label = label

key_layout_upper = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "CLR"],
                    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "SPC"],
                    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "TOG"]]

key_layout_lower = [["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "CLR"],
                    ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";", "SPC"],
                    ["z", "x", "c", "v", "b", "n", "m", ",", ".", "/", "TOG"]]

def render_keys(img, button_list):
    for button in button_list:
        x, y = button.position
        w, h = button.dimensions
        cv2.rectangle(img, button.position, (x + w, y + h), (96, 96, 96), cv2.FILLED)
        cv2.putText(img, button.label, (x + 10, y + 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    return img

upper_buttons = []
lower_buttons = []

for i in range(len(key_layout_upper)):
    for j, key in enumerate(key_layout_upper[i]):
upper_buttons.append(KeyButton([80 * j + 10, 80 * i + 10], key))

for i in range(len(key_layout_lower)):
    for j, key in enumerate(key_layout_lower[i]):
lower_buttons.append(KeyButton([80 * j + 10, 80 * i + 10], key))

mode = 0
delay_counter = 0

def calc_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

x_points = [300, 245, 200, 170, 145, 130, 112, 103, 93, 87, 80, 75, 70, 67, 62, 59, 57]
y_points = [20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]
coefficient = np.polyfit(x_points, y_points, 2)

while True:
    success, frame = camera.read()
    frame = cv2.resize(frame, (1000, 580))
    frame = cv2.flip(frame, 1)
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hand_model.process(rgb_frame)
    landmarks = []

    if mode == 0:
        frame = render_keys(frame, upper_buttons)
current_buttons = upper_buttons
toggle_direction = "up"
    else:
        frame = render_keys(frame, lower_buttons)
current_buttons = lower_buttons
toggle_direction = "down"

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            for idx, landmark in enumerate(hand_landmarks.landmark):
                height, width, _ = frame.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
landmarks.append([idx, cx, cy])

    if landmarks:
        try:
x_thumb, y_thumb = landmarks[5][1], landmarks[5][2]
x_pinky, y_pinky = landmarks[17][1], landmarks[17][2]
            distance = calc_distance(x_thumb, y_thumb, x_pinky, y_pinky)
            A, B, C = coefficient
distance_cm = A * distance ** 2 + B * distance + C

            if 20 <distance_cm< 50:
x_index, y_index = landmarks[8][1], landmarks[8][2]
x_middle, y_middle = landmarks[6][1], landmarks[6][2]
x_ring, y_ring = landmarks[12][1], landmarks[12][2]

                cv2.circle(frame, (x_index, y_index), 20, (255, 0, 255), cv2.FILLED)
                cv2.circle(frame, (x_ring, y_ring), 20, (255, 0, 255), cv2.FILLED)

                if y_middle>y_index:
                    for button in current_buttons:
x_button, y_button = button.position
w_button, h_button = button.dimensions

                        if (x_button<x_index<x_button + w_button) and (y_button<y_index<y_button + h_button):
                            cv2.rectangle(frame, (x_button - 5, y_button - 5), (x_button + w_button + 5, y_button + h_button + 5), (160, 160, 160), cv2.FILLED)
                            cv2.putText(frame, button.label, (x_button + 20, y_button + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)

                            if calc_distance(x_index, y_index, x_ring, y_ring) < 50 and delay_counter == 0:
key_pressed = button.label
                                cv2.rectangle(frame, (x_button - 5, y_button - 5), (x_button + w_button + 5, y_button + h_button + 5), (255, 255, 255), cv2.FILLED)
                                cv2.putText(frame, key_pressed, (x_button + 20, y_button + 65), cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 0), 4)

                                if key_pressed == "SPC":
temp_text = ' '
display_text += temp_text
keyboard_controller.press(temp_text)
elifkey_pressed == "CLR":
temp_text = display_text[:-1]
display_text = temp_text
keyboard_controller.press('\b')
elifkey_pressed == "TOG" and toggle_direction == "up":
                                    mode = 1
elifkey_pressed == "TOG" and toggle_direction == "down":
                                    mode = 0
                                else:
display_text += key_pressed
keyboard_controller.press(key_pressed)
delay_counter = 1

        except Exception as e:
            print(e)
            pass

    if delay_counter != 0:
delay_counter += 1
        if delay_counter> 10:
delay_counter = 0

    cv2.rectangle(frame, (20, 250), (850, 400), (255, 255, 255), cv2.FILLED)
    cv2.putText(frame, display_text, (30, 300), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
    cv2.imshow('Virtual Keyboard', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
