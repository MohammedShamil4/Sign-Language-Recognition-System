# Imports

import cv2
import mediapipe as mp
import pyautogui
import math
from enum import IntEnum

from google.protobuf.json_format import MessageToDict


import pyttsx3
engine = pyttsx3.init()
pyautogui.FAILSAFE = False
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
# from src.voice import playsong


# Gesture Encodings

class Gest(IntEnum):
    # Binary Encoded
    """
    Enum for mapping all hand gesture to binary number.
    """

    FIST = 0
    PINKY = 1
    RING = 2
    MID = 4
    LAST3 = 7
    INDEX = 8
    FIRST2 = 12
    LAST4 = 15
    THUMB = 16
    PALM = 31

    # Extra Mappings
    V_GEST = 33
    TWO_FINGER_CLOSED = 34
    PINCH_MAJOR = 35
    PINCH_MINOR = 36


# Multi-handedness Labels
class HLabel(IntEnum):
    MINOR = 0
    MAJOR = 1


# Convert Mediapipe Landmarks to recognizable Gestures
class HandRecog:
    """
    Convert Mediapipe Landmarks to recognizable Gestures.
    """

    def __init__(self, hand_label):
        """
        Constructs all the necessary attributes for the HandRecog object.

        Parameters
        ----------
            finger : int
                Represent gesture corresponding to Enum 'Gest',
                stores computed gesture for current frame.
            ori_gesture : int
                Represent gesture corresponding to Enum 'Gest',
                stores gesture being used.
            prev_gesture : int
                Represent gesture corresponding to Enum 'Gest',
                stores gesture computed for previous frame.
            frame_count : int
                total no. of frames since 'ori_gesture' is updated.
            hand_result : Object
                Landmarks obtained from mediapipe.
            hand_label : int
                Represents multi-handedness corresponding to Enum 'HLabel'.
        """

        self.finger = 0
        self.ori_gesture = Gest.PALM
        self.prev_gesture = Gest.PALM
        self.frame_count = 0
        self.hand_result = None
        self.hand_label = hand_label

    def update_hand_result(self, hand_result):
        self.hand_result = hand_result

    def get_signed_dist(self, point):
        """
        returns signed euclidean distance between 'point'.

        Parameters
        ----------
        point : list contaning two elements of type list/tuple which represents
            landmark point.

        Returns
        -------
        float
        """
        sign = -1
        if self.hand_result.landmark[point[0]].y < self.hand_result.landmark[point[1]].y:
            sign = 1
        dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x) ** 2
        dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y) ** 2
        dist = math.sqrt(dist)
        return dist * sign

    def get_dist(self, point):
        """
        returns euclidean distance between 'point'.

        Parameters
        ----------
        point : list contaning two elements of type list/tuple which represents
            landmark point.

        Returns
        -------
        float
        """
        dist = (self.hand_result.landmark[point[0]].x - self.hand_result.landmark[point[1]].x) ** 2
        dist += (self.hand_result.landmark[point[0]].y - self.hand_result.landmark[point[1]].y) ** 2
        dist = math.sqrt(dist)
        return dist

    def get_dz(self, point):
        """
        returns absolute difference on z-axis between 'point'.

        Parameters
        ----------
        point : list contaning two elements of type list/tuple which represents
            landmark point.

        Returns
        -------
        float
        """
        return abs(self.hand_result.landmark[point[0]].z - self.hand_result.landmark[point[1]].z)

    # Function to find Gesture Encoding using current finger_state.
    # Finger_state: 1 if finger is open, else 0
    def set_finger_state(self):
        """
        set 'finger' by computing ratio of distance between finger tip
        , middle knuckle, base knuckle.

        Returns
        -------
        None
        """
        if self.hand_result == None:
            return

        points = [[8, 5, 0], [12, 9, 0], [16, 13, 0], [20, 17, 0]]
        self.finger = 0
        self.finger = self.finger | 0  # thumb
        for idx, point in enumerate(points):

            dist = self.get_signed_dist(point[:2])
            dist2 = self.get_signed_dist(point[1:])

            try:
                ratio = round(dist / dist2, 1)
            except:
                ratio = round(dist1 / 0.01, 1)

            self.finger = self.finger << 1
            if ratio > 0.5:
                self.finger = self.finger | 1

    # Handling Fluctations due to noise
    def get_gesture(self):
        """
        returns int representing gesture corresponding to Enum 'Gest'.
        sets 'frame_count', 'ori_gesture', 'prev_gesture',
        handles fluctations due to noise.

        Returns
        -------
        int
        """
        if self.hand_result == None:
            return Gest.PALM

        current_gesture = Gest.PALM
        if self.finger in [Gest.LAST3, Gest.LAST4] and self.get_dist([8, 4]) < 0.05:
            if self.hand_label == HLabel.MINOR:
                current_gesture = Gest.PINCH_MINOR
            else:
                current_gesture = Gest.PINCH_MAJOR

        elif Gest.FIRST2 == self.finger:
            point = [[8, 12], [5, 9]]
            dist1 = self.get_dist(point[0])
            dist2 = self.get_dist(point[1])
            ratio = dist1 / dist2
            if ratio > 1.7:
                current_gesture = Gest.V_GEST
            else:
                if self.get_dz([8, 12]) < 0.1:
                    current_gesture = Gest.TWO_FINGER_CLOSED
                else:
                    current_gesture = Gest.MID

        else:
            current_gesture = self.finger

        if current_gesture == self.prev_gesture:
            self.frame_count += 1
        else:
            self.frame_count = 0

        self.prev_gesture = current_gesture

        if self.frame_count > 4:
            self.ori_gesture = current_gesture
        return self.ori_gesture


