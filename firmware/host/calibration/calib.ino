//firmware/host/calibration/calib.ino
void setup() {
  Serial.begin(115200);
  pinMode(7, INPUT);
}

void loop() {
  // HIGH→LOW の開始を待つ
  while (digitalRead(7) == HIGH);
  unsigned long t0 = micros();  // HIGH→LOW の開始

  // LOW→HIGH の終了を待つ
  while (digitalRead(7) == LOW);
  while (digitalRead(7) == HIGH);
  unsigned long t1 = micros();  // LOW→HIGH の終了

  float period_sec = (t1 - t0) / 1e6;

  Serial.print("PERIOD:");
  Serial.println(period_sec);

  delay(200);
}

