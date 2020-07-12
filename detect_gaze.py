import cv2
import numpy as np
import dlib
from math import hypot

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')

#--------------------------------------------------------------------------------------------------------------------
def midpoint(p1 ,p2):
    return int((p1.x + p2.x)/2), int((p1.y + p2.y)/2)

font = cv2.FONT_HERSHEY_PLAIN

#--------------------------------------------------------------------------------------------------------------------

def detect_faces(img, cascade):
    print ("start 3")
    gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    coords = cascade.detectMultiScale(gray_frame, 1.3, 5)
    if len(coords) > 1:
        biggest = (0, 0, 0, 0)
        for i in coords:
            if i[3] > biggest[3]:
                biggest = i
        biggest = np.array([i], np.int32)
    elif len(coords) == 1:
        biggest = coords
    else:
        return None
    for (x, y, w, h) in biggest:
        frame = img[y:y + h, x:x + w]
    return frame

#--------------------------------------------------------------------------------------------------------------------

def get_blinking_ratio(eye_points, facial_landmarks):
    left_point = (facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y)
    right_point = (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y)
    center_top = midpoint(facial_landmarks.part(eye_points[1]), facial_landmarks.part(eye_points[2]))
    center_bottom = midpoint(facial_landmarks.part(eye_points[5]), facial_landmarks.part(eye_points[4]))

    #hor_line = cv2.line(frame, left_point, right_point, (0, 255, 0), 2)
    #ver_line = cv2.line(frame, center_top, center_bottom, (0, 255, 0), 2)

    hor_line_lenght = hypot((left_point[0] - right_point[0]), (left_point[1] - right_point[1]))
    ver_line_lenght = hypot((center_top[0] - center_bottom[0]), (center_top[1] - center_bottom[1]))

    ratio = hor_line_lenght / ver_line_lenght
    return ratio

#--------------------------------------------------------------------------------------------------------------------

def get_gaze_ratio(img, gray, eye_points, facial_landmarks):
    left_eye_region = np.array([(facial_landmarks.part(eye_points[0]).x, facial_landmarks.part(eye_points[0]).y),
                                (facial_landmarks.part(eye_points[1]).x, facial_landmarks.part(eye_points[1]).y),
                                (facial_landmarks.part(eye_points[2]).x, facial_landmarks.part(eye_points[2]).y),
                                (facial_landmarks.part(eye_points[3]).x, facial_landmarks.part(eye_points[3]).y),
                                (facial_landmarks.part(eye_points[4]).x, facial_landmarks.part(eye_points[4]).y),
                                (facial_landmarks.part(eye_points[5]).x, facial_landmarks.part(eye_points[5]).y)], np.int32)
    # cv2.polylines(frame, [left_eye_region], True, (0, 0, 255), 2)

    height, width, _ = img.shape
    mask = np.zeros((height, width), np.uint8)
    cv2.polylines(mask, [left_eye_region], True, 255, 2)
    cv2.fillPoly(mask, [left_eye_region], 255)
    eye = cv2.bitwise_and(gray, gray, mask=mask)
    cv2.imshow('eye', eye)

    # min_x = np.min(left_eye_region[:, 0])
    # max_x = np.max(left_eye_region[:, 0])
    # min_y = np.min(left_eye_region[:, 1])
    # max_y = np.max(left_eye_region[:, 1])
    #
    # gray_eye = eye[min_y: max_y, min_x: max_x]
    # _, threshold_eye = cv2.threshold(gray_eye, 70, 255, cv2.THRESH_BINARY)
    # height, width = threshold_eye.shape
    # left_side_threshold = threshold_eye[0: height, 0: int(width / 2)]
    # left_side_white = cv2.countNonZero(left_side_threshold)
    #
    # right_side_threshold = threshold_eye[0: height, int(width /2): width]
    # right_side_white = cv2.countNonZero(right_side_threshold)
    #
    #
    # if left_side_white == 0:
    #     gaze_ratio = 1
    # elif right_side_white == 0:
    #     gaze_ratio = 5
    # else:
    #     gaze_ratio = left_side_white / right_side_white
    # return gaze_ratio


def main():
    print ('start')
    img = cv2.imread('elon.jpg')
    new_frame = np.zeros((500, 500, 3), np.uint8)
    print('start2')
    faces = detect_faces(img, face_cascade)
    # if faces is not None:
    #     landmarks = predictor(gray, face)
    gray = cv2.cvtColor(faces, cv2.COLOR_BGR2GRAY)
    faces_i = detector(gray)
    for face in faces_i:
        landmarks = predictor(gray, face)
        left_eye_ratio = get_blinking_ratio([36, 37, 38, 39, 40, 41], landmarks)
        right_eye_ratio = get_blinking_ratio([42, 43, 44, 45, 46, 47], landmarks)
        blinking_ratio = (left_eye_ratio + right_eye_ratio) / 2

        print(blinking_ratio)

        # if blinking_ratio > 5.7:
        #     cv2.putText(img, "BLINKING", (50, 150), font, 7, (255, 0, 0))
        print ("in")
            # Gaze detection
        gaze_ratio_left_eye = get_gaze_ratio(img,gray, [36, 37, 38, 39, 40, 41], landmarks)
        gaze_ratio_right_eye = get_gaze_ratio(img,gray, [42, 43, 44, 45, 46, 47], landmarks)
        gaze_ratio = (gaze_ratio_right_eye + gaze_ratio_left_eye) / 2
        print (gaze_ratio)

        if gaze_ratio <= 1:
            cv2.putText(img, "RIGHT", (50, 100), font, 2, (0, 0, 255), 3)

        elif 1 < gaze_ratio < 1.7:
            cv2.putText(img, "CENTER", (50, 100), font, 2, (0, 0, 255), 3)
            new_frame[:] = (0, 0, 255)
        else:
            new_frame[:] = (255, 0, 0)
            cv2.putText(img, "LEFT", (50, 100), font, 2, (0, 0, 255), 3)


    # cv2.imshow('gray_eye', gray_eye)
    # cv2.imshow('threshold', threshold)
    # cv2.imshow('eye', eye)
    cv2.imshow("faces", faces)
    #cv2.imshow("new_frame", new_frame)
    cv2.imshow("img", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()