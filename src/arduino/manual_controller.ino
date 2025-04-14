#include <AccelStepper.h>

#define X_STEP_PIN 54
#define X_DIR_PIN 55
#define X_ENABLE_PIN 38

#define Y_STEP_PIN 60
#define Y_DIR_PIN 61
#define Y_ENABLE_PIN 56

#define Z_STEP_PIN 46
#define Z_DIR_PIN 48
#define Z_ENABLE_PIN 62

AccelStepper shoulder(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper elbow(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper base(AccelStepper::DRIVER, Z_STEP_PIN, Z_DIR_PIN);

const float speed = 200.0;

void setup() {
  Serial.begin(9600);
  pinMode(X_ENABLE_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);
  pinMode(Z_ENABLE_PIN, OUTPUT);
  digitalWrite(X_ENABLE_PIN, LOW);
  digitalWrite(Y_ENABLE_PIN, LOW);
  digitalWrite(Z_ENABLE_PIN, LOW);
  base.setMaxSpeed(speed);
  elbow.setMaxSpeed(speed);
  elbow.setPinsInverted(true, false, false);
  shoulder.setMaxSpeed(speed);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    char motor = command.charAt(0);
    char dir = command.charAt(1);

    long motorSpeed = 0;
    if (dir == '+') motorSpeed = speed;
    else if (dir == '-') motorSpeed = -speed;
    else motorSpeed = 0;

    switch (motor) {
      case 'B': base.setSpeed(motorSpeed); break;
      case 'E': elbow.setSpeed(motorSpeed); break;
      case 'S': shoulder.setSpeed(motorSpeed); break;
    }
  }

  base.runSpeed();
  elbow.runSpeed();
  shoulder.runSpeed();

  static unsigned long lastPrint = 0;
  if (millis() - lastPrint > 200) {
    lastPrint = millis();
    Serial.print("POS B:");
    Serial.print(base.currentPosition());
    Serial.print(" E:");
    Serial.print(-elbow.currentPosition());
    Serial.print(" S:");
    Serial.println(shoulder.currentPosition());
  }
}
