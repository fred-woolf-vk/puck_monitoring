#**************************************************************/
# get_modem_status.py
# Author: Fred Woolf
# Date:   Jan 18, 2021
# Copyright Vertical Knowledge, Inc.
# version 1.0
#**************************************************************/

import subprocess
import pdb
import sys
import linecache
MODEM_NUMBER_LOCATION = 4
MODEM_NUMBER_IN_LINE = 5
PING_SERVER_IP = "8.8.8.8"
locked_status = "Not Locked"
connected_status = "Not Connected"
stun_number = 0

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename_exc = f.f_code.co_filename
    linecache.checkcache(filename_exc)
    line = linecache.getline(filename_exc, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename_exc, lineno, line.strip(), exc_obj))

# set up python command to send shell commands with return data
def send_cmd_to_gw_modemmgr(cmd):
    stdoutdata = subprocess.getoutput(cmd)
    return stdoutdata

def get_network_stun_number():
    cmd = "ifconfig | grep scatr"
    lines = (send_cmd_to_gw_modemmgr(cmd)).splitlines()
    #print(lines)
    if 'scatr' in lines[0]:
        return lines[0].split('-')[0].split('scatr')[-1]
    else:
        print("Error finding stun number!")
        return 0

def parse_data_section(list_output):
    list_of_all_section_data = []
    #print(" list output modem status ", list_output)
    lines_in_modem_display = [x for x in list_output]
    #lines_in_modem_display.append(" ")  # create extra line for parsing

    pass
    # identify all section boundaries by ----------------------
    # list_start_of_section_by_row_num is a list of row numbers; points to the first row of each section, after the ------ separator
    try:
        list_start_of_section_by_row_num = [[ind, x] for ind, x in enumerate(lines_in_modem_display) if "----" in x]
        list_start_of_section_by_row_num = [x[0] for x in list_start_of_section_by_row_num]
        last_item = list_start_of_section_by_row_num[len(list_start_of_section_by_row_num) -1]

        list_start_of_section_by_row_num.append(len(lines_in_modem_display)) # create dummy start of last section for parsing

        # get list of each section data as list
        # list[each section[data for each section, one line per list element]]
        len_list_start_of_section_by_row_num = len(list_start_of_section_by_row_num)
        for j in range(len(list_start_of_section_by_row_num) - 1):
            list_of_all_section_data.append(
                lines_in_modem_display[list_start_of_section_by_row_num[j] + 1:list_start_of_section_by_row_num[j+1]])
        #print(lines_in_modem_display)
    except:
        print(" error in parse_data_section, get list of each section data as list", "\n", sys.exc_info())

    try:
        # get each element in data section from list_of_all_section_data and place in dictionary
        dict_all_data_elements = {}
        for j in range(len(list_of_all_section_data)):
            if len(list_of_all_section_data[j]) > 0 and '|' in list_of_all_section_data[j][0]:
                dict_data_elements_this_section = {}
                section_name = list_of_all_section_data[j][0].strip().split('|')[0].strip()
                # dict_data_elements_this_section['section_name'] = section_name

                element = ''
                element_index = 0
                for k in range(len(list_of_all_section_data[j])):
                    # element will have this type data: 'manufacturer: QUALCOMM INCORPORATED'
                    # if there is no element name, such as happens in System section, repeat the element name
                    if len(list_of_all_section_data[j]) > k and ':' in list_of_all_section_data[j][k]:
                        element = list_of_all_section_data[j][k].strip().split('|')[1].strip()
                        dict_data_elements_this_section[element.split(':')[0]] = element.split(':')[1].strip()
                        dict_data_elements_this_section[element.split(':')[0]] = element.split(':')[1].strip()
                        element_index = 0
                    else:
                        dict_data_elements_this_section[element.split(':')[0].strip() + str(element_index + 1)] = \
                            list_of_all_section_data[j][k].strip().split('|')[1].strip()

                dict_all_data_elements[section_name] = dict_data_elements_this_section

        return dict_all_data_elements


    except:
        print(" error in parse_data_section, et each element in data section", "\n", sys.exc_info())


# ping server using a specific modem interface
# collect ping samples and average them
def get_average_ping_time(interface, num_pings_to_average, ip_addr=PING_SERVER_IP):
    
    cmd = "ping -I " + interface + " "  + ip_addr + "  -c " + num_pings_to_average
    output_string = (send_cmd_to_gw_modemmgr(cmd))
    #print(output_string)

    search_string = "bytes from " + ip_addr
    if search_string in output_string:
        lines = output_string.splitlines()
        lines_with_search_string = [x.split(" ")[-2:-1]  for x in lines  if search_string in x]
        #print("str: ", lines_with_search_string[0][0], lines_with_search_string[0][0].split("=")[-1:][0])
        line_pings = [float(x[0].split("=")[-1:][0]) for x in lines_with_search_string]
        #print(" lines str:",line_pings)
        #print(" ping time i/f",interface, "= ", str(sum(line_pings)/len(line_pings))) 
        return sum(line_pings)/len(line_pings)

    else:
        return -1


