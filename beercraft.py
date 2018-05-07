import serial
import json
import argparse
import datetime

from elasticsearch import Elasticsearch

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--device", help="Serial Device", default="/dev/ttyACM0")
	parser.add_argument("-p", "--port", help="Serial Port number", type=int, default=9600)
	parser.add_argument("-t", "--tag", help="TAG")
	args = parser.parse_args()

	ser = serial.Serial(args.device, args.port)
	es = Elasticsearch([ {'host': 'search-beercraft-xbadq3qk7g5uxhjdjstow4lwdm.us-east-2.es.amazonaws.com', 'port': 443, 'use_ssl': True, 'verify_certs': False} ])

	while True:
		try:
			data = ser.readline().decode().strip()
			jdata = json.loads(data)

			jdata['tag'] = args.tag
			jdata['time'] = datetime.datetime.utcnow()
			# print(json.dumps(jdata, sort_keys=True, indent=4))

			# insert into elk
			# res = es.index(index="beercraft", doc_type='doc', body=jdata)
			print(jdata.get('temp', 0))
		except Exception as e:
			print(e)




if __name__ == '__main__':
	main()