import serial
import json
import argparse
import datetime
import urllib3

from elasticsearch import Elasticsearch


class DataHandler():
	# Max delta time for each bubulle sound to be considered as the same
	BUBULLE_SEQ_TIME = datetime.timedelta(milliseconds=600)
	# Number of bubulles needed to be considered as valid bubulle
	BUBULLE_THRESHOLD = 5

	def __init__(self):
		self.CURRENT_BUBULLE_SEQ = []

	def is_valid_bubulle_seq(self):
		return len(self.CURRENT_BUBULLE_SEQ) >= self.BUBULLE_THRESHOLD

	def is_part_of_current_sequence(self, d):
		return self.CURRENT_BUBULLE_SEQ and ((d - self.CURRENT_BUBULLE_SEQ[-1]) <= self.BUBULLE_SEQ_TIME)

	def handle_data(self, jdata):
		# Handle bubulle
		if jdata.get('bubulle', False):
			# New sequence or same sequence
			if not self.CURRENT_BUBULLE_SEQ or self.is_part_of_current_sequence(jdata['time']):
				self.CURRENT_BUBULLE_SEQ.append(jdata['time'])
			else:
				if self.is_valid_bubulle_seq():
					yield {'time': self.CURRENT_BUBULLE_SEQ[0], 'bubulle' : 1, 'score': len(self.CURRENT_BUBULLE_SEQ) }
				self.CURRENT_BUBULLE_SEQ = []
				self.CURRENT_BUBULLE_SEQ.append(jdata['time'])
		# Handle other
		# Nothing to do here we just return the data to be inserted to Elastic
		else:
			# Force refresh is a bubulle seq is finished
			if not self.is_part_of_current_sequence(jdata['time']) and self.is_valid_bubulle_seq():
				yield  {'time': self.CURRENT_BUBULLE_SEQ[0], 'bubulle' : 1, 'score': len(self.CURRENT_BUBULLE_SEQ) }
				self.CURRENT_BUBULLE_SEQ = []
			yield jdata

def main():
	urllib3.disable_warnings()
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--device", help="Serial Device", default="/dev/ttyACM0")
	parser.add_argument("-p", "--port", help="Serial Port number", type=int, default=9600)
	parser.add_argument("-t", "--tag", help="TAG")
	args = parser.parse_args()

	ser = serial.Serial(args.device, args.port)
	es = Elasticsearch([ {'host': 'search-beercraft-xbadq3qk7g5uxhjdjstow4lwdm.us-east-2.es.amazonaws.com', 'port': 443, 'use_ssl': True, 'verify_certs': False} ])

	data_handler = DataHandler()

	while True:
		try:
			# Read Serial Input as JSON
			data = ser.readline().decode().strip()
			jdata = json.loads(data)
			jdata['time'] = datetime.datetime.utcnow()

			# Handle JSON data
			for doc in data_handler.handle_data(jdata):
				doc['tag'] = args.tag
				print(doc)
				# insert into elk
				es.index(index="beercraft", doc_type='doc', body=doc)
		except Exception as e:
			print(e)




if __name__ == '__main__':
	main()
