#include <Servo.h>
#include <Wire.h>
#include <Arduino.h>
Servo xservo;
Servo yservo;
Servo zservo;

int R = 3;
int G = 6;
int B = 5;

int flaghappy = false;
int flagsad = false;
int flagangry = false;
int flagneutral = false;
int flagsurprised = false;

int x = 60;
int y = 98;
int z = 90;

int previousx = 0;
int previousy = 0;
int previousz = 0;

int newx = 0;
int newy = 0;
int newz = 0;

unsigned long previousMillis = 0;
unsigned long currentMillis = 0;
int interval2 = 50;
int interval = 1000;

String jetson_msg = "";

void setup() {
  // put your setup code here, to run once:
  xservo.attach(8);
  yservo.attach(12);
  zservo.attach(13);

  xservo.write(x);
  yservo.write(y);
  zservo.write(z);

  newx = random(35, 60);
  newy = random(78, 120);
  newz = random(55, 105);

  pinMode(R, OUTPUT);// Red from RGB led
  pinMode(G, OUTPUT);// Green from RGB led
  pinMode(B, OUTPUT);// Blue from RGB led

  Serial.begin(250000);
  /*
    Serial.println();
    Serial.println(F("DFRobot DFPlayer Mini Demo"));
    Serial.println(F("Initializing DFPlayer ... (May take 3~5 seconds)"));
  */
  

  randomSeed(analogRead(A3));
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    jetson_msg = Serial.readStringUntil('/');

    int star_index = jetson_msg.indexOf("*");
    jetson_msg.remove(0, star_index + 1);

    Serial.println(jetson_msg);
  }
  currentMillis = millis();

  previousx = x;
  previousy = y;
  previousz = z;

  if (jetson_msg == "stop") {
    //Serial.println("Stop");
  }
  else if (jetson_msg == "left") {
    //left
    //Serial.println("left");
    z++;
  }
  else if (jetson_msg == "right") {
    //right
    //Serial.println("right");
    z--;
  }
  else if (jetson_msg == "up") {
    //up
    //Serial.println("up");
    x--;
  }
  else if (jetson_msg == "down") {
    //down
    //Serial.println("down");
    x++;
  }

  else if (jetson_msg == "free-roam") {
    digitalWrite(R, 0);
    digitalWrite(G, 0);
    digitalWrite(B, 0);
    //free-roam
    //Serial.println("free-roam");
    if (currentMillis - previousMillis >= interval2) {
      if (previousx != newx) {
        if (previousx < newx) {
          x++;
        }
        else if (previousx > newx) {
          x--;
        }
      }
      else {
        newx = random(35, 60);
      }

      if (previousy != newy) {
        if (previousy < newy) {
          //y++;
        }
        else if (previousy > newy) {
          //y--;
        }
      }
      else {
        newy = random(60, 70);
      }

      if (previousz != newz) {
        if (previousz < newz) {
          z++;
        }
        else if (previousz > newz) {
          z--;
        }
      }
      else {
        newz = random(30, 150);
      }

      previousx = x;
      previousy = y;
      previousz = z;
      previousMillis = currentMillis;
    }
  }
  else if (jetson_msg == "home") {
    digitalWrite(R, 0);
    digitalWrite(G, 0);
    digitalWrite(B, 0);
    //home
    //Serial.println("home");
    x = 60;
    y = 98;
    z = 90;
  }

  if (x >= 65) {
    x = 65;
  }
  else if (x <= 35) {
    x = 35;
  }

  if (y >= 120) {
    y = 120;
  }
  else if (y <= 78) {
    y = 78;
  }
  if (z >= 179) {
    z = 179;
  }
  else if (z <= 0) {
    z = 0;
  }
  //  Serial.print("X: ");
  //  Serial.print(x);
  //  Serial.print(" / ");
  //  Serial.print("Y: ");
  //  Serial.print(y);
  //  Serial.print(" / ");
  //  Serial.print("Z: ");
  //  Serial.println(z);
  //delay(10);
  xservo.write(x);
  yservo.write(y);
  zservo.write(z);
  //delay(1);

  if (jetson_msg == "low-conf") // Face detected but low confidence
  {
    flaghappy = false;
    flagangry = false;
    flagneutral = false;
    flagsad = false;
    flagsurprised = false;
    digitalWrite(R, 0);
    digitalWrite(G, 0);
    digitalWrite(B, 0);
  }

  if (jetson_msg == "happy") //HAPPY FACE
  {
    digitalWrite(R, 255);
    digitalWrite(G, 255);
    digitalWrite(B, 0);
    //Serial.println("HAPPY");
    // YELLOW COLOR//
    flagangry = false;
    flagneutral = false;
    flagsad = false;
    flagsurprised = false;

  }

  if (jetson_msg == "sad") //SAD FACE
  {
    digitalWrite(R, 0);
    digitalWrite(G, 0);
    digitalWrite(B, 255);
    //Serial.println("SAD");
    // BLUE COLOR//
    flaghappy = false;
    flagangry = false;
    flagneutral = false;
    flagsurprised = false;

  }

  if (jetson_msg == "angry") //ANGRY FACE
  {
    digitalWrite(R, 255);
    digitalWrite(G, 0);
    digitalWrite(B, 0);
    //Serial.println("ANGRY");
    // RED COLOR//
    flaghappy = false;
    flagneutral = false;
    flagsad = false;
    flagsurprised = false;

  }

  if (jetson_msg == "neutral") //NEUTRAL FACE
  {
    digitalWrite(R, 255);
    digitalWrite(G, 255);
    digitalWrite(B, 255);
    //Serial.println("NEUTRAL");
    // WHITE COLOR//
    flaghappy = false;
    flagangry = false;
    flagsad = false;
    flagsurprised = false;

  }

  if (jetson_msg == "surprised") //SURPRISED FACE
  {
    digitalWrite(R, 255);
    digitalWrite(G, 0);
    digitalWrite(B, 255);
    // YELLOW COLOR//
    flaghappy = false;
    flagangry = false;
    flagneutral = false;
    flagsad = false;

  }
  if (jetson_msg != "free-roam") {
    jetson_msg = "";
  }
}
