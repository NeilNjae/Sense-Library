import serial, time, binascii, os, glob, queue, threading

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

REPLY_HEADER = b'\x55\xFF'
REPLY_ACK = b'\x55\xFF\xAA'
BURST_HEADER = b'\x0C'

#class for contolling 1 senseboard
class PySense(object):

    connected_ports = []

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
        if len(reply) >= 5:
            return [reply[3],reply[4]]
        else:
            return [0, 0]
    
    def led_on(self, led_id):
        """ Turns a single L.E.D on, shouldn't return anything
        """
        led_byte = bytes([2**(led_id-1)])
        self.ser.write(COMMAND_HEADER + b'\xC1' + led_byte)

    def led_off(self, led_id):
        """Turns a single LED off
        """
        led_byte = bytes([2**(led_id-1)])
        self.ser.write(COMMAND_HEADER + b'\xC0' + led_byte)
    
    def led_multi_on(self, led_id_array):
        """ Turns many LEDs on, as determined by the user's list
        """
        led_id_total = 0
        for i in led_id_array:
            led_id_total+=(2**(i-1))
        led_byte = bytes([led_id_total])
        self.ser.write(COMMAND_HEADER + b'\xC1' + led_byte)

    def led_multi_off(self, led_id_array):
        """ Turns many LEDs off, as determined by the user's list
        """
        led_id_total = 0
        for i in led_id_array:
            led_id_total+=(2**(i-1))
        led_byte = bytes([led_id_total])
        self.ser.write(COMMAND_HEADER + b'\xC0' + led_byte)
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
        byte_1 = bytes([208+ servo_id])
        byte_2 = bytes([angle])
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)

    def dc_move(self, motor_id, speed, direction):
        """ makes the motor move at a pre set speed and direction
        0=clockwise, 1=anticlockwise
        """
        dir_byte = bytes([128 + direction])
        speed_byte = bytes([speed*32 + motor_id])
        self.ser.write(COMMAND_HEADER + dir_byte + speed_byte)

    def dc_off(self, motor_id):
        """ turns a motor off
        """
        off_motor = bytes([motor_id])
        self.ser.write(COMMAND_HEADER + '\x80' + off_motor)

    def read_sensor(self, sensor_id):
        """ Shows whether a sensor is configured[0] or not[1] 
        and the reading of a sensor, on a scale of 0-1023
        """
        byte_1 = bytes([32 + sensor_id])
        self.ser.write(COMMAND_HEADER + byte_1 + b'\x00')
        # return self.READINGS[sensor_id]

    def sensor_value(self, sensor_id):
        return self.READINGS[sensor_id]
 
    def burstModeSet(self, sensor_id_array):
        """After being given a list of numbers, it puts those sensors  on burst mode!!
        """
        # global COMMAND_HEADER
        sensor_id_total_0_to_7 = 0
        sensor_id_total_8_to_15 = 0
        for i in sensor_id_array:
            if i <= 7:
                sensor_id_total_0_to_7 += 2**i

            if i >7:
                sensor_id_total_8_to_15 += 2**i


        byte_1 = b'\xA0'
        byte_2 = bytes([sensor_id_total_0_to_7])
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        byte_1 = b'\xA1'
        byte_2 = bytes([sensor_id_total_8_to_15])
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        self.burst_length = len(sensor_id_array)
        
    def burstModeOffAll(self):
        """Turns burst mode off
        """
        self.ser.write(COMMAND_HEADER + b'\xA0\x00')
        self.ser.write(COMMAND_HEADER + b'\xA1\x00')
        
    def reading_senseboard(self):
        """This function gives interpret_senseboard data from the senseboard
        """
        while True:
            # print("Waiting for Senseboard")
            byte_read = self.ser.read(size=1)
            # print("Read", byte_read)
            self.sensor_bursts.put(byte_read)

    def interpret_senseboard_II(self):
        """This removes any junk bytes at the beginning of buffer_list and 
        responds to a legitimate reading that is picked up.
        """
        while self.buffer_list and (self.buffer_list[0] != REPLY_HEADER[0] and self.buffer_list[0] != BURST_HEADER[0]):#removes invalid bytes
            # print("Dropping first byte with value", self.buffer_list[0], self.buffer_list[0] != REPLY_HEADER[0])
            self.buffer_list = self.buffer_list[1:]
        if self.buffer_list[:3] == [85, 255, 170]:#ack removal
            #print("Ack removed")
            self.buffer_list = self.buffer_list[3:]
            return False
        elif len(self.buffer_list)>=3 and self.buffer_list[0]==BURST_HEADER[0]:#burst reciever
            sn = round((self.buffer_list[1]&240)/16)
            sv = (self.buffer_list[1]&3)*256+self.buffer_list[2]
           # print("recieved a burst: sensor", sn, "Value", sv)
            self.READINGS[sn] = sv
            #self.READINGS[[round((self.buffer_list[1]&240)/16)]]=(self.buffer_list[1]&3)*256+self.buffer_list[2]
            self.buffer_list = self.buffer_list[3:]
        elif len(self.buffer_list)>=2 and self.buffer_list[0] == REPLY_HEADER[0] and self.buffer_list[1] != REPLY_HEADER[1]:#anti-glitch code...
            self.buffer_list = self.buffer_list[1:]
            return False
        elif len(self.buffer_list)>=4 and self.buffer_list[0]==85 and self.buffer_list[1]==255:#sensor reader
            sensor_id =round((self.buffer_list[2]&240)/16)
            sensor_value =(self.buffer_list[2]&3)*256+self.buffer_list[3]
            #print("the reading for",sensor_id, "is now", sensor_value)
            self.READINGS[sensor_id] = sensor_value

            # self.READINGS[round((self.buffer_list[2]&240)/16)]=(self.buffer_list[2]&3)*256+self.buffer_list[3]
            self.buffer_list = self.buffer_list[4:]
        else:
            return True

    def interpret_senseboard(self):
        """This collects data from a queue and sends it to interpret_senseboard_II, it also
        puts the thread to sleep (temporarily!) when it can't make a valid reading AND there
        aren't any junk bytes to remove.
        """
        while True:
            #print("waiting for data")
            bytes_read = self.sensor_bursts.get()
            for b in bytes_read:
                self.buffer_list.append(b)
            #self.buffer_list.append(self.sensor_bursts.get())
            #print("found data")
            read_all=False
            while not read_all:
             #   print("Starting interpretation")
                if self.buffer_list:
              #      print("Interpreting buffer of", len(self.buffer_list), "bytes")
                    read_all=self.interpret_senseboard_II()
                else:
               #     print("Buffer empty")
                    read_all=True
            
    def __init__(self):
        self.sensor_bursts=queue.Queue()
        self.READINGS={0:0, 1:0, 2:0, 3:0,4:0,5:0,6:0,7:0}
        self.ser = serial.Serial()
        self.burst_length = 0
        self.buffer_list=[]

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
                    # skip if com is in connected ports
                    if com not in self.__class__.connected_ports:
                        self.ser = serial.Serial(com, 115200, timeout=None)
                        print ("trying to connect to " + str(com))
                        time.sleep(2)
                        if self.ping() == [4,96]: #'55ffaa0460':
                            print ("Opening Serial port...")
                            time.sleep(2)
                            print ("Connected to sense at port: " + self.ser.name)
                            # update connected ports
                            self.__class__.connected_ports.append(com)
                            break
                        else:
                            self.ser.close()

                except serial.SerialException:
                    pass
                
        print("Threads starting")
        self.reader=threading.Thread(target=self.reading_senseboard, daemon=True)
        self.interpreter=threading.Thread(target=self.interpret_senseboard, daemon=True)
        self.reader.start()
        self.interpreter.start()
        print("Threads started")