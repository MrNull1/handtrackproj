#include <Stepper.h>

// Define stepper motor connections & steps per revolution
#define STEPS_PER_REV 2048
#define NUM_MOTORS 4  // Number of stepper motors (4 fingers)

// Pins for each motor
const int motorPins[NUM_MOTORS][4] = {
    {10, 11, 12, 13},   // Motor 1 (Index Finger)
    {6, 7, 8, 9},       // Motor 2 (Middle Finger)
    {2, 3, 4, 5},       // Motor 3 (Ring Finger)
    {23, 25, 27, 29}    // Motor 4 (Pinky Finger)
};

// Create Stepper objects for each motor
Stepper stepperMotors[NUM_MOTORS] = {
    Stepper(STEPS_PER_REV, motorPins[0][0], motorPins[0][2], motorPins[0][1], motorPins[0][3]),
    Stepper(STEPS_PER_REV, motorPins[1][0], motorPins[1][2], motorPins[1][1], motorPins[1][3]),
    Stepper(STEPS_PER_REV, motorPins[2][0], motorPins[2][2], motorPins[2][1], motorPins[2][3]),
    Stepper(STEPS_PER_REV, motorPins[3][0], motorPins[3][2], motorPins[3][1], motorPins[3][3])
};

// Track the motor positions
int currentMotorPositions[NUM_MOTORS] = {0, 0, 0, 0};
int targetPositions[NUM_MOTORS] = {0, 0, 0, 0};
int microPositions[NUM_MOTORS] = {0, 0, 0, 0};

// Tweakable step limits for each finger
const int stepLimits[NUM_MOTORS] = {80, 70, 100, 90};  // Example values: Index, Middle, Ring, Pinky

void setup() {
    Serial.begin(115200);
    for (int i = 0; i < NUM_MOTORS; i++) {
        stepperMotors[i].setSpeed(10);  // Set motor speed to a reasonable low value (adjust as necessary)
    }
}

void loop() {
    // Check if there's new input from the serial monitor
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');  // Read the serial input
        int i = 0;
        String temp = ""; 
        for (int j = 0; j < input.length(); j++) {
            if (input.charAt(j) == ',' || j == input.length() - 1) {
                // Check for comma or last character of the string
                if (j == input.length() - 1) {
                    temp += input.charAt(j); // Add the last character
                }
                targetPositions[i++] = temp.toInt();  // Convert to integer and store
                temp = "";  // Reset for next number
            } else {
                temp += input.charAt(j);  // Accumulate characters for each number
            }
        }
    }

    // Move each motor towards its target position gradually
    for (int i = 0; i < NUM_MOTORS; i++) {
        if (currentMotorPositions[i] < targetPositions[i]) {
            stepperMotors[i].step(1);  // Move forward by one step
            microPositions[i]++;
            if (microPositions[i] >= stepLimits[i]) {  // Use tweakable limit for each motor
                currentMotorPositions[i]++;
                microPositions[i] = 0;
            }
        } else if (currentMotorPositions[i] > targetPositions[i]) {
            stepperMotors[i].step(-1);  // Move backward by one step
            microPositions[i]--;
            if (microPositions[i] <= -stepLimits[i]) {  // Use tweakable limit for each motor
                currentMotorPositions[i]--;
                microPositions[i] = 0;
            }
        }
    }
}
