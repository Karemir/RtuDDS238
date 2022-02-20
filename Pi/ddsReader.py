
from datetime import datetime
from os import makedirs
from os.path import exists
from random import randint
from time import sleep

outputDir = 'data'
rtuPort = '/dev/ttyS0'
deviceId = 13
pollIntervalSeconds = 1


class RegisterItem:
    def __init__(self, name, value, unit) -> None:
        self.name = name
        self.value = str(value)
        self.unit = unit


def readArduinoTemp(instrument):
    registers = 0  # instrument.read_registers(0, 2)

    return {'h': registers[0], 't': registers[1]}


def readDds238(instrument):
    return None


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

    instrument = 'a'  # modbus instrument
    print('Instrument initialized, begining to poll')

    if (not exists(outputDir)):
        makedirs(outputDir)

    while(True):
        print('Next read')
        data = readTest(instrument)
        writeLineToFile(data)
        sleep(pollIntervalSeconds)


if __name__ == "__main__":
    main()
