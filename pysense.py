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
READINGS={"slider":0,"infrared":0,"microphone":0,"button":0,"input_a":0,"input_b":0,"input_c":0,"input_d":0}
LIST=["slider","infrared","microphone","button","input_a","input_b","input_c","input_d"]
#motor directions
CLOCKWISE = 0
ANTICLOCKWISE = 1
#header
COMMAND_HEADER = b'\x54\xFE'
ready_to_interpret=threading.Event()
buffer_list=[]
#class for contolling 1 senseboard
class PySense(object):

    def message_reciever(self):
        reader.run()
        interpreter.run()

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
        return [reply[3],reply[4]]
    
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
        return READINGS[LIST[sensor_id]]
    
    #all functions that use burst mode to read sensors here...
    def slider():
        return READINGS["slider"]
    def infrared():
        return READINGS["infrared"]
    def button():
        return READINGS["button"]
    def microphone():
        return READINGS["microphone"]
    def input_a():
        return READINGS["input_a"]
    def input_b():
        return READINGS["input_b"]
    def input_c():
        return READINGS["input_c"]
    def input_d():
        return READINGS["input_d"]

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
        byte_2 = bytes([sensor_id_total_0_to_7])
        self.ser.write(COMMAND_HEADER + byte_1 + byte_2)
        reply_1 = binascii.hexlify(self.ser.read(size=3))
        byte_1 = b'\xA1'
        byte_2 = bytes([sensor_id_total_8_to_15])
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

    def reading_senseboard(self):
        """This function gives interpret_senseboard data from the senseboard
        """
        while True:
            sensor_bursts.put(self.ser.read(size=1))
            ready_to_interpret.set()

    def interpret_senseboard_II(buffer_list):
        """This removes any junk bytes at the beginning of buffer_list and 
        responds to a legitimate reading that is picked up.
        """
        while buffer_list and buffer_list[0] != 85 and buffer_list[0] != 12:#removes invalid bytes
            buffer_list.remove(buffer_list[0:1])
        if len(buffer_list)>=3 and buffer_list[0]==85 and buffer_list[1]==255 and buffer_list[2]==170:#ack removal
            for i in range(3):
                buffer_list.remove(buffer_list[i:i+1])
            return False
        elif len(buffer_list)>=3 and buffer_list[0]==12:#burst reciever
            READINGS[LIST[round((buffer_list[1]&240)/16)]]=(buffer_list[1]&3)*256+buffer_list[2]
            for i in range(3):
                buffer_list.remove(buffer_list[i:i+1])
            return False
        elif len(buffer_list)>=2 and buffer_list[1] != 255:#anti-glitch code...
            buffer_list.remove(buffer_list[0:1])
            return False
        elif len(buffer_list)>=4 and buffer_list[0]==85 and buffer_list[1]==255:#sensor reader
            READINGS[LIST[round((buffer_list[2]&240)/16)]]=(buffer_list[2]&3)*256+buffer_list[3]
            for i in range(4):
                buffer_list.remove(buffer_list[i:i+1])
                return False
        else:
            return True

    def interpret_senseboard(self):
        """This collects data from a queue and sends it to interpret_senseboard_II, it also
        puts the thread to sleep (temporarily!) when it can't make a valid reading AND there
        aren't any junk bytes to remove.
        """
        while True:
            ready_to_interpret.wait()
            while not sensor_bursts.empty():
                buffer_list.append(sensor_bursts.get())
            read_all=False

            while not read_all:
                if buffer_list:
                    read_all=interpret_senseboard_II(buffer_list)
                else:
                    read_all=True
            ready_to_interpret.clear()
            
    def __init__(self):
        self.sensor_bursts=queue.Queue()
        self.ser = serial.Serial()
        self.burst_length = 0
        self.reader=threading.Thread(target=self.reading_senseboard)
        self.interpreter=threading.Thread(target=self.interpret_senseboard)

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
                



