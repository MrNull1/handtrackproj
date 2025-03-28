// Define ULN2003 input pins
const int IN1 = 13;
const int IN2 = 12;
const int IN3 = 11;
const int IN4 = 10;

// Full-step sequence (4 steps per cycle)
const int stepSequence[4][4] = {
  {1, 0, 0, 1},  // Step 1: IN1=HIGH, IN4=HIGH
  {1, 1, 0, 0},  // Step 2: IN1=HIGH, IN2=HIGH
  {0, 1, 1, 0},  // Step 3: IN2=HIGH, IN3=HIGH
  {0, 0, 1, 1}   // Step 4: IN3=HIGH, IN4=HIGH
};

void setup() {
  // Set all control pins as outputs
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    int step_count = Serial.parseInt();  // From Python
    int direction = (step_count > 0) ? 1 : -1;  // 1=CW, -1=CCW

    // Move the motor
    for (int i = 0; i < abs(step_count); i++) {
      for (int step = 0; step < 4; step++) {
        int currentStep = (direction == 1) ? step : 3 - step;  // Reverse for CCW
        digitalWrite(IN1, stepSequence[currentStep][0]);
        digitalWrite(IN2, stepSequence[currentStep][1]);
        digitalWrite(IN3, stepSequence[currentStep][2]);
        digitalWrite(IN4, stepSequence[currentStep][3]);
        delay(5);  // Adjust delay for speed (lower = faster)
      }
    }
  }
}