import os
import pdb

def get_mount_point(pathname):
    "Get the mount point of the filesystem containing pathname"
    pathname= os.path.normcase(os.path.realpath(pathname))
    parent_device= path_device= os.stat(pathname).st_dev
    while parent_device == path_device:
        mount_point= pathname
        pathname= os.path.dirname(pathname)
        if pathname == mount_point:
            break
        parent_device= os.stat(pathname).st_dev
    return mount_point

def get_mounted_device(pathname):
    print("Get the device mounted at pathname")
    # uses "/proc/mounts"
    pathname= os.path.normcase(pathname) #
    try:
        with open("/proc/mounts", "r") as ifp:
            for line in ifp:
                fields= line.rstrip('\n').split()
                # note that line above assumes that
                # no mount points contain whitespace
                if fields[1] == pathname:
                    return fields[0]
    except EnvironmentError:
        pass
    return None # explicit

def get_fs_freespace(pathname):
    #print("Get the free space of the filesystem containing pathname")
    stat= os.statvfs(pathname)
    #print(stat)
    # use f_bfree for superuser, or f_bavail if filesystem
    # has reserved space for superuser
    return stat.f_bfree*stat.f_bsize


def get_storage_string():
    # default - two days storage; for when there is no micro SD card installed
    str_command_line_config_params = ''
    str_retention = '--storage.tsdb.retention.time=2d --storage.tsdb.retention.size=150MB'
    storage_path = ''  # default dir is /var/lib/prometheus
    gigabyte = 1024 * 1024 * 1024
    megabyte = 1024 * 1024
    megabytes_per_day_storage_required = 75000000
    storage_path ="/mnt/microsd"

    # check to see if microsd dir is available
    pdb.set_trace()
    for dir in os.listdir('/mnt'):
        if 'microsd' in dir and get_mount_point(storage_path) == storage_path:
            print(" mount point ", get_mount_point(storage_path), " for device ",
                  get_mounted_device(storage_path))
            freespace = get_fs_freespace(storage_path)
            print("SD micro card freespace: ", freespace)
            max_bytes_storage = 0
            str_storage_path = ''
            days = 0

            if freespace > 29 * gigabyte:  # s/b 32 GB SD card; allocate approx 29 GB
                max_bytes_storage = 29 * gigabyte
                days = int(max_bytes_storage/megabytes_per_day_storage_required)  # assume 75 MB per day for storage
                # limit storage to 60d/30GB
                str_retention = '  --storage.tsdb.retention.time=60d --storage.tsdb.retention.size=29GB'

            else:
                freespace = (freespace * .90)  # else allocate 90% if not than 32 GB
                max_bytes_storage = 0
                if megabyte < freespace < gigabyte:
                    max_bytes_storage = str(int(freespace/megabyte)) + 'MB'
                elif freespace > gigabyte:
                    # limit storage to 60d/30GB
                    if max_bytes_storage > 29:
                        max_bytes_storage = 29
                    max_bytes_storage = str(int(freespace/gigabyte)) + 'GB'

                days = int(freespace/megabytes_per_day_storage_required)  # assume 75 MB per day for storage
                if days > 60:
                    days = 60
                str_retention = '  --storage.tsdb.retention.time=' + str(days) + 'd'
                str_retention = str_retention + '  --storage.tsdb.retention.size=' + str(max_bytes_storage)

            str_command_line_config_params =   str_retention + ' --storage.tsdb.path=' + storage_path

        else:
            # default prometheus storage path will be uesd
            str_command_line_config_params = '  --storage.tsdb.retention.time=2d --storage.tsdb.retention.size=150MB'


    return str_command_line_config_params


str_service_config1 = '[Unit]\n' \
'Description=Monitoring system and time series database\n'   \
'Documentation=https://prometheus.io/docs/introduction/overview/\n'   \
'\n' \
'[Service]\n'   \
'Restart=always\n'   \
'User=prometheus\n'   \
'EnvironmentFile=/etc/default/prometheus'

str_service_config2 = 'ExecStart=/usr/bin/prometheus --config.file /etc/prometheus/prometheus.yml'

str_service_config2 = str_service_config2 + get_storage_string()

str_service_config3 = 'ExecReload=/bin/kill -HUP $MAINPID\n'   \
'TimeoutStopSec=20s\n'   \
'SendSIGKILL=no\n'   \
'LimitNOFILE=8192 \n'   \
'\n' \
'[Install]\n'   \
'WantedBy=multi-user.target\n'
'\n'

filename = 'prometheus.service'
with open(filename, 'w') as f:
    #print(str_service_config1+ ' \\' + '\n' +str_service_config2 + ' \\' +'\n'+str_service_config3)
    f.write(str_service_config1+ '\n' + str_service_config2 + '\n' + str_service_config3 )

