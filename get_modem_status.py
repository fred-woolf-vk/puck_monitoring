#**************************************************************/
# get_modem_status.py
# Author: Fred Woolf
# Date:   Jan 18, 2021
# Copyright Vertical Knowledge, Inc.
# version 1.0
#**************************************************************/

import subprocess
MODEM_IN_LINE = 4
MODEM_NUMBER_IN_LINE = 5
NY_SERVER_IP = "206.166.228.21"

# set up python command to send shell commands with return data
def send_cmd_to_gw_modemmgr(cmd):
    stdoutdata = subprocess.getoutput(cmd)
    return stdoutdata

# ping server using a specific modem interface
# collect 5 ping samples and average them 
def get_average_ping_time(interface, num_pings_to_average):
    cmd = "sudo ping -I " + interface + " "  + NY_SERVER_IP + "  -c " + num_pings_to_average
    output_string = (send_cmd_to_gw_modemmgr(cmd))
    #print(output_string)

    search_string = "bytes from " + NY_SERVER_IP
    if search_string in output_string:
        lines = output_string.splitlines()
        lines_with_search_string = [x.split(" ")[-2:-1]  for x in lines  if search_string in x]
        #print("str: ", lines_with_search_string[0][0], lines_with_search_string[0][0].split("=")[-1:][0])
        line_pings = [float(x[0].split("=")[-1:][0]) for x in lines_with_search_string]
        #print(" lines str:",line_pings)
        return sum(line_pings)/len(line_pings)

    else:
        return -1