# for the mmcli commands, extract the parameters for storage
def parse_data_section(list_output):
    list_of_all_section_data = []
    # print(" list output modem status ", list_output)
    lines_in_modem_display = [x for x in list_output]
    # lines_in_modem_display.append(" ")  # create extra line for parsing

    pass
    # identify all section boundaries by ----------------------
    # list_start_of_section_by_row_num is a list of row numbers; points to the first row of each section, after the ------ separator
    try:
        list_start_of_section_by_row_num = [[ind, x] for ind, x in enumerate(lines_in_modem_display) if "----" in x]
        list_start_of_section_by_row_num = [x[0] for x in list_start_of_section_by_row_num]
        last_item = list_start_of_section_by_row_num[len(list_start_of_section_by_row_num) - 1]

        list_start_of_section_by_row_num.append(
            len(lines_in_modem_display))  # create dummy start of last section for parsing

        # get list of each section data as list
        # list[each section[data for each section, one line per list element]]
        len_list_start_of_section_by_row_num = len(list_start_of_section_by_row_num)
        for j in range(len(list_start_of_section_by_row_num) - 1):
            list_of_all_section_data.append(
                lines_in_modem_display[list_start_of_section_by_row_num[j] + 1:list_start_of_section_by_row_num[j + 1]])
        # print(lines_in_modem_display)
    except:
        print(" error in parse_data_section, get list of each section data as list", "\n", sys.exc_info())

    try:
        # get each element in data section from list_of_all_section_data and place in dictionary
        dict_all_data_elements = {}
        for j in range(len(list_of_all_section_data)):
            if len(list_of_all_section_data[j]) > 0 and '|' in list_of_all_section_data[j][0]:
                dict_data_elements_this_section = {}
                section_name = list_of_all_section_data[j][0].strip().split('|')[0].strip()
                # dict_data_elements_this_section['section_name'] = section_name

                element = ''
                element_index = 0
                for k in range(len(list_of_all_section_data[j])):
                    # element will have thislen(list_of_all_section_data[j]) type data: 'manufacturer: QUALCOMM INCORPORATED'
                    # if there is no element name, such as happens in System section, repeat the element name
                    if len(list_of_all_section_data[j]) > k and ':' in list_of_all_section_data[j][k]:
                        element = list_of_all_section_data[j][k].strip().split('|')[1].strip()
                        dict_data_elements_this_section[element.split(':')[0].strip()] = element.split(':')[1].strip()
                        element_index = 0
                    else:
                        dict_data_elements_this_section[element.split(':')[0].strip() + str(element_index + 1)] = \
                            list_of_all_section_data[j][k].strip().split('|')[1].strip()

                dict_all_data_elements[section_name] = dict_data_elements_this_section

        return dict_all_data_elements


    except:
        print(" error in parse_data_section, et each element in data section", "\n", sys.exc_info())


