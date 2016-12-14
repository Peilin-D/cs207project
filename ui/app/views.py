from flask import jsonify, render_template, flash, redirect, session, url_for, request, g, abort
from app import app, db
from .models import User, Post, Timeseries
import json
from sqlalchemy import and_

import os
import socket
import sys
import pickle
from timeseries.FileStorageManager import FileStorageManager
import numpy as np
import random

def randomTSMetadata(id, cur_ts):
	if id is None:
		return None

	return Timeseries(id=id, 
						blarg=np.random.uniform(low=0.0, high=1.0),
						level=random.choice(['A','B','C','D','E']),
						mean=cur_ts.mean(),
						std=cur_ts.std())

def connectRBTree():
	port = 12341
	s = socket.socket()
	host = socket.gethostname()
	s.connect((host, port))
	return s

def connectSM():
	port = 12340 
	s = socket.socket()
	host = socket.gethostname()	
	s.connect((host, port))
	return s

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html',title='Home')	

@app.route('/timeseries', methods=['POST','GET'])
def timeseries():
	if request.method == 'POST':
		# adds a new timeseries into the database given a json which has a
		# key for an id and a key for the timeseries, and returns the timeseries
		data = request.get_json(force=True)
		if('id' not in data or 'time' not in data or 'value' not in data):
			return json.dumps("Invalid file."), 20, {'ContentType':'application/json'} 
		
		
		data['cmd'] = "ADDTS"
		s = connectSM()
		try:
			# Send POST request to server
			s.send(pickle.dumps(data))
			response = pickle.loads(s.recv(1024))

			# Add metadata to db
			t = db.session.query(Timeseries).filter_by(id=data['id']).first()
			if t:
				print("T exists, updating...")
				t.mean = np.mean(data['value'])
				t.std = np.std(data['value'])
			else:
				t = Timeseries(id=data['id'],
						blarg=np.random.uniform(low=0.0, high=1.0),
						level=random.choice(['A','B','C','D','E']),
						mean=np.mean(data['value']),
						std=np.std(data['value']))

			db.session.add(t)
			db.session.commit()
			print("Saved ts with id=",data['id'])
		except Exception as e:
			print("Exception ",e)
		finally:
			s.close()
			return json.dumps(response)
		
	else:
		# should send back a json with metadata from all the time series
		# Get all rows from table
		results = set(Timeseries.query.all())

		# Get query parameters
		mean_in = request.args.get('mean_in')
		level_in = request.args.get('level_in')
		level = request.args.get('level')
		
		# Filter by mean in 
		if mean_in is not "":
			mean_in = mean_in.split('-')
			m_min, m_max = mean_in[0],mean_in[1]
			if m_min == "inf" and m_max == "inf":
				tmp = set(Timeseries.query.all())	
			elif m_min == "inf" and m_max != "inf":
				m_max = float(m_max)
				tmp = set(Timeseries.query.filter(Timeseries.mean <= m_max).all())	
			elif m_min != "inf" and m_max == "inf":
				m_min = float(m_min)
				tmp = set(Timeseries.query.filter(Timeseries.mean >= m_min).all())
			else:
				m_min, m_max = float(m_min), float(m_max)
				tmp = set(Timeseries.query.filter(and_(Timeseries.mean >= m_min, Timeseries.mean <= m_max)).all())	
			
			results &= tmp
		
		# Filter by level in 
		if level_in is not None:
			level_in = level_in.split(',') 
			tmp = set(Timeseries.query.filter(Timeseries.level.in_(level_in)).all())
			results &= tmp
		
		# Filter by level 
		if level is not None:
			tmp = set(Timeseries.query.filter_by(level=level).all())
			results &= tmp
		
		# Serialize objects 

		r = [e.serialize() for e in results]
		print("R=",r)
		print("Jsonify",jsonify(r))
		return jsonify(r)
	
@app.route('/simquery', methods=['POST','GET'])
def simquery():
	if request.method == 'POST':
		# take a timeseries as an input in a JSON, carry out the query, and 
		# return the appropriate ids as well. 
		data = request.get_json(force=True)
		data['cmd'] = "SIMTS"
		if 'n' not in data:
			data['n'] = 5
		s = connectRBTree()
		try:
			s.send(pickle.dumps(data))
			response = pickle.loads(s.recv(8192))
			return jsonify({"similar_points": response})	
		finally:
			s.close()
			
	else:
		#  take a id=the_id querystring and use that as an id into the database
		# to find the timeseries that are similar, sending back the ids of (say) the top 5
		sim_id = request.args.get('id')
		n = request.args.get('n')
		print("SIMID=",sim_id)
		if n is None:
			n = 5
		s = connectRBTree()
		try:
			while True:
				toSend = {"cmd":"SIMID", "id":sim_id, "n":n}
				s.send(pickle.dumps(toSend))
				rec = s.recv(8192)
				# TODO data MORE THAN 1024, protocol?
				rec = pickle.loads(rec)
				return jsonify({"similar_points": rec})	
		finally:
			s.close()
		

@app.route('/timeseries/<id>')
def timeseries_id(id):
	# should send back metadata and the timeseries itself in a JSON payload

	# Get metadata
	t = Timeseries.query.get(id)
	if t is None:
		return jsonify("Timeseries id does not exist")

	t = t.serialize()

	# Get timeseries 
	s = connectSM()
	try:
		toSend = {"cmd":"BYID","id":id} # A = get timeseries by id, B = get all timeseries etc
		s.send(pickle.dumps(toSend))
		rec = s.recv(8192)
		rec = pickle.loads(rec)
		return jsonify({"timeseries": rec, "metadata": t})

	finally:
		s.close()

@app.route('/initsqldb')
def init_sqldb():
	# Create fake metadata for 1000 timeseries
	filePath = os.path.dirname(__file__)
	for id in range(1000):
		relPath = '../../simsearch/ts_data/ts_%d.dat'%id
		cur_ts = pickle.load(open(os.path.join(filePath, relPath), 'rb'))
		t = db.session.query(Timeseries).filter_by(id=id).first()
		if t:
			t.mean = cur_ts.mean()
			t.std = cur_ts.std()
		else:
			t = Timeseries(id=id,
					blarg=np.random.uniform(low=0.0, high=1.0),
					level=random.choice(['A','B','C','D','E']),
					mean=cur_ts.mean(),
					std=cur_ts.std())

		db.session.add(t)
	db.session.commit()

	return json.dumps("Success")





