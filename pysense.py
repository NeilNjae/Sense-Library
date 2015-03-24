import serial, time, binascii, os, glob
from ctypes import c_uint8

#sensor ids
SLIDER = 0
INFRARED = 1
MICROPHONE = 2
BUTTON = 3
INPUT_A = 4
INPUT_B = 5
INPUT_C = 6
INPUT_D = 7

#motor directions
CLOCKWISE = 0
ANTICLOCKWISE = 1

#header
COMMAND_HEADER = b'\x54\xFE'

#class for contolling 1 senseboard
class PySense(object):
    
    ser = serial.Serial()
    burst_length = 0

    def scanWindows(self):
        available = []
        for i in range(256):
            try:
                s = serial.Serial(i)
                available.append( [i, s.portstr] )
                s.close()
            except serial.SerialException:
                pass

        return available
        
    def scanPosix(self):
        """scan for available ports. return a list of device names."""
        return glob.glob('/dev/ttyS*') + glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*')

    def resetSenseBoard(self):
        global COMMAND_HEADER
        byte_1 = b'\x10'
        byte_2 = b'\x00'
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply = binascii.hexlify(self.ser.read(size=3))
        if os.name == 'nt':
            return str(reply, 'ascii')
        elif os.name == 'posix':
            return str(reply)

    # def pingSenseBoard(self):
    #     global COMMAND_HEADER
    #     byte_1 = b'\x00'
    #     byte_2 = b'\x00'
    #     self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
    #     reply = binascii.hexlify(self.ser.read(size=5))
    #     if os.name == 'nt':
    #         return str(reply, 'ascii')
    #     elif os.name == 'posix':
    #         return str(reply)
    def ping(self):
        """Pings the sensboard and returns firmware version number
        and board revision number.
        """
        self.ser.write(COMMAND_HEADER+b'\x00'+b'\x00')
        reply=self.ser.read(size=5)
        reply[3],reply[4]
    
    def led_on(self, led_id):
        """ Turns a single L.E.D on, shouldn't return anything
        """
        led_byte = bytes([2**(led_id-1)])
        self.ser.write(COMMAND_HEADER + b'\xC1' + led_byte)
        reply = self.ser.read(size=3)

    def led_off(self, led_id):
        led_byte = bytes([2**(led_id-1)])
        self.ser.write(COMMAND_HEADER + b'\xC0' + led_byte)
        reply = binascii.hexlify(self.ser.read(size=3))
    
    def ledMultiOn(self, led_id_array):
        global COMMAND_HEADER
        led_id_total = 0
        byte_1 = b'\xC1'
        for i in led_id_array:
            led_id_total+=(2**(i-1))
        byte_2 = bytes(c_uint8(led_id_total))
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply = binascii.hexlify(self.ser.read(size=3))
        if os.name == 'nt':
            return str(reply, 'ascii')
        elif os.name == 'posix':
            return str(reply)

    def ledMultiOff(self, led_id_array):
        global COMMAND_HEADER
        led_id_total = 0
        byte_1 = b'\xC0'
        for i in led_id_array:
            led_id_total+=(2**(i-1))
        byte_2 = bytes(c_uint8(led_id_total))
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply = binascii.hexlify(self.ser.read(size=3))
        if os.name == 'nt':
            return str(reply, 'ascii')
        elif os.name == 'posix':
            return str(reply)
    
    def scaleLEDs(self, minvalue, maxvalue, value, ledno):
        AMOUNT = round(((value-minvalue)/(maxvalue-minvalue)) * ledno)
        intarrayon = []
        intarrayoff = []

        for i in range(0, ledno, 1):
            if(i < AMOUNT):
                intarrayon.append(i+1)
            else:
                intarrayoff.append(i+1)

        self.ledMultiOn(intarrayon)
        self.ledMultiOff(intarrayoff)
        

    def stepperMove(self, motor_id, steps):
        global COMMAND_HEADER
        byte_1 = bytes(c_uint8(240 + motor_id))
        byte_2 = bytes(c_uint8(steps))
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply = binascii.hexlify(self.ser.read(size=3))
        if os.name == 'nt':
            return str(reply, 'ascii')
        elif os.name == 'posix':
            return str(reply)
        

    def servoSetPosition(self, servo_id, angle):
        global COMMAND_HEADER
        byte_1 = bytes(c_uint8(208+ servo_id))
        byte_2 = bytes(c_uint8(angle))
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply = binascii.hexlify(self.ser.read(size=3))
        if os.name == 'nt':
            return str(reply, 'ascii')
        elif os.name == 'posix':
            return str(reply)

    def dcMove(self, motor_id, direction, speed):
        global COMMAND_HEADER
        byte_1 = bytes(c_uint8( 128 + direction ))
        byte_2 = bytes(c_uint8(speed*32 + motor_id))
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply = binascii.hexlify(self.ser.read(size=3))
        if os.name == 'nt':
            return str(reply, 'ascii')
        elif os.name == 'posix':
            return str(reply)
        

    def dcOff(self, motor_id):
        global COMMAND_HEADER
        byte_1 = '\x80'
        byte_2 = bytes(c_uint8(motor_id))
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply = binascii.hexlify(self.ser.read(size=3))
        if os.name == 'nt':
            return str(reply, 'ascii')
        elif os.name == 'posix':
            return str(reply)

    def readSensor(self, sensor_id):
        global COMMAND_HEADER
        byte_1 = bytes(c_uint8(32 + sensor_id))
        byte_2 = b'\x00'
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply=binascii.hexlify(self.ser.read(size=4))
        if os.name == 'nt':
            string_reply = str(reply, 'ascii')
        elif os.name == 'posix':
            string_reply = str(reply)
        return int(string_reply[5:], 16)

    def burstModeSet(self, sensor_id_array):
        global COMMAND_HEADER
        sensor_id_total_0_to_7 = 0
        sensor_id_total_8_to_15 = 0
        for i in sensor_id_array:
            if i <= 7:
                sensor_id_total_0_to_7 += 2**i

            if i >7:
                sensor_id_total_8_to_15 += 2**i


        byte_1 = b'\xA0'
        byte_2 = bytes(c_uint8(sensor_id_total_0_to_7))
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply_1 = binascii.hexlify(self.ser.read(size=3))
        byte_1 = b'\xA1'
        byte_2 = bytes(c_uint8(sensor_id_total_8_to_15))
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply_2 = binascii.hexlify(self.ser.read(size=3))
        self.burst_length = len(sensor_id_array)
        if reply_1 == reply_2:
            if os.name == 'nt':
                return str(reply_1, 'ascii')
            elif os.name == 'posix':
                return str(reply_1)
        



    def burstModeOffAll(self):
        global COMMAND_HEADER
        byte_1 = b'\xA0'
        byte_2 = b'\x00'
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply_1 = binascii.hexlify(self.ser.read(size=3))
        byte_1 = b'\xA1'
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply_2 = binascii.hexlify(self.ser.read(size=3))
        if reply_1 == reply_2:
            if os.name == 'nt':
                return str(reply_1, 'ascii')
            elif os.name == 'posix':
                return str(reply_1)
            
        

    def readBursts(self):
        burst_response = binascii.hexlify(self.ser.read(size=3*self.burst_length))
        if os.name == 'nt':
            return str(burst_repsonse, 'ascii')
        elif os.name == 'posix':
            return str(burst_response)

    def __init__(self):
        if os.name == 'nt':
            for com in self.scanWindows():
                self.ser = serial.Serial(int(com[0]), 115200, timeout=1)
                time.sleep(2)
                if self.pingSenseBoard() == '55ffaa0460':
                    print ("Opening Serial port...")
                    time.sleep(2)
                    print ("Connected to sense at port: " + self.ser.name)
                    break
                else:
                    self.ser.close()
            
        elif os.name == 'posix':
            for com in self.scanPosix():
                try:
                    self.ser = serial.Serial(com, 115200, timeout=1)
                    print ("trying to connect to " + str(com))
                    time.sleep(2)
                    if self.pingSenseBoard() == "b'55ffaa0460'": #'55ffaa0460':
                        print ("Opening Serial port...")
                        time.sleep(2)
                        print ("Connected to sense at port: " + self.ser.name)
                        break
                    else:
                        self.ser.close()

                except serial.SerialException:
                    pass
                



