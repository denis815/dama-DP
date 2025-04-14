#include <AccelStepper.h>
//final
// Definovanie pinov pre krokové motory (RAMPS 1.4)
#define X_STEP_PIN 54
#define X_DIR_PIN 55
#define X_ENABLE_PIN 38

#define Y_STEP_PIN 60
#define Y_DIR_PIN 61
#define Y_ENABLE_PIN 56

#define Z_STEP_PIN 46
#define Z_DIR_PIN 48
#define Z_ENABLE_PIN 62

#define GRIPPER_PIN 10  

AccelStepper shoulder(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper elbow(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper base(AccelStepper::DRIVER, Z_STEP_PIN, Z_DIR_PIN);

const float maxSpeed = 330.0;
const float acceleration = 80.0;

int state = 0;  // 0: čaká na elbow, 1: shoulder, 2: base
float e_val = 0, s_val = 0, b_val = 0;

void setup() {
  Serial.begin(9600);

  pinMode(X_ENABLE_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);
  pinMode(Z_ENABLE_PIN, OUTPUT);

  digitalWrite(X_ENABLE_PIN, LOW);
  digitalWrite(Y_ENABLE_PIN, LOW);
  digitalWrite(Z_ENABLE_PIN, LOW);

  pinMode(GRIPPER_PIN, OUTPUT);
  digitalWrite(GRIPPER_PIN, LOW);

  shoulder.setMaxSpeed(maxSpeed);
  shoulder.setAcceleration(acceleration);

  elbow.setMaxSpeed(maxSpeed);
  elbow.setAcceleration(acceleration);

  base.setMaxSpeed(maxSpeed);
  base.setAcceleration(acceleration);

  Serial.println("init");
}

void loop() {
  if (Serial.available() > 0) {
    float input = Serial.readStringUntil('\n').toFloat();
    Serial.print("Received: ");
    Serial.println(input);

    if (input == 900) {
      rest();
    } else if (input == 901) {
      grasp();
    } else if (input == 902) {
      drop();
    } else {
      if (state == 0) {
        e_val = input;
        state = 1;
      } else if (state == 1) {
        s_val = input;
        state = 2;
      } else if (state == 2) {
        b_val = input;
        state = 0;
        moveAll(e_val, s_val, b_val);
      }
    }
  }

  base.run();
  elbow.run();
  shoulder.run();
}

void moveAll(float e, float s, float b) {
  Serial.print("Moving to: E="); Serial.print(e);
  Serial.print(" S="); Serial.print(s);
  Serial.print(" B="); Serial.println(b);

  elbow.moveTo(e);
  shoulder.moveTo(s);
  base.moveTo(b);

  while (elbow.distanceToGo() != 0 || shoulder.distanceToGo() != 0 || base.distanceToGo() != 0) {
    elbow.run();
    shoulder.run();
    base.run();
  }
}

void grasp() {
  Serial.println("Grasping (magnet ON)");
  digitalWrite(GRIPPER_PIN, HIGH);
}

void drop() {
  Serial.println("Dropping (magnet OFF)");
  digitalWrite(GRIPPER_PIN, LOW);
}

void rest() {
  Serial.println("Resetting to rest position");
  moveAll(0, 0, 0);
}
