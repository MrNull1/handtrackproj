#include <Stepper.h>

const int STEPS_PER_REV = 2048;
const int MAX_POSITION = 1023;

Stepper stepper(STEPS_PER_REV, 8, 10, 9, 11);  // IN1,IN3,IN2,IN4

int targetPos = 512;
int currentPos = 512;

void setup() {
  Serial.begin(9600);
  stepper.setSpeed(15);  // RPM
}

void loop() {
  if (Serial.available()) {
    targetPos = constrain(Serial.parseInt(), 0, MAX_POSITION);
    
    int stepsToMove = map(targetPos, 0, MAX_POSITION, 0, STEPS_PER_REV) - currentPos;
    
    if (stepsToMove != 0) {
      stepper.step(stepsToMove);
      currentPos += stepsToMove;
    }
  }
}