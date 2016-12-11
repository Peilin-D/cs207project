from timeseries.ArrayTimeSeries import ArrayTimeSeries
from timeseries.TimeSeries import TimeSeries
import numpy as np
import json

from socket import *
import threading
import pickle
from _thread import *
from timeseries.FileStorageManager import FileStorageManager
from simsearch.Globals import NUM_TS_DATA
import os

def clientThread(conn, sm):
	
	while True:
	#    conn.send("Server waiting for input:".encode())
		rec = conn.recv(1024)
		if not rec:
			break
		print("Server received:",rec)
		receivedData = pickle.loads(rec)
		if receivedData['cmd'] == "BYID":
			# Get ts storage using id received
			print("RECEVIED ID",receivedData['id']," TYPE:",type(receivedData['id']))
			ts = sm.get(receivedData['id'])
			toSend = {"time":list(ts.times()),"value":list(ts.values()),"id":receivedData['id']}
			conn.send(pickle.dumps(toSend))

		elif receivedData['cmd'] == 'ADDTS':
			# Save to storage manager
			id, time, value = receivedData['id'], receivedData['time'], receivedData['value']
			sm.store(id, ArrayTimeSeries(input_time=time, input_value=value))
			conn.send(pickle.dumps("Saved to DB!"))
		
	conn.close()

if __name__ == "__main__":
	# store 1000 randomly generated ts data from simsearch/ if necessary
	StorageManager = FileStorageManager()
	if len(os.listdir('sm_data/')) == 0:
		print('Loading Data')
		for id in range(NUM_TS_DATA):
			cur_ts = pickle.load(open('simsearch/ts_data/ts_%d.dat'%id, 'rb'))
			StorageManager.store(id, cur_ts)
	else:
		print('Data Already Loaded')
		
	StorageManager.store(1000,ArrayTimeSeries([1,2,3],[4,5,6]))
	s = socket()
	host = gethostbyname("")
	port = 12340
	s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	s.bind((host, port))
	s.listen(5)
	try:
		while True:
			c, addr = s.accept()
			print("Got connection from:",addr)
			t = threading.Thread(target=clientThread,args=(c,StorageManager))
			t.start()
	finally:
		s.close()

