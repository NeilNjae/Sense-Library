import pysense
#import threading
#import serial
#import time
# ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=None)

# # senseboard = pysense.PySense()
# def reading_senseboard():
#     """This function gives interpret_senseboard data from the senseboard
#     """
       
#     while True:
#         print("Waiting for Senseboard")
#         byte_read = ser.read(size=1)
#         print("Read", byte_read)
#         #self.sensor_bursts.put(byte_read)
#         #self.ready_to_interpret.set()

# def silly():
# 	for i in range(10):
# 		print(i)
# 		time.sleep(0.5)

senseboard = pysense.PySense()

# print("Threads starting")
# reader=threading.Thread(target=reading_senseboard, daemon=True)
# reader.start()
# st=threading.Thread(target=silly, daemon=True)
# st.start()
# print("Threads started")


finished = False

while not finished:
	command_line = input("> ").split()
	if command_line[0] == 'l':
		if command_line[2] == '0':
			senseboard.led_off(int(command_line[1]))
		else:
			senseboard.led_on(int(command_line[1]))
	elif command_line[0] == 'r':
		senseboard.read_sensor(int(command_line[1]))
	elif command_line[0] == 's':
		sv = senseboard.sensor_value(int(command_line[1]))
		print(sv)
	elif command_line[0] == 'q':
		finished = True