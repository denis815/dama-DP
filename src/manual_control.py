import serial
import keyboard
import time
import json
import os

arduino = serial.Serial('COM7', 9600) 

key_map = {
    'q': 'B+', 'a': 'B-',
    'w': 'E+', 's': 'E-',
    'e': 'S+', 'd': 'S-'
}

pressed = set()
last_positions = {'B': 0, 'E': 0, 'S': 0}
calibration_file = 'calibration_map.json'

if os.path.exists(calibration_file):
    with open(calibration_file, 'r') as f:
        calibration_map = json.load(f)
else:
    calibration_map = {}

def send_command(cmd):
    arduino.write((cmd + '\n').encode())

try:
    print("Stlač Q/A pre base, W/S pre elbow, E/D pre shoulder")
    print("Stlač ENTER pre uloženie aktuálnej pozície")

    while True:
        for key, cmd in key_map.items():
            if keyboard.is_pressed(key):
                if key not in pressed:
                    send_command(cmd)
                    pressed.add(key)
            else:
                if key in pressed:
                    send_command(cmd[0] + '0')
                    pressed.remove(key)

        if arduino.in_waiting:
            line = arduino.readline().decode().strip()
            if line.startswith("POS"):
                parts = line.split()
                last_positions['B'] = int(parts[1][2:])
                last_positions['E'] = int(parts[2][2:])
                last_positions['S'] = int(parts[3][2:])
                print(f"\rBase: {last_positions['B']}  Elbow: {last_positions['E']}  Shoulder: {last_positions['S']}   ", end='')

        if keyboard.is_pressed('b'):
            break
        # Uloženie pozicie do json
        if keyboard.is_pressed('enter'):
            print("\nZadaj označenie políčka (napr. e3): ")
            while True:
                pole = input(">> ").strip().lower()
                if pole in calibration_map:
                    calibration_map[pole] = [
                        last_positions['B'],
                        last_positions['E'],
                        last_positions['S']
                    ]
                    with open(calibration_file, 'w') as f:
                        json.dump(calibration_map, f, indent=2)
                    print(f"✅ Pozícia uložená pre {pole}: {calibration_map[pole]}")
                    break
                else:
                    print(f"❌ Políčko '{pole}' nie je v mapovacom súbore, zadaj ine.")

            time.sleep(0.5) 

except KeyboardInterrupt:
    print("\nUkončené.")
