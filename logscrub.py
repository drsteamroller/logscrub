#!/usr/bin/env python3
# Description - On the way
# Author: Andrew McConnell
# Date: 04/04/2023

import random
import re
import sys

# GLOBAL VARS
# Log content is a list of dictionaries if one log is supplied, and if multiple are supplied,
# then it is a list of lists of dictionaries
logcontents = []
# list of filenames
og_filenames = []
opflags = []
vdom_names = dict()
VDOM_INC = 1
dev_names = dict()
DEV_INC = 1
ip_repl = dict()
user_names = dict()
USER_INC = 1
syslogregex = re.compile(r'(.+?)=("[^"]*"|\S*)\s*')
ip4 = re.compile(r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)[.](25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)[.](25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)[.](25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)')
ip6 = re.compile(r"(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))")

# RFC1918 Detector
def isRFC1918(ip):
    a,b,c,d = ip.split('.')

    # Very explicitly checks if the addresses are RFC 1918 Class A/B/C addresses
    if (int(a) == 10):
        return(True)
    elif(int(a) == 172 and int(b) in range(16,32)):
        return(True)
    elif(int(a) == 192 and int(b) == 168):
        return(True)
    else:
        return(False)

# Subnet mask detector (Insert if needed)
'''
How it works:
1) Split the IP into a list of 4 numbers (we assume IPv4)
  a) expect_0 is set to True when we view a shift in 1's to 0's                                V We set it to True so if there's a '1' after a '0', it's not a net_mask
                                                    ===> 255.255.240.0 = 11111111.11111111.11110000.00000000
  b) constant is a catch-all for when we detect it isn't (or is!!!) a net_mask, and we return it accordingly

2) We take each value in the ip_list and check if it's non zero
  a) If it's non zero, we subtract 2^i from that value where i is a list from 7 to 0 (decremented).
    i) If the value hits zero during this process and i is not zero, set expect_0 to True and break out of the process [val is zero so we don't need to subtract any more]
    ii) If the value hits zero during the process and i IS zero (255 case), we continue to the next value
    ###### IF AT ALL DURING THIS PROCESS THE VALUE GOES BELOW ZERO, WE SET constant = False AND BREAK AND 'return constant' ######
  b) If the value starts out as zero, we don't bother with the process and just set expect_0 to True (catches 255.0.255.0 and similar cases)
'''
def isNetMask(ip):
    _ = ip.split('.')
    ip_list = list()
    for item in _:
        ip_list.append(int(item))

    # Return false for quad 0 case (default routes)
    if (ip_list == [0,0,0,0]):
        return False

    # Netmasks ALWAYS start with 1's
    expect_0 = False
    # We start out assuming constancy
    constant = True

    for val in ip_list:
        if (val != 0):
            for i in range(7, -1, -1):
                val = val - pow(2, i)
                if (val > 0 and not expect_0):
                    continue
                elif (val == 0  and i != 0):
                    expect_0 = True
                    break
                elif (val == 0 and not expect_0 and i == 0):
                    break
                else:
                    constant = False
                    break
            if (not constant):
                break
        else:
            expect_0 = True
    return constant

# Mask IPs
def replace_ip4(ip):
    if (isNetMask(ip)):
        return ip
    if (ip not in ip_repl.keys()):
        repl = ""
        if (isRFC1918(ip) and "-sPIP" in opflags and "-pi" not in opflags):
            octets = ip.split('.')
            repl = f"{octets[0]}.{octets[1]}.{random.randrange(0, 256)}.{random.randrange(1, 256)}"
        elif (not isRFC1918(ip) and "-pi" not in opflags):
            repl = f"{random.randrange(1, 255)}.{random.randrange(0, 255)}.{random.randrange(0, 255)}.{random.randrange(1, 255)}"
        else:
            repl = ip
        ip_repl[ip] = repl
        return repl
    
    # If we've replaced it before, pick out that replacement and return it
    else:
        return ip_repl[ip]

def replace_vdom(vdom):
    if (vdom not in vdom_names.keys()):
        pass

def replace_ip6(ip):
    if (ip not in ip_repl.keys() and "-pi" not in opflags):
        repl = f'{hex(random.randrange(1, 65535))[2:]}:{hex(random.randrange(1, 65535))[2:]}:{hex(random.randrange(1, 65535))[2:]}:{hex(random.randrange(1, 65535))[2:]}:{hex(random.randrange(1, 65535))[2:]}:{hex(random.randrange(1, 65535))[2:]}:{hex(random.randrange(1, 65535))[2:]}:{hex(random.randrange(1, 65535))[2:]}'
        ip_repl[ip] = repl
        return repl
    elif ("-pi" not in opflags):
        return ip_repl[ip]
    else:
        return ip

options = {"-h": "Display this output",\
           "-g": "Use this option if you are inputting a group of logs. Usage: py logscrub.py -g log1.log,log2.log3.log...",\
           "-sPIP": "Scrub private IPs. Assumes /16 subnet",\
           "-pi":"preserve all ip addresses",\
           "-pv":"preserve vdom names",\
           "-pd":"preserve device names",\
           "-csv":"Log files provided are in csv format"}

args = sys.argv

if (len(args) < 2):
    print("Usage: \n\tpy logscrub.py logfile.log [options]\nOR\n\tpy logscrub.py -g log1.log,log2.log,...")
    sys.exit()

if ('-h' in args[1]):
    for k,v in options.items():
        print(f'\t{k}: {v}')
    sys.exit()