# Executes commands according to detected gestures
class Controller:
    """
    Executes commands according to detected gestures.

    Attributes
    ----------
    tx_old : int
        previous mouse location x coordinate
    ty_old : int
        previous mouse location y coordinate
    flag : bool
        true if V gesture is detected
    grabflag : bool
        true if FIST gesture is detected
    pinchmajorflag : bool
        true if PINCH gesture is detected through MAJOR hand,
        on x-axis 'Controller.changesystembrightness',
        on y-axis 'Controller.changesystemvolume'.
    pinchminorflag : bool
        true if PINCH gesture is detected through MINOR hand,
        on x-axis 'Controller.scrollHorizontal',
        on y-axis 'Controller.scrollVertical'.
    pinchstartxcoord : int
        x coordinate of hand landmark when pinch gesture is started.
    pinchstartycoord : int
        y coordinate of hand landmark when pinch gesture is started.
    pinchdirectionflag : bool
        true if pinch gesture movment is along x-axis,
        otherwise false
    prevpinchlv : int
        stores quantized magnitued of prev pinch gesture displacment, from
        starting position
    pinchlv : int
        stores quantized magnitued of pinch gesture displacment, from
        starting position
    framecount : int
        stores no. of frames since 'pinchlv' is updated.
    prev_hand : tuple
        stores (x, y) coordinates of hand in previous frame.
    pinch_threshold : float
        step size for quantization of 'pinchlv'.
    """

    tx_old = 0
    ty_old = 0
    trial = True
    flag = False
    grabflag = False
    pinchmajorflag = False
    pinchminorflag = False
    pinchstartxcoord = None
    pinchstartycoord = None
    pinchdirectionflag = None
    prevpinchlv = 0
    pinchlv = 0
    framecount = 0
    prev_hand = None
    pinch_threshold = 0.3

    def getpinchylv(hand_result):
        """returns distance beween starting pinch y coord and current hand position y coord."""
        dist = round((Controller.pinchstartycoord - hand_result.landmark[8].y) * 10, 1)
        return dist

    def getpinchxlv(hand_result):
        """returns distance beween starting pinch x coord and current hand position x coord."""
        dist = round((hand_result.landmark[8].x - Controller.pinchstartxcoord) * 10, 1)
        return dist

    # def changesystembrightness():
    #     """sets system brightness based on 'Controller.pinchlv'."""
    #     currentBrightnessLv = sbcontrol.get_brightness(display=0)/100.0
    #     currentBrightnessLv += Controller.pinchlv/50.0
    #     if currentBrightnessLv > 1.0:
    #         currentBrightnessLv = 1.0
    #     elif currentBrightnessLv < 0.0:
    #         currentBrightnessLv = 0.0
    #     sbcontrol.fade_brightness(int(100*currentBrightnessLv) , start = sbcontrol.get_brightness(display=0))
    #
    # def changesystemvolume():
    #     """sets system volume based on 'Controller.pinchlv'."""
    #     devices = AudioUtilities.GetSpeakers()
    #     interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    #     volume = cast(interface, POINTER(IAudioEndpointVolume))
    #     currentVolumeLv = volume.GetMasterVolumeLevelScalar()
    #     currentVolumeLv += Controller.pinchlv/50.0
    #     if currentVolumeLv > 1.0:
    #         currentVolumeLv = 1.0
    #     elif currentVolumeLv < 0.0:
    #         currentVolumeLv = 0.0
    #     volume.SetMasterVolumeLevelScalar(currentVolumeLv, None)

    # def scrollVertical():
    #     """scrolls on screen vertically."""
    #     pyautogui.scroll(120 if Controller.pinchlv>0.0 else -120)
    #
    #
    # def scrollHorizontal():
    #     """scrolls on screen horizontally."""
    #     pyautogui.keyDown('shift')
    #     pyautogui.keyDown('ctrl')
    #     pyautogui.scroll(-120 if Controller.pinchlv>0.0 else 120)
    #     pyautogui.keyUp('ctrl')
    #     pyautogui.keyUp('shift')

    # Locate Hand to get Cursor Position
    # Stabilize cursor by Dampening
    def get_position(hand_result):
        """
        returns coordinates of current hand position.

        Locates hand to get cursor position also stabilize cursor by
        dampening jerky motion of hand.

        Returns
        -------
        tuple(float, float)
        """
        point = 9
        position = [hand_result.landmark[point].x, hand_result.landmark[point].y]
        sx, sy = pyautogui.size()
        x_old, y_old = pyautogui.position()
        x = int(position[0] * sx)
        y = int(position[1] * sy)
        if Controller.prev_hand is None:
            Controller.prev_hand = x, y
        delta_x = x - Controller.prev_hand[0]
        delta_y = y - Controller.prev_hand[1]

        distsq = delta_x ** 2 + delta_y ** 2
        ratio = 1
        Controller.prev_hand = [x, y]

        if distsq <= 25:
            ratio = 0
        elif distsq <= 900:
            ratio = 0.07 * (distsq ** (1 / 2))
        else:
            ratio = 2.1
        x, y = x_old + delta_x * ratio, y_old + delta_y * ratio
        return (x, y)

    def pinch_control_init(hand_result):
        """Initializes attributes for pinch gesture."""
        Controller.pinchstartxcoord = hand_result.landmark[8].x
        Controller.pinchstartycoord = hand_result.landmark[8].y
        Controller.pinchlv = 0
        Controller.prevpinchlv = 0
        Controller.framecount = 0

    # Hold final position for 5 frames to change status
    def pinch_control(hand_result, controlHorizontal, controlVertical):
        """
        calls 'controlHorizontal' or 'controlVertical' based on pinch flags,
        'framecount' and sets 'pinchlv'.

        Parameters
        ----------
        hand_result : Object
            Landmarks obtained from mediapipe.
        controlHorizontal : callback function assosiated with horizontal
            pinch gesture.
        controlVertical : callback function assosiated with vertical
            pinch gesture.

        Returns
        -------
        None
        """
        if Controller.framecount == 5:
            Controller.framecount = 0
            Controller.pinchlv = Controller.prevpinchlv

            if Controller.pinchdirectionflag == True:
                controlHorizontal()  # x

            elif Controller.pinchdirectionflag == False:
                controlVertical()  # y

        lvx = Controller.getpinchxlv(hand_result)
        lvy = Controller.getpinchylv(hand_result)

        if abs(lvy) > abs(lvx) and abs(lvy) > Controller.pinch_threshold:
            Controller.pinchdirectionflag = False
            if abs(Controller.prevpinchlv - lvy) < Controller.pinch_threshold:
                Controller.framecount += 1
            else:
                Controller.prevpinchlv = lvy
                Controller.framecount = 0

        elif abs(lvx) > Controller.pinch_threshold:
            Controller.pinchdirectionflag = True
            if abs(Controller.prevpinchlv - lvx) < Controller.pinch_threshold:
                Controller.framecount += 1
            else:
                Controller.prevpinchlv = lvx
                Controller.framecount = 0

    def handle_controls(gesture, hand_result):
        """Impliments all gesture functionality."""
        x, y = None, None
        if gesture != Gest.PALM:
            x, y = Controller.get_position(hand_result)

        # flag reset
        if gesture != Gest.FIST and Controller.grabflag:
            Controller.grabflag = False
            pyautogui.mouseUp(button="left")

        if gesture != Gest.PINCH_MAJOR and Controller.pinchmajorflag:
            Controller.pinchmajorflag = False

        if gesture != Gest.PINCH_MINOR and Controller.pinchminorflag:
            Controller.pinchminorflag = False

        # implementation
        if gesture == Gest.V_GEST:
            Controller.flag = True
            pyautogui.moveTo(x, y, duration=0.1)

        elif gesture == Gest.FIST:
            if not Controller.grabflag:
                Controller.grabflag = True
                pyautogui.mouseDown(button="left")
            pyautogui.moveTo(x, y, duration=0.1)

        elif gesture == Gest.MID and Controller.flag:
            pyautogui.click()
            Controller.flag = False

        elif gesture == Gest.INDEX and Controller.flag:
            pyautogui.click(button='right')
            Controller.flag = False

        elif gesture == Gest.TWO_FINGER_CLOSED and Controller.flag:
            pyautogui.doubleClick()
            Controller.flag = False

        elif gesture == Gest.PINCH_MINOR:
            if Controller.pinchminorflag == False:
                Controller.pinch_control_init(hand_result)
                Controller.pinchminorflag = True
            Controller.pinch_control(hand_result, Controller.scrollHorizontal, Controller.scrollVertical)

        elif gesture == Gest.PINCH_MAJOR:
            if Controller.pinchmajorflag == False:
                Controller.pinch_control_init(hand_result)
                Controller.pinchmajorflag = True
            Controller.pinch_control(hand_result, Controller.changesystembrightness, Controller.changesystemvolume)


