import time
import subprocess
from prometheus_client import start_http_server, Summary, Info, Gauge, Counter, Histogram
import pdb
import sys
import itertools
import linecache

'''
  --------------------------
  3GPP |      operator code: 310
       |      operator name: 410
       | location area code: FFFE
       | tracking area code: 2C14
       |            cell id: 0B28DF0A
  
3GPP scan | networks: 311480 - Verizon (lte, available)
            |           311490 - 311 490 (lte, available)
            |           310260 - T-Mobile (mts, available)
            |           310260 - T-Mobile (lte, available)
            |           313100 - 313 100 (lte, available)
            |           310410 - AT&T (umts, available)
            |           310410 - AT&T (lte, current)
'''


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename_exc = f.f_code.co_filename
    linecache.checkcache(filename_exc)
    line = linecache.getline(filename_exc, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename_exc, lineno, line.strip(), exc_obj))
    print(sys.exc_info())

def send_cmd_to_gw_modemmgr(cmd):
    stdoutdata = subprocess.getoutput(cmd)
    return stdoutdata

def get_raw_data_location(str):
    dict_location_data = {}
    lines = str.splitlines()

    dict_location_data['operator_code'] = lines[1].split()[-1]
    dict_location_data['operator_name'] = lines[2].split()[-1]
    dict_location_data['lac'] = lines[3].split()[-1]
    dict_location_data['tac'] = lines[4].split()[-1]
    dict_location_data['cell_id'] = lines[5].split()[-1]
    #print(dict_location_data)
    return dict_location_data

def get_raw_data_scan(data):
    print(data)
    lines = data.splitlines()
    dict_scan_data = {}

    print("size of lines: ", len(lines), lines)
    if len(lines) > 1:
        line = lines[1].split()
        str_data = ''
        for i in range(1, len(lines)):
            #pdb.set_trace()
            line = lines[i].split()
            if 'networks:' in line:
                dict_scan_data['network_'+str(i)] = ' '.join([line[4] , ' '.join(line[6:])])
            else:
                dict_scan_data['network_'+str(i)] = ' '.join([line[1] ,' '.join(line[3:])])

    #print(dict_scan_data)
    return dict_scan_data


port_number_for_status_check = 8084
start_http_server(port_number_for_status_check)
time.sleep(1)

i_status_cell_location1 = Info("modem_location1", 'system')
i_status_cell_location2 = Info("modem_location2", 'system')
i_status_neighbor_cell_info = Info("tower_info", 'system')

modem1 = 0
modem2 = 1

try:
        output_string = send_cmd_to_gw_modemmgr('mmcli -m ' + str(modem1) + '  --location-enable-3gpp')

        time.sleep(1)
        output_string = send_cmd_to_gw_modemmgr('mmcli -m ' + str(modem2) + ' --location-enable-3gpp')
        time.sleep(1)

        output_string_loc1 = send_cmd_to_gw_modemmgr('mmcli -m ' + str(modem1) + '  --location-get')
        time.sleep(1)

        output_string_loc2 = send_cmd_to_gw_modemmgr('mmcli -m ' + str(modem2) + ' --location-get')
        time.sleep(1)

        if len(output_string_loc1) > 0:
            loc1 = get_raw_data_location(output_string_loc1)
            print("\nCurrent location data for modem 1: \n" + output_string_loc1 + "\n")
        else:
            print(" Error in getting raw data for modem 1")

	#print(loc1)
	#loc2 = get_raw_data_location(output_string_loc2)
	#print("\nCurrent location data for modem 2: \n" + output_string_loc2 + "\n" )
        if len(output_string_loc2) > 0:
            loc2 = get_raw_data_location(output_string_loc2)
            print("\nCurrent location data for modem 2: \n" + output_string_loc2 + "\n")  
        else:
            print(" Error in getting raw data for modem 2")


        #print(loc2)
        i_status_cell_location1.info(loc1)
        i_status_cell_location2.info(loc2)

        '''
        str1 = " --------------------- " + "\n"  \
        "  3GPP scan | networks: 311480 - Verizon (lte, available) " + "\n" \
        "            |           313100 - 313 100 (lte, available) " + "\n"  \
        "            |           310260 - T-Mobile (umts, available) " + "\n"  \
        "            |           311490 - 311 490 (lte, available) " + "\n"  \
        "            |           310260 - T-Mobile (lte, available) " + "\n"  \
        "            |           310410 - AT&T (umts, available) " + "\n"  \
        "            |           310410 - AT&T (lte, current)"
        neighbor = get_raw_data_scan(str1)
        print(neighbor, "\n  len of neighbor: ", len(neighbor))
        #pdb.set_trace()
        i_status_neighbor_cell_info.info(neighbor)
        '''

        print(" scanning network . . . ")
        output_string_neighbor_cell_info = send_cmd_to_gw_modemmgr('mmcli -m ' + str(modem1) + ' --3gpp-scan --timeout=300')
        print("\nNeighbor cell data:\n" + output_string_neighbor_cell_info)
        neighbor = get_raw_data_scan(output_string_neighbor_cell_info)
        print(neighbor)


        print(" write data to DB")

        i_status_neighbor_cell_info.info(neighbor)



except:
    PrintException()

while(1):
    time.sleep(1) # keep this going so that the 8084 server process can be accessed by Grafana

