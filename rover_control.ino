#include <Stepper.h>

// Motor Driver Pins
#define ML_Ctrl 4     // Left motor direction control
#define ML_PWM 5      // Left motor PWM speed control
#define MR_Ctrl 2     // Right motor direction control
#define MR_PWM 9      // Right motor PWM speed control
#define ML1_Ctrl 7    // Extra left motor (if used)
#define ML1_PWM 6
#define MR1_Ctrl 8    // Extra right motor (if used)
#define MR1_PWM 10

// Moisture Sensor
#define sensorPin A0  // Soil moisture analog input

// Stepper Motor Pins (used for spraying mechanism)
#define IN1 3
#define IN2 A3
#define IN3 A4
#define IN4 A5

// Stepper motor setup
const int steps_per_rev = 512;
Stepper motor(steps_per_rev, IN1, IN3, IN2, IN4);

// Variables
int messageGot;
float waterLevel;

void setup() {
  Serial.begin(9600);
  motor.setSpeed(10);  // Stepper motor speed

  // Set motor control pins as OUTPUT
  pinMode(ML_Ctrl, OUTPUT);
  pinMode(ML_PWM, OUTPUT);
  pinMode(MR_Ctrl, OUTPUT);
  pinMode(MR_PWM, OUTPUT);
  pinMode(ML1_Ctrl, OUTPUT);
  pinMode(ML1_PWM, OUTPUT);
  pinMode(MR1_Ctrl, OUTPUT);
  pinMode(MR1_PWM, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    messageGot = Serial.parseInt();

    switch (messageGot) {
      case 10:
        Serial.println("I got the forward code");
        car_front();
        break;

      case 20:
        Serial.println("I got the backward code");
        car_back();
        break;

      case 30:
        Serial.println("I got the right code");
        car_right();
        break;

      case 40:
        Serial.println("I got the left code");
        car_left();
        break;

      case 50:
        Serial.println("Starting stepper and moisture measurement");
        startStepMotor();
        waterLevel = readSensor();
        Serial.println(String(waterLevel));  // Send moisture value to Pi
        stopStepMotor();
        break;

      case 70:
        Serial.println("Stop command received");
        car_Stop();
        break;
    }
  }
}

// Moisture sensor reading (returns percentage)
float readSensor() {
  int sensor_analog = analogRead(sensorPin);
  float moisture_percentage = 100 - ((sensor_analog / 1023.0) * 100);
  return moisture_percentage;
}

// Stepper motor control
void startStepMotor() {
  motor.step(steps_per_rev); // Rotate forward
}

void stopStepMotor() {
  motor.step(-steps_per_rev); // Rotate backward
}

// Movement functions

void car_front() {
  digitalWrite(ML_Ctrl, HIGH);
  analogWrite(ML_PWM, 180);
  digitalWrite(MR_Ctrl, HIGH);
  analogWrite(MR_PWM, 180);
  digitalWrite(ML1_Ctrl, HIGH);
  analogWrite(ML1_PWM, 178);
  digitalWrite(MR1_Ctrl, HIGH);
  analogWrite(MR1_PWM, 178);
}

void car_back() {
  digitalWrite(ML_Ctrl, LOW);
  analogWrite(ML_PWM, 180);
  digitalWrite(MR_Ctrl, LOW);
  analogWrite(MR_PWM, 180);
  digitalWrite(ML1_Ctrl, LOW);
  analogWrite(ML1_PWM, 178);
  digitalWrite(MR1_Ctrl, LOW);
  analogWrite(MR1_PWM, 178);
}

void car_left() {
  digitalWrite(ML_Ctrl, LOW);
  analogWrite(ML_PWM, 255);
  digitalWrite(MR_Ctrl, HIGH);
  analogWrite(MR_PWM, 255);
  digitalWrite(ML1_Ctrl, LOW);
  analogWrite(ML1_PWM, 255);
  digitalWrite(MR1_Ctrl, HIGH);
  analogWrite(MR1_PWM, 255);
}

void car_right() {
  digitalWrite(ML_Ctrl, HIGH);
  analogWrite(ML_PWM, 255);
  digitalWrite(MR_Ctrl, LOW);
  analogWrite(MR_PWM, 255);
  digitalWrite(ML1_Ctrl, HIGH);
  analogWrite(ML1_PWM, 255);
  digitalWrite(MR1_Ctrl, LOW);
  analogWrite(MR1_PWM, 255);
}

void car_Stop() {
  analogWrite(ML_PWM, 0);
  analogWrite(MR_PWM, 0);
  analogWrite(ML1_PWM, 0);
  analogWrite(MR1_PWM, 0);
}