'''
----------------------------------------  Main Class  ----------------------------------------
    Entry point of Gesture Controller
'''


class GestureController:
    """
    Handles camera, obtain landmarks from mediapipe, entry point
    for whole program.

    Attributes
    ----------
    gc_mode : int
        indicates weather gesture controller is running or not,
        1 if running, otherwise 0.
    cap : Object
        object obtained from cv2, for capturing video frame.
    CAM_HEIGHT : int
        highet in pixels of obtained frame from camera.
    CAM_WIDTH : int
        width in pixels of obtained frame from camera.
    hr_major : Object of 'HandRecog'
        object representing major hand.
    hr_minor : Object of 'HandRecog'
        object representing minor hand.
    dom_hand : bool
        True if right hand is domaniant hand, otherwise False.
        default True.
    """
    gc_mode = 0
    cap = None
    CAM_HEIGHT = None
    CAM_WIDTH = None
    hr_major = None  # Right Hand by default
    hr_minor = None  # Left hand by default
    dom_hand = True

    def __init__(self):
        """Initilaizes attributes."""
        GestureController.gc_mode = 1



    def classify_hands(results):
        """
        sets 'hr_major', 'hr_minor' based on classification(left, right) of
        hand obtained from mediapipe, uses 'dom_hand' to decide major and
        minor hand.
        """
        left, right = None, None
        try:
            handedness_dict = MessageToDict(results.multi_handedness[0])
            if handedness_dict['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[0]
            else:
                left = results.multi_hand_landmarks[0]
        except Exception as e:
            #print(e)

            pass

        try:
            handedness_dict = MessageToDict(results.multi_handedness[1])
            if handedness_dict['classification'][0]['label'] == 'Right':
                right = results.multi_hand_landmarks[1]
            else:
                left = results.multi_hand_landmarks[1]
        except:
            pass

        if GestureController.dom_hand == True:
            GestureController.hr_major = right
            GestureController.hr_minor = left
        else:
            GestureController.hr_major = left
            GestureController.hr_minor = right

    def stop(self):

        cv2.destroyAllWindows()
    def start(self):
        """
        Entry point of whole programm, caputres video frame and passes, obtains
        landmark from mediapipe and passes it to 'handmajor' and 'handminor' for
        controlling.
        """
        cap = cv2.VideoCapture(0)
        GestureController.CAM_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        GestureController.CAM_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        handmajor = HandRecog(HLabel.MAJOR)
        handminor = HandRecog(HLabel.MINOR)
        currentgustflag = ""
        txt=""
        with mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
            while cap.isOpened() and GestureController.gc_mode:
                success, image = cap.read()

                if not success:
                    #print("Ignoring empty camera frame.")
                    continue

                image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
                image.flags.writeable = False
                results = hands.process(image)

                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    GestureController.classify_hands(results)
                    handmajor.update_hand_result(GestureController.hr_major)
                    handminor.update_hand_result(GestureController.hr_minor)

                    handmajor.set_finger_state()
                    handminor.set_finger_state()
                    gest_name = str(handminor.get_gesture())
                    gest_name1 = str(handmajor.get_gesture())
                    print("==========", gest_name)
                    print("*********", gest_name1)
                    print("+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=")

                    if str(gest_name)=="15" and str(gest_name1)=="15":

                        cg="gesture_1"
                        if currentgustflag!=cg:
                            engine.say("hi all")
                            txt = "hi all"
                            print(txt)
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="15" and gest_name1=="0":
                        cg="gesture_2"
                        if currentgustflag!=cg:
                            engine.say("nice to meet you")
                            txt = "nice to meet you"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="15" and gest_name1=="1":
                        cg="gesture_3"
                        if currentgustflag!=cg:
                            engine.say("wait a minute")
                            txt = "wait a minute"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="15" and gest_name1=="3":
                        cg="gesture_4"
                        if currentgustflag!=cg:
                            engine.say("good to see")
                            txt = "good to see"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="15" and gest_name1=="7":
                        cg="gesture_5"
                        if currentgustflag!=cg:
                            engine.say("welcome")
                            txt = "welcome"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="15" and gest_name1=="8":
                        cg="gesture_6"
                        if currentgustflag!=cg:
                            engine.say(" let me think")
                            txt = "let me think"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="15" and gest_name1=="14":
                        cg="gesture_7"
                        if currentgustflag!=cg:
                            engine.say("let me say something")
                            txt = "let me say something"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="0" and gest_name1=="15":
                        cg="gesture_8"
                        if currentgustflag!=cg:
                            engine.say("stop")
                            txt = "stop"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="1" and gest_name1=="15":
                        cg="gesture_9"
                        if currentgustflag!=cg:
                            engine.say("say something")
                            txt = "say something"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="3" and gest_name1=="15":
                        cg="gesture_10"
                        if currentgustflag!=cg:
                            engine.say("it is important")
                            txt = "it is important"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="8" and gest_name1=="15":
                        cg="gesture_11"
                        if currentgustflag!=cg:
                            engine.say("almost there")
                            txt = "almost there"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="14" and gest_name1=="15":
                        cg="gesture_12"
                        if currentgustflag!=cg:
                            engine.say("thank you")
                            txt = "thank you"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="0" and gest_name1=="0":
                        cg="gesture_13"
                        if currentgustflag!=cg:
                            engine.say("pause")
                            txt = "pause"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="1" and gest_name1=="1":
                        cg="gesture_14"
                        if currentgustflag!=cg:
                            engine.say("wait")
                            txt = "wait"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="3" and gest_name1=="3":
                        cg="gesture_15"
                        if currentgustflag!=cg:
                            engine.say("smile")
                            txt = "smile"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="1" and gest_name1=="3":
                        cg="gesture_16"
                        if currentgustflag!=cg:
                            engine.say("respect")
                            txt = "respect"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="3" and gest_name1=="1":
                        cg="gesture_17"
                        if currentgustflag!=cg:
                            engine.say("another")
                            txt = "another"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="8" and gest_name1=="8":
                        cg="gesture_18"
                        if currentgustflag!=cg:
                            engine.say("focus on")
                            txt = "focus on"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="Gest.PALM" and gest_name1=="15":
                        cg="gesture_19"
                        if currentgustflag!=cg:
                            engine.say("hello")
                            txt = "hello"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="Gest.PALM" and gest_name1=="Gest.PINCH_MAJOR":
                        cg="gesture_20"
                        if currentgustflag!=cg:
                            engine.say("good")
                            txt = "good"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="Gest.PALM" and gest_name1=="3":
                        cg="gesture_21"
                        if currentgustflag!=cg:
                            engine.say("congratulate")
                            txt = "congratulate"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="Gest.PALM" and gest_name1=="1":
                        cg="gesture_22"
                        if currentgustflag!=cg:
                            engine.say("urgent")
                            txt = "urgent"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name=="1" and gest_name1=="Gest.PALM":
                        cg="gesture_21"
                        if currentgustflag!=cg:
                            engine.say("feels sad")
                            txt = "feels sad"
                            engine.runAndWait()
                            currentgustflag=cg

                    elif gest_name == "3" and gest_name1 == "Gest.PALM":
                        cg = "gesture_22"
                        if currentgustflag != cg:
                            engine.say("Hurry up")
                            txt = "Hurry up"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "15" and gest_name1 == "Gest.PALM":
                        cg = "gesture_23"
                        if currentgustflag != cg:
                            engine.say("well done")
                            txt = "well done"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "Gest.PINCH_MINOR" and gest_name1 == "Gest.PALM":
                        cg = "gesture_24"
                        if currentgustflag != cg:
                            engine.say("good morning")
                            txt = "good morning"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "0" and gest_name1 == "Gest.PALM":
                        cg = "gesture_25"
                        if currentgustflag != cg:
                            engine.say("join us")
                            txt = "join us"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "15" and gest_name1 == "Gest.PINCH_MAJOR":
                        cg = "gesture_26"
                        if currentgustflag != cg:
                            engine.say("one more time")
                            txt = "one more time"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "0" and gest_name1 == "1":
                        cg = "gesture_27"
                        if currentgustflag != cg:
                            engine.say("we have to move on")
                            txt = "we have to move on"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "0" and gest_name1 == "Gest.PINCH_MAJOR":
                        cg = "gesture_28"
                        if currentgustflag != cg:
                            engine.say("see you later")
                            txt = "see you later"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "0" and gest_name1 == "7":
                        cg = "gesture_29"
                        if currentgustflag != cg:
                            engine.say("okay")
                            txt = "okay"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "0" and gest_name1 == "8":
                        cg = "gesture_30"
                        if currentgustflag != cg:
                            engine.say("good evening")
                            txt = "good evening"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "0" and gest_name1 == "Gest.V_GEST":
                        cg = "gesture_30"
                        if currentgustflag != cg:
                            engine.say("we should consider")
                            txt = "we should consider"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "0" and gest_name1 == "14":
                        cg = "gesture_31"
                        if currentgustflag != cg:
                            engine.say("In my opinion")
                            txt = "In my opinion"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "0" and gest_name1 == "13":
                        cg = "gesture_32"
                        if currentgustflag != cg:
                            engine.say("on my way")
                            txt = "on my way"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "15" and gest_name1 == "13":
                        cg = "gesture_33"
                        if currentgustflag != cg:
                            engine.say("how can i help you")
                            txt = "how can i help you"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "1" and gest_name1 == "0":
                        cg = "gesture_34"
                        if currentgustflag != cg:
                            engine.say("have a great day")
                            txt = "have a great day"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "1" and gest_name1 == "8":
                        cg = "gesture_35"
                        if currentgustflag != cg:
                            engine.say("good night")
                            txt = "good night"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "1" and gest_name1 == "14":
                        cg = "gesture_35"
                        if currentgustflag != cg:
                            engine.say("good bye")
                            txt = "good bye"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "1" and gest_name1 == "13":
                        cg = "gesture_36"
                        if currentgustflag != cg:
                            engine.say("iam busy now")
                            txt = "good bye"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "8" and gest_name1 == "Gest.PALM":
                        cg = "gesture_37"
                        if currentgustflag != cg:
                            engine.say("excuse me")
                            txt = "excuse me"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "8" and gest_name1 == "0":
                        cg = "gesture_38"
                        if currentgustflag != cg:
                            engine.say("i have an idea")
                            txt = "i have an idea"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "8" and gest_name1 == "14":
                        cg = "gesture_38"
                        if currentgustflag != cg:
                            engine.say("let me clarify")
                            txt = "let me clarify"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "8" and gest_name1 == "7":
                        cg = "gesture_39"
                        if currentgustflag != cg:
                            engine.say("need a suggestion")
                            txt = "need a suggestion"
                            engine.runAndWait()
                            currentgustflag = cg

                    elif gest_name == "8" and gest_name1 == "1":
                        cg = "gesture_40"
                        if currentgustflag != cg:
                            engine.say("hang on")
                            txt = "hang on"
                            engine.runAndWait()
                            currentgustflag = cg

                    if gest_name == Gest.PINCH_MINOR:
                        #print(gest_name, "+=+=+=+=+=", currentgustflag)
                        if currentgustflag != gest_name:
                            print("========================================")
                            # engine.say("working on it")
                            # txt = "working on it"
                            # engine.runAndWait()
                            # playsong("gesture 1")

                        # Controller.handle_controls(gest_name, handminor.hand_result)
                    else:
                        gest_name = handmajor.get_gesture()
                        gest_name1 = handminor.get_gesture()
                        #print("+=+=+=+=+=+=", gest_name1)
                        #print(gest_name, "_+_+_+_+_+_+_+", currentgustflag)
                        # if str(gest_name)=="15":
                        #     #print("*****************************************")
                        #     if str(currentgustflag)!=str(gest_name):
                        #         #print("+++++++++++++++++++++++++++++++++++++++++++++++++")
                        #         playsong("gesture 0")
                        # if str(gest_name)=="1":
                        #     #print("*****************************************")
                        #     if str(currentgustflag)!=str(gest_name):
                        #         #print("+++++++++++++++++++++++++++++++++++++++++++++++++")
                        #         playsong("gesture 1")
                        # if str(gest_name)=="Gest.PINCH_MAJOR":
                        #     #print("*****************************************")
                        #     if str(currentgustflag)!=str(gest_name):
                        #         #print("+++++++++++++++++++++++++++++++++++++++++++++++++")
                        #         playsong("gesture 2")
                        # if str(gest_name)=="0":
                        #     #print("*****************************************")
                        #     if str(currentgustflag)!=str(gest_name):
                        #         #print("+++++++++++++++++++++++++++++++++++++++++++++++++")
                        #         playsong("gesture 3")
                        # if str(gest_name)=="Gest.V_GEST":
                        #     #print("*****************************************")
                        #     if str(currentgustflag)!=str(gest_name):
                        #         #print("+++++++++++++++++++++++++++++++++++++++++++++++++")
                        #         playsong("gesture 4")
                        # if str(gest_name)=="8":
                        #     #print("*****************************************")
                        #     if str(currentgustflag)!=str(gest_name):
                        #         #print("+++++++++++++++++++++++++++++++++++++++++++++++++")
                        #         playsong("gesture 5")
                        # if str(gest_name)=="3":
                        #     #print("*****************************************")
                        #     if str(currentgustflag)!=str(gest_name):
                        #         #print("+++++++++++++++++++++++++++++++++++++++++++++++++")
                        #         playsong("gesture 6")
                        # if str(gest_name)=="9":
                        #     #print("*****************************************")
                        #     if str(currentgustflag)!=str(gest_name):
                        #         #print("+++++++++++++++++++++++++++++++++++++++++++++++++")
                        #         playsong("gesture 7")
                        #
                        # currentgustflag=str(gest_name)
                        # # Controller.handle_controls(gest_name, handmajor.hand_result)

                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                else:
                    Controller.prev_hand = None

                # org
                org = (50, 50)

                # fontScale
                fontScale = 1

                # Blue color in BGR
                color = (255, 0, 0)

                # Line thickness of 2 px
                thickness = 2
                font = cv2.FONT_HERSHEY_SIMPLEX

                image = cv2.putText(image, txt, org, font,
                                    fontScale, color, thickness, cv2.LINE_AA)
                cv2.imshow('Gesture Controller', image)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
        cap.release()
        cap = cv2.VideoCapture(0)
        cap.release()

        cv2.destroyAllWindows()


gc1 = GestureController()
gc1.start()