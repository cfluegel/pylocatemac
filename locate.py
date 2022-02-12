import sys
from pprint import pprint as pp

# Core modules
from network import NSCheckResult, MACAddress, NetworkSwitch

# Import the topology from a separate file.
# This allowes me to develop this on a realworld network without exposing
# too much information
from topology import CoreSwitch, SwitchList

# No arguments passed to commandline
if len(sys.argv) < 2:
    print("MAC Address not supplied")
    sys.exit(0)

# is it a valid mac address in the format xx:xx:xx:xx:xx:xx ?
try:
    Device = MACAddress(str(sys.argv[1]))
except:
    print("Error with creating Device from provided MAC address")
    sys.exit(1)


# I plan to iterate over the network topology and follow each know switch connection
# until the final destination is found

# Until I can create this, I use simple loop and stop when I found the device
for switch in SwitchList:
    # Find Connections to other switches that are not known to the topology
    # e.g. 8 Port unmanaged switches put in by the work force themselves
    # pretty time consuming... thus, probably should not be done during a
    # quick search.
    # switch.identifyPotentialConnection()

    try:
        result = switch.isDeviceConnected(Device)
    except ConnectionError:
        print(f"{switch.address} is not reachable")
        continue

    if  result == NSCheckResult.DeviceDirectlyConnected:
        port = switch.getDevicePort(Device)
        devicemac = str(Device)
        print(f"{devicemac} is connected to port {port} on Switch {switch.address}")

sys.exit(0)