def get_modem_stats():
    global locked_status, connected_status
    list_dict_all_modem_stats = []
    dict_bearer_info = {}
    dict_modem_info = {}
    list_output_modem_info = []
    list_output_bearer_info = []
    # print(output_list)
    num_modems_found = 0

    cmd = "mmcli --list-modems"
    output_list = (send_cmd_to_gw_modemmgr(cmd))
    #print(output_list)
    list_modems = list((output_list).split("\n"))

    for modem_list in range(0, len(list_modems)):
        if list_modems[modem_list] != '':
            num_modems_found = num_modems_found + 1

    print("Found ", num_modems_found, " modems")
    print("----------------------------------------------------------------------")
    locked_status = "no"

    for modem_number in range(num_modems_found):
        #pdb.set_trace()
        # dictionary which holds key:value pair for each modem parameter of interest
        # one dictionary for each Modem will be appended to the list_dict_all_modem_stats
        dict_all_modem_stats = {}
        current_line_in_modem_list = list_modems[modem_number].split('/')
        # print(" current_line ", current_line_in_modem_list)

        current_modem_number = -1
        dict_all_modem_stats["operator_name"] = ''
        dict_all_modem_stats["carrier_config"] = ''
        dict_all_modem_stats["locked_status"] = 'no'
        dict_all_modem_stats["connected"] = 'no'
        dict_all_modem_stats["current_signal_strength"] = 0
        # get all mmcli data elements
        try:
            if "Modem" in current_line_in_modem_list[MODEM_NUMBER_LOCATION]:
                current_modem_number = current_line_in_modem_list[MODEM_NUMBER_IN_LINE][0]
                modem_id = list_modems[modem_number].strip()
                modem_id = modem_id.split("[")[0]
                print("  Modem #",current_modem_number, modem_id, end='')
                dict_all_modem_stats["current_modem_number"] = current_modem_number

                cmd = "mmcli -m " + current_modem_number
                list_output_modem_info = list(send_cmd_to_gw_modemmgr(cmd).splitlines())
                #print(" list output modem status: \n", list_output_modem_info)

                if "error" in list_output_modem_info[0]:
                    print(" Error in reading modem data for Modem ", current_modem_number)
                    continue

                # get dictionary of each section data as a dictionary  of elements
                # dict{each section{dict for each section, one dict element for each paramName:value pair}
                dict_modem_info = parse_data_section(list_output_modem_info)
                if "General" in dict_modem_info:
                    if 'dbus path' in dict_modem_info['General']:
                        print(" modem General info: ", dict_modem_info['General']['dbus path'])

                #print(dict_modem_info)
                bearer_number = -1
                if 'Bearer' in dict_modem_info:
                    if 'dbus path' in dict_modem_info['Bearer']:
                        bearer_number = dict_modem_info['Bearer']['dbus path']
                        bearer_number = bearer_number.split('/')[-1:][0]
                        #print(" bearer_number for Modem ", current_modem_number, " is ", bearer_number)

                        cmd = "mmcli --bearer " + bearer_number
                        list_output_bearer_info = list(send_cmd_to_gw_modemmgr(cmd).splitlines())
                        if "error" in list_output_bearer_info[0]:
                            print(" Error in reading bearer data for Modem ", current_modem_number)

                        dict_bearer_info = parse_data_section(list_output_bearer_info)
                        #print("  bearer data for Modem ", current_modem_number, ":\n", list_output_bearer_info)
                        #print(dict_bearer_info)
                else:
                    print(" Error!  No Bearer number available for modem #", current_modem_number)

        except:
            print(" error in getting modem data for Modem ", current_modem_number, "\n", sys.exc_info())

        try:
            # get keys from dictionary to develop list of all param data available
            modem_info_sections = list(dict_modem_info.keys())
            #print(" modem info sections for Modem ", modem_info_sections)

            if "Hardware" in modem_info_sections:
                list_modem_info_Hardware_section_params = list(dict_modem_info["Hardware"].keys())
                if "carrier config" in list_modem_info_Hardware_section_params:
                    dict_all_modem_stats["carrier_config"] = \
                        dict_modem_info["Hardware"]["carrier config"].strip().split('%')[0]
                else:
                    print(" no carrier config found for Modem ", current_modem_number)
            else:
                print(" no Hardware section found for Modem ", current_modem_number)


            if "Status" in modem_info_sections:
                list_modem_info_Status_section_params = list(dict_modem_info["Status"].keys())
                if "lock" in list_modem_info_Status_section_params:
                    if 'sim-pin2' in dict_modem_info["Status"]["lock"]:
                        locked_status = "yes"  # locked_status = locked_status + " -- sim-pin2"
                    else:
                        locked_status = "no"  # locked_status = "status " + " -- NOT locked"
                else:
                    print(" Error! no lock status available")

                dict_all_modem_stats["locked_status"] = locked_status
                if "signal quality" in list_modem_info_Status_section_params:
                    dict_all_modem_stats["current_signal_strength"]  = dict_modem_info["Status"]["signal quality"].strip().split('%')[0]

                if "3GPP" in modem_info_sections:
                    list_modem_info_Statistics_section_params = list(dict_modem_info["3GPP"].keys())
                    if "operator name" in list_modem_info_Statistics_section_params:
                        dict_all_modem_stats["operator_name"] = dict_modem_info["3GPP"]["operator name"].strip()


        except:
            print(" Error in getting lock status; no entry in table for modem data - [Status][lock]")

        try:
            # get keys from dictionary to carrier_confige and develop list of all param data available
            modem_bearer_sections = list(dict_bearer_info.keys())
            if "Status" in modem_bearer_sections:
                list_modem_bearer_Status_section_params = list(dict_bearer_info["Status"].keys())

                if "connected" in list_modem_bearer_Status_section_params:
                    connected_status = dict_bearer_info["Status"]["connected"]

                if "yes" not in connected_status:
                    connected_status = "no"
                    print(" Error! Modem ", modem_number, " is not connected")
                    if "failed reason" in list_modem_bearer_Status_section_params:
                        print("    Reason: ", dict_bearer_info["Status"]["failed reason"])

                dict_all_modem_stats["connected"] = connected_status

            else:
                print(" Error!  Unable to find Status section in modem_bearer_sections")
        except:
            print(" Error in getting connected status; no entry in table for modem data - [Status][connected]")


        try:
            # bearer data of interest - Status section
            # get keys from dictionary to develop list of all param data available
            list_modem_bearer_sections = list(dict_bearer_info.keys())
            dict_all_modem_stats["suspended"] = ''
            dict_all_modem_stats["interface"] = ''
            dict_all_modem_stats["ip_timeout"] = '0'

            if "Status" in list_modem_bearer_sections:

                list_modem_bearer_Status_section_params = list(dict_bearer_info["Status"].keys())
                if "suspended" in list_modem_bearer_Status_section_params:
                    dict_all_modem_stats["suspended"] = dict_bearer_info["Status"]["suspended"]
                if "interface" in list_modem_bearer_Status_section_params:
                    dict_all_modem_stats["interface"] = dict_bearer_info["Status"]["interface"]
                if "ip timeout" in list_modem_bearer_Status_section_params:
                    dict_all_modem_stats["ip_timeout"] = dict_bearer_info["Status"]["ip timeout"]

            else:
                print(" Error! No Status section in modem_bearer_info")

            # bearer data of interest - IPv4 section
            dict_all_modem_stats["method"] = ''
            dict_all_modem_stats["ipaddr"] = ''
            dict_all_modem_stats["prefix"] = ''
            dict_all_modem_stats["gateway"] = ''
            dict_all_modem_stats["dns"] = ''
            if "IPv4 configuration" in list_modem_bearer_sections:
                list_modem_bearer_IPv4_section_params = list(dict_bearer_info["IPv4 configuration"].keys())

                if "method" in list_modem_bearer_IPv4_section_params:
                    dict_all_modem_stats["method"] = dict_bearer_info["IPv4 configuration"]["method"]
                if "address" in list_modem_bearer_IPv4_section_params:
                    dict_all_modem_stats["ipaddr"] = dict_bearer_info["IPv4 configuration"]["address"]
                if "prefix" in list_modem_bearer_IPv4_section_params:
                    dict_all_modem_stats["prefix"] = dict_bearer_info["IPv4 configuration"]["prefix"]
                if "gateway" in list_modem_bearer_IPv4_section_params:
                    dict_all_modem_stats["gateway"] = dict_bearer_info["IPv4 configuration"]["gateway"]
                if "dns" in list_modem_bearer_IPv4_section_params:
                    dict_all_modem_stats["dns"] = dict_bearer_info["IPv4 configuration"]["dns"]

            else:
                print(" Error! No IPv4 section in modem_bearer_info")

            # bearer data of interest - Statistics section
            dict_all_modem_stats["duration"] = '0'
            dict_all_modem_stats["bytesRx"] = '0'
            dict_all_modem_stats["bytesTx"] = '0'
            dict_all_modem_stats["attempts"] = '0'
            dict_all_modem_stats["total_duration"] = '0'
            dict_all_modem_stats["total_bytesRx"] = '0'
            dict_all_modem_stats["total_bytesTx"] = '0'
            if "Statistics" in list_modem_bearer_sections:
                list_modem_bearer_Statistics_section_params = list(dict_bearer_info["Statistics"].keys())

                if "duration" in list_modem_bearer_Statistics_section_params:
                    dict_all_modem_stats["duration"] = dict_bearer_info["Statistics"]["duration"]
                if "bytes rx" in list_modem_bearer_Statistics_section_params:
                    dict_all_modem_stats["bytesRx"] = dict_bearer_info["Statistics"]["bytes rx"]
                if "bytes tx" in list_modem_bearer_Statistics_section_params:
                    dict_all_modem_stats["bytesTx"] = dict_bearer_info["Statistics"]["bytes tx"]
                if "attempts" in list_modem_bearer_Statistics_section_params:
                    dict_all_modem_stats["attempts"] = dict_bearer_info["Statistics"]["attempts"]
                if "total-duration" in list_modem_bearer_Statistics_section_params:
                    dict_all_modem_stats["total_duration"] = dict_bearer_info["Statistics"]["total-duration"]
                if "total-bytes rx" in list_modem_bearer_Statistics_section_params:
                    dict_all_modem_stats["total_bytesRx"] = dict_bearer_info["Statistics"]["total-bytes rx"]
                if "total-bytes tx" in list_modem_bearer_Statistics_section_params:
                    dict_all_modem_stats["total_bytesTx"] = dict_bearer_info["Statistics"]["total-bytes tx"]

            else:
                print(" Error! No Statistics section in modem_bearer_info")
                PrintException()

        except:
            print(" Error! Could not get bearer data ")
            PrintException()

        #for key in dict_all_modem_stats:
        #    print("         ", key, ": ", dict_all_modem_stats[key])

        list_dict_all_modem_stats.append(dict_all_modem_stats)
        # print(list_dict_all_modem_stats)


    return list_dict_all_modem_stats



