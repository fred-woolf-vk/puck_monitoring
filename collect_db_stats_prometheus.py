#*************************************************************/
# collect_db_stats_prometheus.py
# Author: Fred Woolf
# Date:   Jan 18, 2021
# Copyright Vertical Knowledge, Inc.
# version 1.0
#**************************************************************/
from prometheus_client import start_http_server, Summary, Info, Gauge, Counter
import datetime
import time
from get_modem_status import *
import sys
import socket
import pdb 

# use current IP for database query
current_ip_addr = socket.gethostbyname(socket.gethostname())
print(" prometheus gw6200 exporter")
print (current_ip_addr)
#client=InfluxDBClient(host=current_ip_addr, port="8086")

DATA_COLLECTION_INTERVAL_IN_SECS = 15
NUM_PINGS_TO_AVERAGE = 5

remote_server_ip_address = '8.8.4.4'

# init time tracking for percentage uptime stats
total_available_time_in_secs_modems = {'Modem 0': 0, 'Modem 1': 0}
ping_time_wwan = {'Modem 0': 0, 'Modem 1': 0}
prev_time = datetime.datetime.now()
print(" Modem Script started on ", prev_time.ctime())
total_time_in_secs_script_running = 1
time_increment_in_sec_Modem = 1

start_http_server(8082)
time.sleep(1)
# this calculates the 'Availability' percentage
def calculate_percentage_uptime(modem_num, stats_connected, locked):
	global total_time_in_secs_script_running, prev_time, time_increment_in_sec_Modem

	# if "connected" status in mmcli bearer is "yes" then add data collection interval to the total time available
	#print("\n% 1 available ",modem_num, ": ", total_available_time_in_secs_modems[modem_num], time_increment_in_sec_Modem)
	#print(" connected  ", stats_connected, " locked: ", locked)
	if 'yes' in stats_connected and 'yes' in locked:
		total_available_time_in_secs_modems[modem_num] = total_available_time_in_secs_modems[modem_num] + time_increment_in_sec_Modem

		#print("num secs = ", total_time_in_secs_script_running, "num_min = ", total_time_in_secs_script_running / 60)
		#print("% available ",modem_num, ": ", total_available_time_in_secs_modems[modem_num]*100/total_time_in_secs_script_running)
		#print("% available ",modem_num, ": ", total_available_time_in_secs_modems[modem_num])
	else:
		print("Warning: modem not connected")

	percentage_uptime = total_available_time_in_secs_modems[modem_num]*100/total_time_in_secs_script_running
	return percentage_uptime

def get_config_params():
	global remote_server_ip_address
	print(" params from param file:")
	with open("gw6200_exporter_params.txt", 'r') as f:
		lines = f.readlines()
		if len(lines) > 0:
			for i in range(0, len(lines) - 1):
				print(" lines:",  lines)
				param_name = lines[i].strip().split('=')[0]
				param = lines[i].strip().split('=')[1]
				if param_name.find('remote_server_ip') != -1:
					remote_server_ip_address = param
					print(" wrote ", param_name+':'+param)



g_signal_strength1 = Gauge('gw6200_signal_strength1', 'Modem 1')
g_signal_strength2 = Gauge('gw6200_signal_strength2', 'Modem 2')
g_duration1 = Gauge('gw6200_duration1', 'Modem 1')
g_duration2 = Gauge('gw6200_duration2', 'Modem 2')
g_total_duration1 = Gauge('gw6200_total_duration1', 'Modem 1')
g_total_duration2 = Gauge('gw6200_total_duration2', 'Modem 2')
s_bytes_tx1 = Summary('gw6200_bytes_transmitted1', 'Modem 1')
s_total_bytes_tx1 = Summary('gw6200_total_bytes_transmitted1', 'Modem 1')
s_bytes_rx1 = Summary('gw6200_bytes_received1', 'Modem 1')
s_total_bytes_rx1 = Summary('gw6200_total_bytes_received1', 'Modem 1')
s_bytes_tx2 = Summary('gw6200_bytes_transmitted2', 'Modem 2')
s_total_bytes_tx2 = Summary('gw6200_total_bytes_transmitted2', 'Modem 2')
s_bytes_rx2 = Summary('gw6200_bytes_received2', 'Modem 2')
s_total_bytes_rx2 = Summary('gw6200_total_bytes_received2', 'Modem 2')
i_modem_info1 = Info("gw6200_modem_info1", 'Modem 1')
i_modem_info2 = Info("gw6200_modem_info2", 'Modem 2')
i_remote_server_ip = Info("gw6200_modem_remote_server_ip", 'Modem 0')
g_percent_uptime1 = Gauge('gw6200_percent_uptime1', 'Modem 1')
g_percent_uptime2 = Gauge('gw6200_percent_uptime2', 'Modem 2')
g_ping_time_to_server1 = Gauge('gw6200_ping_time_to_server1', 'Modem 1')
g_ping_time_to_server2 = Gauge('gw6200_ping_time_to_server2', 'Modem 2')

