#include <Stepper.h>

// Define stepper motor connections & steps per revolution
#define STEPS_PER_REV 2048  // Adjust based on your motor's specifications
#define IN1_PIN 10
#define IN2_PIN 11
#define IN3_PIN 12
#define IN4_PIN 13

Stepper stepperMotor(STEPS_PER_REV, IN1_PIN, IN3_PIN, IN2_PIN, IN4_PIN);

int currentMotorPosition = 0;  // Track the motor's current position
int targetPosition = 0;       // Track the finger's position

void setup() {
    Serial.begin(115200);
    stepperMotor.setSpeed(17);  // Set the motor speed (RPM)
}

void loop() {
    // Check if there's new input from the serial monitor
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');  // Read the serial input
        targetPosition = input.toInt();  // Update the target position based on finger
    }

    // Continuously move the motor toward the target position
    if (currentMotorPosition < targetPosition) {
        stepperMotor.step(25);  // Move forward one step
        currentMotorPosition++;
    } else if (currentMotorPosition > targetPosition) {
        stepperMotor.step(-25);  // Move backward one step
        currentMotorPosition--;
    }
}
