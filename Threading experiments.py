self.sensor_bursts=queue.Queue()
self.READINGS={"slider":0,"infrared":0,"microphone":0,"button":0,"input_a":0,"input_b":0,"input_c":0,"input_d":0}
self.LIST=["slider","infrared","microphone","button","input_a","input_b","input_c","input_d"]
self.ser = serial.Serial()
self.burst_length = 0
self.ready_to_interpret=threading.Event()
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
            self.ser = serial.Serial(com, 115200, timeout=None)
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
                
print("Threads starting")
self.reader=threading.Thread(target=self.reading_senseboard(),daemon=True)
self.reader.start()
# self.interpreter=threading.Thread(target=self.interpret_senseboard())
print("Threads started")