# for the mmcli commands, extract the parameters for storage in the influx db 
def get_modem_stats():
    list_dict_all_modem_stats  = []
    cmd = "mmcli --list-modems"
    output_list = (send_cmd_to_gw_modemmgr(cmd))
    #print(output_list)
    list_modems = list((output_list).split("\n"))
    num_modems_found = len(list_modems)
    print("\nFound ", num_modems_found, " modems")
    print("----------------------------------------------------------------------")

    for i in range(num_modems_found):
        # dictionary which holds key:value pair for each modem parameter of interest
        # one dictionary for each Modem will be appended to the list_dict_all_modem_stats
        dict_all_modem_stats = {}  
        current_line_in_modem_list = list_modems[i].split('/')
        #print(" current_line ", current_line_in_modem_list)
        if "Modem" in current_line_in_modem_list[MODEM_IN_LINE] :

            current_modem_number = current_line_in_modem_list[MODEM_NUMBER_IN_LINE][0]
            print("\n Modem #",current_modem_number , " ", list_modems[i].strip())

            # get modem status and verify lock state
            cmd = "mmcli -m " + current_line_in_modem_list[MODEM_NUMBER_IN_LINE][0]
            list_output_modem_status = list(send_cmd_to_gw_modemmgr(cmd).splitlines())
            #print(" list output modem status ", list_output_modem_status)
            lines_in_modem_display = [x for x in list_output_modem_status]
            #print(" lines in modem status ", lines_in_modem_status)

            status = ""
            reason = ""
            # find Status section
            Status_section_index = [[ind, x] for ind, x in enumerate(lines_in_modem_display) if "Status" in x][0][0]
            Modes_section_index = [[ind, x] for ind, x in enumerate(lines_in_modem_display) if "Modes" in x][0][0]

            list_Status_section = lines_in_modem_display[Status_section_index:Modes_section_index]
	
            # get current signal strength
            status = ""
            current_signal_strength = ""
            if 'recent' in list_Status_section[5]:
                current_signal_strength = list_Status_section[5].split()[-2:-1][0]

            dict_all_modem_stats['current_signal_strength'] = current_signal_strength
            # some elements may be missing or out of order so each line must be searched
            for i in range(len(list_Status_section)):
                if list_Status_section[i].lower().find("lock") != -1:
                    status = "Locked"
                    #print("sim: ", list_Status_section)
                    if list_Status_section[i].lower().find('sim-pin2') != -1: # sim-pin2 is displayed for lock
                        status = status + " -- sim-pin2"
                    else:
                        status = "status " + " -- NOT locked"

                # print(" status = ", status)

            # if there is an error in the modem connecting, a reason may be stated here
            if list_Status_section[i].find('reason') != -1:
                list_reason = list(list_Status_section[i].split()[-1:])
                reason = list_reason[0]
                status = "failed"

                print("    Error!: modem #", current_modem_number, " is in Failed state")
                print("       Reason: ", reason)

            else:
                print("    Success! Modem #", current_modem_number, " is ", status)
                
                if "Locked" in status:
                    # get bearer data 
                    cmd = "mmcli --bearer " + current_modem_number
                    output = send_cmd_to_gw_modemmgr(cmd)
                    list_bearer_data = list(send_cmd_to_gw_modemmgr(cmd).splitlines())

                    #print(" bearer data: ", list_bearer_data)
                    Status_section_index = [[ind, x] for ind, x in enumerate(list_bearer_data) if "Status" in x][0][0]
                    IPv4_section_index = [[ind, x] for ind, x in enumerate(list_bearer_data) if "IPv4 configuration" in x][0][0]
                    IPv6_section_index = [[ind, x] for ind, x in enumerate(list_bearer_data) if "IPv6 configuration" in x][0][0]
                    Statistics_section_index = [[ind, x] for ind, x in enumerate(list_bearer_data) if "Statistics" in x][0][0]

                    # extract parameters from the Status section
                    list_bearer_Status_section = list_bearer_data[Status_section_index:IPv4_section_index]
                    connected = ""
                    suspended = ""
                    interface = ""
                    ip_timeout = ""

                    # since elements and sections can be missing from the output, search for each
                    # parameter in each line of the section 

                    for j in range(len(list_bearer_Status_section)):
                        if list_bearer_Status_section[j].lower().find("connected") != -1:
                            try:
                                dict_all_modem_stats["connected"]= list_bearer_Status_section[j].split()[-1:][0]
                            except:
                                print("error in data from mmcli: connected")

                        if list_bearer_Status_section[j].lower().find("suspended") != -1:
                            try:
                                dict_all_modem_stats["suspended "]= list_bearer_Status_section[j].split()[-1:][0]
                            except:
                                print("error in data from mmcli: suspended ")

                        if list_bearer_Status_section[j].lower().find("interface") != -1:
                            try:
                                dict_all_modem_stats["interface"]= list_bearer_Status_section[j].split()[-1:][0]
                            except:
                                print("error in data from mmcli: interface")

                        if list_bearer_Status_section[j].lower().find("ip_timeout") != -1:
                            try:
                                dict_all_modem_stats["ip_timeout"]= list_bearer_Status_section[j].split()[-1:][0]
                            except:
                                print("error in data from mmcli: ip_timeout")

                    
                    # extract parameters from the IPv4 section
                    method = ""
                    address = ""
                    prefix = ""
                    gateway = ""
                    dns1 = ""
                    dns2 = ""
                    list_bearer_IPv4_section = list_bearer_data[IPv4_section_index:IPv6_section_index]
                    for j in range(len(list_bearer_IPv4_section)):
                        #print("j: ", j, list_bearer_IPv4_section[j])
                        if list_bearer_IPv4_section[j].lower().find("method") != -1:
                            try:
                                dict_all_modem_stats["method"]= list_bearer_IPv4_section[j].split()[-1:][0]
                                print(" method")
                            except:
                                print("error in data from mmcli: method")

                        if list_bearer_IPv4_section[j].lower().find("address") != -1:
                            try:
                                dict_all_modem_stats["ipaddr"]= list_bearer_IPv4_section[j].split()[-1:][0]
                            except:
                                print("error in data from mmcli: addresss")

                        if list_bearer_IPv4_section[j].lower().find("prefix") != -1:
                            try:
                                print(" prefix")
                                dict_all_modem_stats["prefix"]= list_bearer_IPv4_section[j].split()[-1:][0]
                            except:
                                print("error in data from mmcli: prefix ")

                        if list_bearer_IPv4_section[j].lower().find("gateway") != -1:
                            try:
                                dict_all_modem_stats["gateway"]= list_bearer_IPv4_section[j].split()[-1:][0]
                            except:
                                print("error in data from mmcli: gateway ")

                        if list_bearer_IPv4_section[j].lower().find("dns1") != -1:
                            try:
                                dict_all_modem_stats["dns1 "]= int(list_bearer_IPv4_section[j].split()[-1:][0])
                            except:
                                print("error in data from mmcli: dns1")

                        if list_bearer_IPv4_section[j].lower().find("dns2") != -1:
                            try:
                                dict_all_modem_stats["dns2"]= int(list_bearer_IPv4_section[j].split()[-1:][0])
                            except:
                                print("error in data from mmcli: dns2 ")

                    # extract parameters from the Statistics section
                    duration = ""
                    bytesRx = ""
                    bytesTx = ""
                    attempts = ""
                    total_duration = ""
                    total_bytesRx = ""
                    total_bytesTx = ""
                    list_bearer_Statistics_section = list_bearer_data[Statistics_section_index:]
                    #print(" Statistics: ", list_bearer_Statistics_section)
                    for j in range(len(list_bearer_Statistics_section)):
                        #print("l = ", list_bearer_Statistics_section[j])
                        # extra check to distinguish total-duration and duration
                        if list_bearer_Statistics_section[j].lower().find("duration") != -1 and  \
                            list_bearer_Statistics_section[j].lower().find("total-duration") == -1:
                            try:
                                print(" duration = ", int(list_bearer_Statistics_section[j].split()[-1:][0]))
                                dict_all_modem_stats["duration"] = int(list_bearer_Statistics_section[j].split()[-1:][0])
                            except:
                                print("error in data from mmcli: duration")

                        if list_bearer_Statistics_section[j].lower().find("bytes rx") != -1 and \
                           list_bearer_Statistics_section[j].lower().find("total-bytes rx") == -1:
                            try:
                                dict_all_modem_stats["bytesRx"] = int(list_bearer_Statistics_section[j].split()[-1:][0])
                            except:
                                print("error in data from mmcli: bytesRx ")

                        if list_bearer_Statistics_section[j].lower().find("bytes tx") != -1 and \
                            list_bearer_Statistics_section[j].lower().find("total-bytes tx") == -1:
                            try:
                                dict_all_modem_stats["bytesTx"] = int(list_bearer_Statistics_section[j].split()[-1:][0])
                            except:
                                print("error in data from mmcli: bytesTx ")

                        if list_bearer_Statistics_section[j].lower().find("attempts") != -1:
                            try:
                                dict_all_modem_stats["attempts"] = int(list_bearer_Statistics_section[j].split()[-1:][0])
                            except:
                                print("error in data from mmcli: attempts ")

                        if list_bearer_Statistics_section[j].lower().find("total-duration") != -1:
                            try:
                                print(" total-duration = ", int(list_bearer_Statistics_section[j].split()[-1:][0]))
                                dict_all_modem_stats["total_duration"] = int(list_bearer_Statistics_section[j].split()[-1:][0])
                            except:
                                print("error in data from mmcli: total_duration")

                        if list_bearer_Statistics_section[j].lower().find("total-bytes rx") != -1:
                            try:
                                dict_all_modem_stats["total_bytesRx"] = int(list_bearer_Statistics_section[j].split()[-1:][0])
                            except:
                                print("error in data from mmcli: total_bytesRx")

                        if list_bearer_Statistics_section[j].lower().find("total-bytes tx") != -1:
                            try:
                                dict_all_modem_stats["total_bytesTx"] = int(list_bearer_Statistics_section[j].split()[-1:][0])
                            except:
                                print("error in data from mmcli: total_bytesTx")

                    for key in dict_all_modem_stats:
                        print("         ", key, ": ", dict_all_modem_stats[key])
                    print()

                    list_dict_all_modem_stats.append(dict_all_modem_stats)
                    #print(list_dict_all_modem_stats)


                else:
                    print("   Error! in connecting modem.  Reason: ", output_list)


        else:
            print(" Error: Modem not found")

    print(" completed stats collection")
    return list_dict_all_modem_stats



