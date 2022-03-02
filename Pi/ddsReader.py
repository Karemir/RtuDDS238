#!/usr/bin/python3

from datetime import datetime
from os import makedirs
from os.path import exists
from random import randint
from time import sleep
from struct import *

import minimalmodbus
import serial

outputDir = 'data'
rtuPort = '/dev/ttyS0'
deviceId = 1
pollIntervalSeconds = 1
serialBaudrate = 9600
serialTimeout = 1.3  # seconds


class RegisterItem:
    def __init__(self, name, value, unit) -> None:
        self.name = name
        self.value = str(value)
        self.unit = unit


def readArduinoTemp(instrument):
    registers = instrument.read_registers(0, 2, functioncode=4)

    return [
        RegisterItem('Humidity', registers[0] / 100.0, '%'),
        RegisterItem('temperature', registers[1] / 100.0, 'C')
    ]


def regToUnsigned32(registers, startIdx):
    s = pack('>HH', registers[startIdx], registers[startIdx+1])
    return unpack('>L', s)[0]


def regToSigned16(registers, index):
    s = pack('>H', registers[index])
    return unpack('>h', s)[0]


def readDds238(instrument):
    registers = instrument.read_reagisters(0, 18)

    return [
        RegisterItem('total energy',
                     regToUnsigned32(registers, 0) * 0.01, 'kWh'),
        RegisterItem('export energy',
                     regToUnsigned32(registers, 8) * 0.01, 'kWh'),
        RegisterItem('import energy',
                     regToUnsigned32(registers, 10) * 0.01, 'kWh'),
        RegisterItem('voltage',
                     registers[12] * 0.1, 'V'),
        RegisterItem('current',
                     registers[13] * 0.01, 'A'),
        RegisterItem('active power',
                     regToSigned16(registers, 14), 'W'),
        RegisterItem('reactive power',
                     registers[15], 'VAr'),
        RegisterItem('power factor',
                     registers[16] * 0.001, 'Scale'),
        RegisterItem('frequency',
                     registers[17] * 0.01, 'Hz'),
    ]


def readTest(instrument):
    return [
        RegisterItem('Humidity', randint(10, 99), '%'),
        RegisterItem('temperature', randint(0, 20), 'C')
    ]


def writeLineToFile(data):
    now = datetime.now()
    todayStr = now.strftime("%d_%m_%Y")
    stamp = now.strftime("%H-%M-%S")

    headers = list(map(lambda x: '{}({})'.format(x.name, x.unit), data))
    values = list(map(lambda x: x.value, data))

    headers.insert(0, 'timestamp')
    values.insert(0, stamp)

    path = '{}/{}.csv'.format(outputDir, todayStr)

    try:
        if (exists(path)):
            with open(path, "a") as datafile:
                datafile.write(','.join(values) + '\n')
        else:
            with open(path, "w") as datafile:
                datafile.write(','.join(headers) + '\n')
                datafile.write(','.join(values) + '\n')

    except Exception as e:
        print(e)
        pass

    return


def main():
    print('Starting RTU reader...')
    print('Config:')
    print('- output dir: ', outputDir)
    print('- polling: ', pollIntervalSeconds)
    print('- rtuPort: ', rtuPort)
    print('- deviceId: ', deviceId)

    instrument = minimalmodbus.Instrument(rtuPort, deviceId)
    instrument.serial.baudrate = serialBaudrate
    instrument.serial.timeout = serialTimeout
    instrument.serial.bytesize = 8
    instrument.serial.parity = serial.PARITY_NONE
    instrument.serial.stopbit = 1

    print('Instrument initialized, begining to poll')

    if (not exists(outputDir)):
        makedirs(outputDir)

    while(True):
        sleep(pollIntervalSeconds)
        print('Next read')
        try:
            data = readDds238(instrument)  # readArduinoTemp(instrument)
            writeLineToFile(data)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    main()
