#include "WiFi.h"
#include "AsyncUDP.h"

const char* ssid = "";
const char* pass = "";
const int relay = 26;
int count = 1;

AsyncUDP udp;

void setup()
{
  Serial.begin(115200);
  pinMode(relay, OUTPUT);
  //turn it off
  digitalWrite(relay, HIGH);
  WiFi.disconnect(true);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);
  Serial.println(WiFi.macAddress());
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print("connecting...");
  }
  if (udp.listen(7)) {
    Serial.print(" ");
    Serial.print("UDP Listening on IP: ");
    Serial.println(WiFi.localIP());
    udp.onPacket([](AsyncUDPPacket packet) {
      Serial.print("UDP Packet Type: ");
      Serial.print(packet.isBroadcast() ? "Broadcast" : packet.isMulticast() ? "Multicast" : "Unicast");
      Serial.print(", From: ");
      Serial.print(packet.remoteIP());
      Serial.print(":");
      Serial.print(packet.remotePort());
      Serial.print(", To: ");
      Serial.print(packet.localIP());
      Serial.print(":");
      Serial.print(packet.localPort());
      Serial.print(", Length: ");
      Serial.print(packet.length()); 
      Serial.print(", Data: ");
      Serial.write(packet.data(), packet.length());
      Serial.println();
      String myString = (const char*)packet.data();
      packet.printf("Got %u bytes of data", packet.length());

      //Normal mode
      if (packet.length() == 102)
      {
        if(count % 2 != 0)
        {
        digitalWrite(relay, LOW);
        }
        else
        {
          digitalWrite(relay, HIGH);
        }
        count++;
      } 

      //Latch mode
      if (packet.length() == 96) {
        digitalWrite(relay,LOW);
        delay(1000);
        digitalWrite(relay,HIGH);
      } 
      
    });
  }
}

void loop()
{
  delay(1000);
  udp.broadcast("Anyone here?");
}