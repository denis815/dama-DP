import cv2
import json
import numpy as np
import os

pattern_size = (7, 7)  # vnútorné rohy
cap = cv2.VideoCapture(0)

print("Umiestni šachovnicu do stredu a stlač 's' pre uloženie.")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    found, corners = cv2.findChessboardCorners(gray, pattern_size)

    vis = frame.copy()
    if found:
        cv2.drawChessboardCorners(vis, pattern_size, corners, found)

    cv2.imshow("Kalibracia hracej plochy", vis)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('s') and found:
        print("\nRozpoznané rohy, enerujem sqdict.json...")

        corners = corners.reshape((7, 7, 2))

        top_left = corners[0, 0]
        top_right = corners[0, -1]
        bottom_left = corners[-1, 0]
        bottom_right = corners[-1, -1]

        def extrapolate_corner(p, vec, scale):
            return p + vec * scale

        extended_corners = np.zeros((9, 9, 2), dtype=np.float32)
        for i in range(9):
            for j in range(9):
                y = (i - 1) / 6.0
                x = (j - 1) / 6.0
                base = (1 - x) * (1 - y) * top_left + \
                       x * (1 - y) * top_right + \
                       (1 - x) * y * bottom_left + \
                       x * y * bottom_right
                extended_corners[i, j] = base

        for i in [0, 8]:
            for j in range(1, 8):
                extended_corners[i, j] = extended_corners[1 if i == 0 else 7, j] + (extended_corners[1 if i == 0 else 7, j] - extended_corners[2 if i == 0 else 6, j])
        for j in [0, 8]:
            for i in range(1, 8):
                extended_corners[i, j] = extended_corners[i, 1 if j == 0 else 7] + (extended_corners[i, 1 if j == 0 else 7] - extended_corners[i, 2 if j == 0 else 6])

        extended_corners[0, 0] = extended_corners[1, 1] + (extended_corners[1, 1] - extended_corners[2, 2])
        extended_corners[0, 8] = extended_corners[1, 7] + (extended_corners[1, 7] - extended_corners[2, 6])
        extended_corners[8, 0] = extended_corners[7, 1] + (extended_corners[7, 1] - extended_corners[6, 2])
        extended_corners[8, 8] = extended_corners[7, 7] + (extended_corners[7, 7] - extended_corners[6, 6])

        sqdict = {}
        for i in range(8):
            for j in range(8):
                pts = [
                    extended_corners[i][j],
                    extended_corners[i][j+1],
                    extended_corners[i+1][j+1],
                    extended_corners[i+1][j]
                ]
                square_name = f"{chr(ord('a') + j)}{8 - i}"
                sqdict[square_name] = [[int(round(p[0])), int(round(p[1]))] for p in pts]

        output_path = os.path.join("src", "sqdict.json")
        try:
            with open(output_path, "w") as f:
                json.dump(sqdict, f, indent=4)
            print("sqdict.json uložený, počet polí:", len(sqdict))
        except Exception as e:
            print("Chyba pri ukladaní sqdict.json:", e)

        import time
        time.sleep(1)
        print("Zobrazenie výslednej mriežky...")
        with open(output_path, "r") as f:
            sqdict = json.load(f)

        for square, corners in sqdict.items():
            pts = [tuple(point) for point in corners]
            pts = sorted(pts, key=lambda x: (x[1], x[0]))
            cv2.polylines(frame, [np.array(pts)], isClosed=True, color=(0, 255, 0), thickness=1)
            cx = int(sum([p[0] for p in pts]) / 4)
            cy = int(sum([p[1] for p in pts]) / 4)
            cv2.putText(frame, square, (cx - 10, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow("Vizualizacia sqdict.json", frame)
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        break

    elif key & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