get_config_params()

while(1):
		# 'list_all_stats' is a list which contains Modem 0 and Modem 1 data; each dataset is a dictionary with a key:value pair for
		# each element extracted from the mmcli commands in get_modem_status.py

		list_all_stats = get_modem_stats()
		print("\n", list_all_stats, "\n")
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
				duration_min = (int(list_all_stats[i]['duration']))/60  #change default seconds to minutes for display
				#print("duration_min0 = ", duration_min0)
			except:
				print(" error in duration0 value", sys.exc_info() )
				duration_min = -1

			'''try:
				duration_min1 = (int(list_all_stats[1]['duration']))/60
				#print("duration_min1 = ", duration_min1)
			except:
				print(" error in duration1 value", sys.exc_info() )
				duration_min1 = -1
			'''
			try:
				total_duration_min = (int(list_all_stats[i]['total_duration']))/60
			except:
				print(" error in  total_duration0", sys.exc_info())
				total_duration_min = -1
			'''
			try:
				total_duration_min = (int(list_all_stats[1]['total_duration']))/60
			except:
				print(" error in  total_duration1", sys.exc_info())
				total_duration_min1 = -1
			'''

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
			this_interface_name = "ping_time_avg_" +  list_all_stats[i]["interface"]

			try:
				i_remote_server_ip.info({'remote_server':remote_server_ip_address})
				#pdb.set_trace()
				if i == 0:  # modem 1
					g_signal_strength1.set(int(list_all_stats[i]['current_signal_strength'][:2]))
					g_duration1.set(float(duration_min)) # up time in minutes
					s_bytes_tx1.observe(float(list_all_stats[i]['bytesTx']))
					s_bytes_rx1.observe(float(list_all_stats[i]['bytesRx']))
					s_total_bytes_tx1.observe(float(list_all_stats[i]['total_bytesTx']))
					s_total_bytes_rx1.observe(float(list_all_stats[i]['total_bytesRx']))
					i_modem_info1.info({'ip_addr':list_all_stats[i]['ipaddr'], "modem":"Modem 1", "interface":"wan0"})

					g_percent_uptime1.set(float(calculate_percentage_uptime(current_modem,
												list_all_stats[i]['connected'], list_all_stats[i]['locked_status'])))
					g_duration1.set(duration_min)
					g_total_duration1.set(total_duration_min)
					g_ping_time_to_server1.set(ping_time_wwan[i])

				else:   # modem 2
					g_signal_strength2.set(int(list_all_stats[i]['current_signal_strength'][:2]))
					g_duration2.set(float(duration_min)) # up time in minutes
					s_bytes_tx2.observe(float(list_all_stats[i]['bytesTx']))
					s_bytes_rx2.observe(float(list_all_stats[i]['bytesRx']))
					s_total_bytes_tx2.observe(float(list_all_stats[i]['total_bytesTx']))
					s_total_bytes_rx2.observe(float(list_all_stats[i]['total_bytesRx']))
					i_modem_info2.info({'ip_addr':list_all_stats[i]['ipaddr'],  "modem":"Modem 2", "interface":"wan1"})
					g_percent_uptime2.set(float(calculate_percentage_uptime(current_modem,
												list_all_stats[i]['connected'], list_all_stats[i]['locked_status'])))
					g_duration2.set(duration_min)
					g_total_duration2.set(total_duration_min)
					g_ping_time_to_server2.set(ping_time_wwan[i])

			except:
				print("\n Error!  Unable to write db values\n", sys.exc_info())


		# set time calculations for the next iteration
		time_increment_in_sec_Modem = datetime.datetime.now() - prev_time
		#print("time_increment_in_sec_Modem:", time_increment_in_sec_Modem, "  type:", type(time_increment_in_sec_Modem))
		time_increment_in_sec_Modem = time_increment_in_sec_Modem.seconds
		#print("time_increment_in_sec_Modem:", time_increment_in_sec_Modem, "  type:", type(time_increment_in_sec_Modem))

		total_time_in_secs_script_running = total_time_in_secs_script_running + time_increment_in_sec_Modem
		#print("2 total_time  :", total_time_in_secs_script_running)

		prev_time = datetime.datetime.now()


		time.sleep(DATA_COLLECTION_INTERVAL_IN_SECS - NUM_PINGS_TO_AVERAGE - 1)



