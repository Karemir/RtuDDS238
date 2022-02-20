#include <ModbusSlave.h>
#include "DHT.h"

#define DHTPIN 3 // Digital pin connected to the DHT sensor

Modbus slave(Serial1, 13); // stream = Serial, slave id = 13
DHT dht(DHTPIN, DHT11);

uint16_t sensorRegister[2] = {0, 0};

void setup()
{
    dht.begin();
    slave.cbVector[FC_READ_HOLDING_REGISTERS] = handleReadHoldingRegs; // FC = 3

    Serial.begin(9600);
    Serial.println(F("Starting thermometer"));

    Serial1.begin(9600);
}

long lastUpdate = 0;
void loop()
{
    if (lastUpdate + 2000 < millis())
    {
        Serial.println("updating DHT");
        // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
        float h = dht.readHumidity();
        float t = dht.readTemperature();
        Serial.println(h);
        Serial.println(t);

        if (isnan(h) || isnan(t))
        {
            Serial.println(F("Failed to read from DHT sensor!"));
            return;
        }

        lastUpdate = millis();

        sensorRegister[0] = h * 100;
        sensorRegister[1] = t * 100;
    }

    slave.poll();

    // useful for debugging RS, write or read anything to the wire.
    // int incomingByte = 0;
    // delay(100);
    /*if (Serial1.available() > 0) {
      // read the incoming byte:
      incomingByte = Serial1.read();

      // say what you got:
      Serial.print("I received: ");
      Serial.println(incomingByte, HEX);
    } else {
      Serial1.write('a');
    }*/
}

uint8_t handleReadHoldingRegs(uint8_t fc, uint16_t address, uint16_t length)
{
    if (length > 2)
    {
        return STATUS_ILLEGAL_DATA_ADDRESS;
    }

    for (int i = 0; i < length; i++)
    {
        slave.writeRegisterToBuffer(i, sensorRegister[address + i]);
    }
    return STATUS_OK;
}