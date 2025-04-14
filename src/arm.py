import serial
import time
import json

SERIAL_PORT = 'COM7'
BAUD_RATE = 9600
COMMAND_DELAY = 2.0
LIFT_OFFSET = 550

ser = None
square_map = None

def init():
    global ser, square_map
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    square_map = load_square_map()
    print("Ruka pripravená")

def move_from_to(start_sq, end_sq):
    if not ser or not square_map:
        raise Exception("arm.init() musí byť zavolané ako prvé.")
    move_to_square(ser, start_sq, square_map, grasp=True)
    move_to_square(ser, end_sq, square_map, drop=True)

def move_to(square, grasp=False, drop=False):
    if not ser or not square_map:
        raise Exception("arm.init() musí byť zavolané ako prvé.")
    move_to_square(ser, square, square_map, grasp=grasp, drop=drop)

def load_square_map(path='calibration_map.json'):
    with open(path, 'r') as f:
        return json.load(f)

def send_number(ser, num):
    command = f"{num}\n"
    ser.write(command.encode())
    time.sleep(COMMAND_DELAY)

def move_to_position(ser, base, elbow, shoulder):
    send_number(ser, elbow)
    send_number(ser, shoulder)
    send_number(ser, base)

def move_to_square(ser, square, square_map, grasp=False, drop=False, lift_after_drop=True):
    if square not in square_map:
        print(f"Políčko {square} nie je v mapovaní.")
        return

    base, elbow, shoulder = square_map[square]
    lifted_shoulder = shoulder - LIFT_OFFSET

    print(f"Presun nad {square}")
    move_to_position(ser, base, elbow, lifted_shoulder)

    print("Zníženie na cieľovú pozíciu")
    move_to_position(ser, base, elbow, shoulder)

    if grasp:
        print("Uchopenie figúrky")
        send_number(ser, 901)
        print("Zdvih po uchopení")
        move_to_position(ser, base, elbow, lifted_shoulder)

    if drop:
        print("Položenie figúrky")
        send_number(ser, 902)

        if lift_after_drop:
            print("Zdvih po položení")
            move_to_position(ser, base, elbow, lifted_shoulder)

            if "home" in square_map:
                print("Presun na domovskú pozíciu")
                home_base, home_elbow, home_shoulder = square_map["home"]
                move_to_position(ser, home_base, home_elbow, home_shoulder)
            else:
                print("Pozícia 'home' nie je definovaná v calibration_map.json")


def main():
    print("Pripájanie k robotickej ruke...")
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
    except Exception as e:
        print("Nepodarilo sa pripojiť na port:", e)
        return

    square_map = load_square_map()

    print("Zadaj napr. 'e3', 'grasp e3', 'drop e5', alebo *.")
    while True:
        cmd = input("📍 Príkaz: ").strip().lower()
        if cmd == '*':
            break
        elif cmd == 'rest':
            send_number(ser, 900)
        elif cmd.startswith('grasp '):
            square = cmd.split()[1]
            move_to_square(ser, square, square_map, grasp=True)
        elif cmd.startswith('drop '):
            square = cmd.split()[1]
            move_to_square(ser, square, square_map, drop=True)
        else:
            move_to_square(ser, cmd, square_map)

    ser.close()
    print("Odpojené.")

if __name__ == '__main__':
    main()
