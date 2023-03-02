 #include<AFMotor.h>
 AF_DCMotor motor1(1); 
 AF_DCMotor motor2(2);
 AF_DCMotor motor3(3);
 AF_DCMotor motor4(4);
 String readString;
 void setup(){
  Serial.begin(9600);
  motor1.setSpeed(250);
  motor2.setSpeed(250);
  motor3.setSpeed(250);
  motor4.setSpeed(250);
 }
 void loop(){
  while(Serial.available()){
    delay(50);
    char c=Serial.read();
    readString+=c; 
  }
  if(readString.length()>0){
    Serial.println(readString);
    if(readString=="up"){
      motor1.run (FORWARD);
      motor2.run (FORWARD);
      motor3.run (FORWARD);
      motor4.run (FORWARD);
    }
    if(readString=="down"){
      motor1.run (BACKWARD);
      motor2.run (BACKWARD);
      motor3.run (BACKWARD);
      motor4.run (BACKWARD);
    }
    if(readString=="left"){
      motor1.run (BACKWARD);
      motor2.run (FORWARD);
      motor3.run (FORWARD);
      motor4.run (BACKWARD);
    }
    if(readString=="right"){
      motor1.run (FORWARD);
      motor2.run (BACKWARD);
      motor3.run (BACKWARD);
      motor4.run (FORWARD);
    }
    
    if(readString=="center"){
      motor1.run (RELEASE);
      motor2.run (RELEASE);
      motor3.run (RELEASE);
      motor4.run (RELEASE);
    }
    readString="";
  }
 }
