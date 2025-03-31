#include <AccelStepper.h>

// Define stepper motor connections & interface type
#define MOTOR_INTERFACE_TYPE 4
#define STEP_PIN 10
#define DIR_PIN 11
#define ENABLE_PIN 12  // Optional, can be removed if not used

AccelStepper stepperMotor(MOTOR_INTERFACE_TYPE, STEP_PIN, DIR_PIN);

int targetPosition = 0;  // Desired motor position

void setup() {
    Serial.begin(115200);
    stepperMotor.setMaxSpeed(17);   // Max speed (higher = faster)
    stepperMotor.setAcceleration(500); // Acceleration rate
    stepperMotor.setSpeed(17);         // Start at zero speed
}

void loop() {
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');  // Read the serial input
        targetPosition = input.toInt();  // Convert to integer
    }

    // Set the new target position
    stepperMotor.moveTo(targetPosition);

    // Keep running the motor to reach the position
    stepperMotor.run();
}
