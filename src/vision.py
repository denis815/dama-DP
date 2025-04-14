import cv2
import json
import numpy as np

COLOR_BLUE = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)


def load_square_dict(path="sqdict.json"):
    with open(path, 'r') as f:
        sqdict = json.load(f)
    return {k: np.array(v, dtype=np.int32) for k, v in sqdict.items()}


def detect_pieces(frame, sqdict):
    detected = {}
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_blue = np.array([100, 150, 50])
    upper_blue = np.array([130, 255, 255])

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 25, 255])

    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
    mask_white = cv2.inRange(hsv, lower_white, upper_white)

    for square, polygon in sqdict.items():
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [polygon], 255)

        blue_pixels = cv2.countNonZero(cv2.bitwise_and(mask_blue, mask))
        white_pixels = cv2.countNonZero(cv2.bitwise_and(mask_white, mask))

        if blue_pixels > 50:
            detected[square] = 'blue'
        elif white_pixels > 50:
            detected[square] = 'white'
        else:
            detected[square] = None

    return detected


def diff_states(before, after):
    removed = None
    added = None
    for square in before:
        if before[square] == 'blue' and after[square] is None:
            removed = square
        if before[square] is None and after[square] == 'blue':
            added = square
    if removed and added:
        return removed, added
    return None, None


if __name__ == "__main__":
    sqdict = load_square_dict()
    cap = cv2.VideoCapture(0)

    print("Stlač 'r' pre snímku pred pohybom, potom 's'.")

    state_before = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        for poly in sqdict.values():
            cv2.polylines(frame, [poly], isClosed=True, color=(255, 255, 255), thickness=1)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1)

        if key == ord('r'):
            state_before = detect_pieces(frame, sqdict)
            print("Uložený stav pred pohybom")

        elif key == ord('s') and state_before:
            state_after = detect_pieces(frame, sqdict)
            start, end = diff_states(state_before, state_after)
            print(f"Zistený pohyb: {start} -> {end}")
            state_before = None

        elif key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
