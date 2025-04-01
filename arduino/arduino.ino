#include <Stepper.h>

// Define stepper motor connections & steps per revolution
#define STEPS_PER_REV 2048  // Adjust based on your motor's specifications
#define IN1_PIN 10
#define IN2_PIN 11
#define IN3_PIN 12
#define IN4_PIN 13

Stepper stepperMotor(STEPS_PER_REV, IN1_PIN, IN3_PIN, IN2_PIN, IN4_PIN);

int currentPosition = 0;  // Track the current motor position

void setup() {
    Serial.begin(115200);
    stepperMotor.setSpeed(15);  // Set the motor speed (RPM)
}

void loop() {
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');  // Read the serial input
        int mappedPosition = input.toInt();          // Convert to integer

        // Stop the motor if the mapped position is -6 or 2
        if (mappedPosition == -6 || mappedPosition == 2) {
            // Do nothing to stop the motor
            return;
        }

        // Move motor forward for negative positions above -6
        if (mappedPosition < 0 && mappedPosition > -6) {
            stepperMotor.step(5);  // Move motor forward
        }

        // Move motor backward for positive positions below 2
        else if (mappedPosition > 0 && mappedPosition < 2) {
            stepperMotor.step(-5);  // Move motor backward
        }
    }
}
