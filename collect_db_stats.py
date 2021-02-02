#*************************************************************/
# collect_db_stats.py
# Author: Fred Woolf
# Date:   Jan 18, 2021
# Copyright Vertical Knowledge, Inc.
# version 1.0
#**************************************************************/

from influxdb import InfluxDBClient
#from influxdb_client import InfluxDBClient
import datetime
import time
from get_modem_status import *
import sys
import socket
import pytz

# use current IP for database query
current_ip_addr = socket.gethostbyname(socket.gethostname())
print (current_ip_addr)
client=InfluxDBClient(host=current_ip_addr, port="8086")

DATA_COLLECTION_INTERVAL_IN_SECS = 15
NUM_PINGS_TO_AVERAGE = 5

# setup up influx db
if 'GW_Collections_DB' in client.get_list_database():
	client.switch_database('GW_Collections_DB2')
else:
	client.create_database("GW_Collections_DB2")
	client.switch_database('GW_Collections_DB2')

# init time tracking for percentage uptime stats
total_available_time_in_secs_modems = {}
total_available_time_in_secs_modems['Modem 0'] = 0
total_available_time_in_secs_modems['Modem 1'] = 0
ping_time_wwan = {}
ping_time_wwan['Modem 0'] = 0
ping_time_wwan['Modem 1'] = 0
prev_time = datetime.datetime.now()
print(" Modem Script started on ", prev_time.ctime())
total_time_in_secs_script_running = 1
time_increment_in_sec_Modem = 1

time.sleep(1)
# this calculates the 'Availability' percentage
def calculate_percentage_uptime(modem_num, stats_connected):
	global total_time_in_secs_script_running, prev_time, time_increment_in_sec_Modem
	
	# if "connected" status in mmcli bearer is "yes" then add data collection interval to the total time available
	#print("\n% 1 available ",modem_num, ": ", total_available_time_in_secs_modems[modem_num], time_increment_in_sec_Modem)
	#print(" connected  ", stats_connected)
	if 'yes' in stats_connected:
		total_available_time_in_secs_modems[modem_num] = total_available_time_in_secs_modems[modem_num] + time_increment_in_sec_Modem

		#print("num secs = ", total_time_in_secs_script_running, "num_min = ", total_time_in_secs_script_running / 60)
	    #print("% available ",modem_num, ": ", total_available_time_in_secs_modems[modem_num]*100/total_time_in_secs_script_running)	
	    #print("% available ",modem_num, ": ", total_available_time_in_secs_modems[modem_num])
	else:
		print("Warning: modem not connected")

	percentage_uptime = total_available_time_in_secs_modems[modem_num]*100/total_time_in_secs_script_running
	return percentage_uptime



while(1):
		# 'list_all_stats' is a list which contains Modem 0 and Modem 1 data; each dataset is a dictionary with a key:value pair for
		# each element extracted from the mmcli commands in get_modem_status.py
		list_all_stats = get_modem_stats()
		#print("\n", list_all_stats, "\n")
		for i in range(len(list_all_stats)):
			current_interface = 'wwan0'
			current_modem = 'Modem 0'
			if i == 1:
				current_interface = 'wwan1'
				current_modem = 'Modem 1'

			# check ping times to NY server
			ping_time_wwan[i] = get_average_ping_time(current_interface, str(NUM_PINGS_TO_AVERAGE))
			#print(" ping time[" + str(i) + "]:" + str(ping_time_wwan[i]))

			# some elements can be randomly missing in data updates from the modem; make sure any missing data returns -1
			try:
				duration_min0 = (list_all_stats[i]['duration'])/60  #change default seconds to minutes for display
			except:
				#print(" error in duration0 value", sys.exc_info() )
				duration_min0 = -1

			try:
				duration_min1 = (list_all_stats[1]['duration'])/60
			except:
				#print(" error in duration1 value", sys.exc_info() )
				duration_min1 = -1
			try:
				total_duration_min0 = (list_all_stats[i]['total_duration'])/60
			except:
				#print(" error in  total_duration0", sys.exc_info())
				total_duration_min0 = -1

			try:
				total_duration_min1 = (list_all_stats[1]['total_duration'])/60
			except:
				#print(" error in  total_duration1", sys.exc_info())
				total_duration_min1 = -1

			#percent_uptime1 = (total_duration_min1)/(duration_min1)*100
			#percent_uptime0 = (total_duration_min0)/(duration_min0)*100

			# for each non-string element expected in the data from modem, if not in this current snapshot, set the value to -1
			if 'current_signal_strength' not in list_all_stats[i].keys():
				list_all_stats[i]['current_signal_strength'] = -1
			if 'bytesRx' not in list_all_stats[i].keys():
				list_all_stats[i]['bytesRx'] = -1
			if 'bytesTx' not in list_all_stats[i].keys():
				list_all_stats[i]['bytesTx'] = -1
			if 'total_bytesRx' not in list_all_stats[i].keys():
				list_all_stats[i]['total_bytesRx'] = -1
			if 'total_bytesTx' not in list_all_stats[i].keys():
				list_all_stats[i]['total_bytesTx'] = -1
			if 'interface' not in list_all_stats[i].keys():
				list_all_stats[i]['interface'] = "unk"

			#list_all_stats[i]['ipaddr'] = ''

			# json_body is the data sent to the influx db; list_all_stats[i] is Modem 0,
			#  list_all_stats[1] is Modem 1
			try:
				json_body = [
						{
						"measurement": "uptime",
						"tags": {
								"modemName": current_modem,
						"interfaceName": list_all_stats[i]['interface']
						},
					"time":datetime.datetime.now(tz=pytz.timezone('US/Eastern')),
						"fields":{
						"interface" : list_all_stats[i]['interface'],
						"ipaddr" : list_all_stats[i]['ipaddr'],
						"duration": float(duration_min0), # time in minutes
						"percent_Uptime": float(calculate_percentage_uptime(current_modem, list_all_stats[i]['connected'])),
						"total_duration": float(total_duration_min0),
						"signal_strength": int(list_all_stats[i]['current_signal_strength'][:2]),
						"bytes_rx": int(list_all_stats[i]['bytesRx']) ,
						"total_bytes_rx": int(list_all_stats[i]['total_bytesRx']),
						"bytes_tx": int(list_all_stats[i]['bytesTx']) ,
						"total_bytes_tx": int(list_all_stats[i]['total_bytesTx']),
						"ping_time_avg_wwan0": float(ping_time_wwan[i])
							}
					}
					]
			except:
				print("\n Error!  Unable to write json_body\n", sys.exc_info())
			#print("\n", json_body)
			client.write_points(json_body)

		# set time calculations for the next iteration
		time_increment_in_sec_Modem = datetime.datetime.now() - prev_time
		time_increment_in_sec_Modem = time_increment_in_sec_Modem.seconds
		#print("time_increment_in_sec_Modem:", time_increment_in_sec_Modem)

		total_time_in_secs_script_running = total_time_in_secs_script_running + time_increment_in_sec_Modem
		#print("2 total_time  :", total_time_in_secs_script_running)

		prev_time = datetime.datetime.now()


		time.sleep(DATA_COLLECTION_INTERVAL_IN_SECS - NUM_PINGS_TO_AVERAGE - 1)


