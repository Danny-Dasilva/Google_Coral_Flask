import serial
port = "/dev/ttyACM0"
baudRate = 9600
ser = serial.Serial(port=port, baudrate=baudRate)
while True:
    current_reading = ""

    while True:
        token = ser.read()
        if(token == b'/'):
            current_reading = int(current_reading)
            break
        else:
            current_reading = current_reading + token.decode("utf-8")
    print(current_reading)
