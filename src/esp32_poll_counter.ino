/*
 * src/esp32_poll_counter.ino
 * Optional Hardware Extension (Step 3 Reference):
 * Local physical voting station using ESP32 + Push Buttons
 * Streams live CSV-formatted vote events over USB Serial to Python.
 *
 * Circuit Connections:
 *   Button A (Option 1 - Python)   -> GPIO 4 (with 10K pull-down resistor)
 *   Button B (Option 2 - Power BI) -> GPIO 5 (with 10K pull-down resistor)
 */

const int buttonA = 4;
const int buttonB = 5;
int countA = 0;
int countB = 0;

void setup() {
  Serial.begin(115200);
  pinMode(buttonA, INPUT);
  pinMode(buttonB, INPUT);
  Serial.println("Option,Vote_Count,Status");
}

void loop() {
  if (digitalRead(buttonA) == HIGH) {
    countA++;
    Serial.print("Option A,");
    Serial.print(countA);
    Serial.println(",Option A Vote Recorded");
    delay(300); // Debounce delay
  }
  if (digitalRead(buttonB) == HIGH) {
    countB++;
    Serial.print("Option B,");
    Serial.print(countB);
    Serial.println(",Option B Vote Recorded");
    delay(300); // Debounce delay
  }
}
