## Description

Scrubs logs directly downloaded directly from FortiGate/FortiAnalyzer/FortiManager (syslog formatted). Scrubs usernames, ip addresses, vdom names, and device names. For private ip addresses, if -sPIP is included (see below), it assumes a /16 subnet.

## Usage
```
py | python | python3 logscrub.py [logfile] <options>
```

## Options
```
-h: Display this output
-g: Use this option if you are inputting a group of logs. DIFFERENT USAGE: py logscrub.py -g log1.log,log2.log3.log... <options> <---- Must be comma separated, with no spaces
-d: Same as -g, but specifying a whole directory. Usage: py logscrub.py -d [path] <options>
-sPIP: Scrub private IPs. Assumes /16 subnet
-pi: preserve all ip addresses (overrides -sPIP)
-pv: preserve vdom names
-pd: preserve device names
-csv: Log files provided are in csv format [DOES NOT WORK]
```