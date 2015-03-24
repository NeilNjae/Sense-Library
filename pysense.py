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

    def reset_sense_board(self):
        """resets the sense board, turning all devices off"""
        self.ser.write(COMMAND_HEADER+b'\x10\x00')
        reply=self.ser.read(size=3)
        # global COMMAND_HEADER
        # byte_1 = b'\x10'
        # byte_2 = b'\x00'
        # self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        # reply = binascii.hexlify(self.ser.read(size=3))
        # if os.name == 'nt':
        #     return str(reply, 'ascii')
        # elif os.name == 'posix':
        #     return str(reply)

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
        return [reply[3],reply[4]]
    
    def led_on(self, led_id):
        """ Turns a single L.E.D on, shouldn't return anything
        """
        led_byte = bytes([2**(led_id-1)])
        self.ser.write(COMMAND_HEADER + b'\xC1' + led_byte)
        reply = self.ser.read(size=3)

    def led_off(self, led_id):
        """Turns a single LED off
        """
        led_byte = bytes([2**(led_id-1)])
        self.ser.write(COMMAND_HEADER + b'\xC0' + led_byte)
        reply = self.ser.read(size=3)
    
    def led_multi_on(self, led_id_array):
        """ Turns many LEDs on, as determined by the user's list
        """
        led_id_total = 0
        for i in led_id_array:
            led_id_total+=(2**(i-1))
        led_byte = bytes([led_id_total])
        self.ser.write(COMMAND_HEADER + b'\xC1' + led_byte)
        reply =self.ser.read(size=3)

    def led_multi_off(self, led_id_array):
        """ Turns many LEDs off, as determined by the user's list
        """
        led_id_total = 0
        for i in led_id_array:
            led_id_total+=(2**(i-1))
        led_byte = bytes([led_id_total])
        self.ser.write(COMMAND_HEADER + b'\xC0' + led_byte)
        reply =self.ser.read(size=3)
        # global COMMAND_HEADER
        # led_id_total = 0
        # byte_1 = b'\xC0'
        # for i in led_id_array:
        #     led_id_total+=(2**(i-1))
        # byte_2 = bytes(c_uint8(led_id_total))
        # self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        # reply = binascii.hexlify(self.ser.read(size=3))
        # if os.name == 'nt':
        #     return str(reply, 'ascii')
        # elif os.name == 'posix':
        #     return str(reply)

    def led_change(self,on_array):
        """ Turns a list of LEDs on, the turns the rest off
        """
        a= self.led_multi_on(on_array)
        off_array = [i for i in range(1,8) if i not in on_array]
        # off_array=[]
        # for i in range(1,7):
        #     if i not in on_array:
        #         off_array.append(i)
        b=self.led_multi_off(off_array)
    
    def led_scale(self, value, minvalue=0, maxvalue=100, ledno=7):
        """makes all the LEDs lower than a certain percentage of the number of L.E.D's turn on,
        and the others turn off; often used for volume bars.
        """
        scaled_value = round(((value-minvalue)/(maxvalue-minvalue)) * ledno)
        intarrayon = [i+1 for i in range(ledno) if i < scaled_value]
        # for i in range(ledno):
        #     if i < scaled_value:
        #         intarrayon.append(i+1)
        self.led_change(intarrayon)

    def motor(self,steps,motor_id=0):
        """This turns the motor/stepper a number of steps decided by the user
        
        NOTE TO USERS: numbers 1-128 will turn motor clockwise the appropriate number of steps;
        129-255 will turn motor anticlockwise 256 minus the number of steps stated.
        (e.g 254 = anticlockwise 2 steps, 200 = anticlockwise 56 steps, 100 = clockwise 100 steps)
        """
        byte_1 = bytes([240 + motor_id])
        byte_2 = bytes([steps])
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply = binascii.hexlify(self.ser.read(size=3))
        
    # def stepperMove(self, motor_id, steps):
    #     byte_1 = bytes([240 + motor_id])
    #     byte_2 = bytes([steps])
    #     self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
    #     reply = binascii.hexlify(self.ser.read(size=3))
    #     if os.name == 'nt':
    #         return str(reply, 'ascii')
    #     elif os.name == 'posix':
    #         return str(reply)
        

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
                    if self.ping() == [4,96]: #'55ffaa0460':
                        print ("Opening Serial port...")
                        time.sleep(2)
                        print ("Connected to sense at port: " + self.ser.name)
                        break
                    else:
                        self.ser.close()

                except serial.SerialException:
                    pass
                