if ("-g" == args[1]):
    # Expects literally: py logscrub.py -g log1.log,log2.log,log3.log...
    og_filenames = [arg for arg in args[2].split(',')]
    if (len(args) > 2):
        for x in args[3:]:
            opflags.append(x)
else:
    og_filenames.append(args[1])
    if (len(args) > 2):
        for x in args[2:]:
            opflags.append(x)

# Load contents
for filename in og_filenames:
    with open(filename, 'r') as logfile:
        lines = logfile.readlines()
        logentry = {}
        logfile_per_list = []
        for l in lines:
            elements = syslogregex.findall(l)
            for e in elements:
                logentry[e[0]] = e[1]

            logfile_per_list.append(logentry.copy())
            logentry.clear()

        logcontents.append(logfile_per_list.copy())
        logfile_per_list.clear()

# Walk through contents & scrub
for l_off, logfile in enumerate(logcontents):
    for entry_off, logentry in enumerate(logfile):
        try:
            # usernames
            if ("user" in logentry.keys()):
                if (logentry['user'] not in user_names.keys()):
                    user_names[logentry['user']] = logentry["user"] = f'"US_FED_USER{USER_INC}"'
                    USER_INC += 1
                else:
                    logentry["user"] = user_names[logentry['user']]

            # ip addresses (also under"ui" & msg)
            if ("srcip" in logentry.keys() or "dstip" in logentry.keys()):
                    if (':' in logentry["srcip"]):
                        if ("\"" in logentry['srcip']):
                            logentry["srcip"] = f'"{replace_ip6(logentry["srcip"][1:-1])}"'
                        else:
                            logentry["srcip"] = replace_ip6(logentry["srcip"])
                    else:
                        if ("\"" in logentry['srcip']):
                            logentry["srcip"] = f'"{replace_ip4(logentry["srcip"][1:-1])}"'
                        else:
                            logentry["srcip"] = replace_ip4(logentry["srcip"])

                    if (':' in logentry["dstip"]):
                        if ("\"" in logentry['dstip']):
                            logentry["dstip"] = f'"{replace_ip6(logentry["dstip"][1:-1])}"'
                        else:
                            logentry["dstip"] = replace_ip6(logentry["dstip"])
                    else:
                        if ("\"" in logentry['dstip']):
                            logentry["dstip"] = f'"{replace_ip4(logentry["dstip"][1:-1])}"'
                        else:
                            logentry["dstip"] = replace_ip4(logentry["dstip"])

            if ("ui" in logentry.keys()):
                ip_search = ip4.search(logentry['ui'])
                if (ip_search is None):
                    ip_search = ip6.search(logentry['ui'])
                if (ip_search is not None):
                    logentry['ui'] = logentry['ui'][:ip_search.span()[0]] + replace_ip4(ip_search.group()) + logentry['ui'][ip_search.span()[1]:]
            # msg
            if ("msg" in logentry.keys()):
                ip_search = ip4.search(logentry['msg'])
                if (ip_search is None):
                    ip_search = ip6.search(logentry['msg'])
                if (ip_search is not None):
                    logentry['msg'] = logentry['msg'][:ip_search.span()[0]] + replace_ip4(ip_search.group()) + logentry['msg'][ip_search.span()[1]:]

                for og_name, rep_name in user_names.items():
                    m = re.search(og_name, logentry['msg'])
                    if (m is not None):
                        logentry['msg'] = logentry['msg'][:m.span()[0]] + rep_name[1:-1] + logentry['msg'][m.span()[1]:]
                
                # scrub device names
                for og_name, rep_name in dev_names.items():
                    m = re.search(og_name, logentry['msg'])
                    if (m is not None):
                        logentry['msg'] = logentry['msg'][:m.span()[0]] + rep_name[1:-1] + logentry['msg'][m.span()[1]:]
                # scrub VDOM names
                for og_name, rep_name in vdom_names.items():
                    m = re.search(og_name, logentry['msg'])
                    if (m is not None):
                        logentry['msg'] = logentry['msg'][:m.span()[0]] + rep_name[1:-1] + logentry['msg'][m.span()[1]:]

            # device names
            if ('-pd' not in opflags and "devname" in logentry.keys()):
                if (logentry['devname'] not in dev_names.keys()):
                    dev_names[logentry['devname']] = logentry['devname'] = f'"US_FED_DEV_#{DEV_INC}"'
                    DEV_INC += 1
                else:
                    logentry['devname'] = dev_names[logentry['devname']]
            # vdom names
            if ('-pv' not in opflags and "vd" in logentry.keys()):
                if (logentry['vd'] != "root" ):
                    if (logentry['vd'] not in vdom_names.keys()):
                        vdom_names[logentry['vd']] = logentry['vd'] = f'"US_FED_VDOM_#{VDOM_INC}"'
                        DEV_INC += 1
                    else:
                        logentry['vd'] = vdom_names[logentry['vd']]
            # CSF names
        
        except (KeyError, IndexError) as e:
            print("Incomplete log")

        logfile[entry_off] = logentry.copy()
    logcontents[l_off] = logfile.copy()

print(og_filenames)

# Write modifications to scrubbed files

for c, fn in enumerate(og_filenames):
    with open(f"mod_{fn}", 'w') as modfile:
        for d in logcontents[c]:
            for b, a in d.items():
                modfile.write(f"{b}={a} ")
            modfile.write("\n")