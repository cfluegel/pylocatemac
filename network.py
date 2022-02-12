from snmp import snmp_walk, snmp_get
from enum import Enum

import subprocess

from pprint import pprint as pp

class MACAddress():
    _address = None
    _separator = ":"
    _default_separator = ":"

    def __init__(self, MAC=None):
        if MAC:
            self.address = MAC

    @property
    def separator(self):
        return self._separator

    @separator.setter
    def separator(self, newseparator=None):
        if not newseparator:
            raise ValueError()

        if len(newseparator) > 2:
            raise ValueError()

        self._separator = newseparator

    @separator.deleter
    def separator(self):
        self._separator = self._default_separator

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, MAC=None):
        if not isinstance(MAC, (str)):
            raise ValueError()

        if len(MAC.split(":")) != 6:
            raise ValueError()

        self._address = tuple(MAC.split(":"))

    @address.deleter
    def address(self):
        self._address = None

    def convertToOID(self):
        if not isinstance(self.address, (tuple)):
            raise ValueError()

        oid_formatted_mac = str(int("0x"+str(self.address[0]), base=16)) + \
            "." + str(int("0x"+str(self.address[1]), base=16)) + "." + \
            str(int("0x"+str(self.address[2]), base=16)) + "." + \
            str(int("0x"+str(self.address[3]), base=16)) + "." + \
            str(int("0x"+str(self.address[4]), base=16)) + "." + \
            str(int("0x"+str(self.address[5]), base=16))

        return oid_formatted_mac

    def convertFromOID(self, OID=None):
        if not isinstance(OID, (str)):
            raise ValueError()

        splittedOID = OID.split(".")
        if not len(splittedOID) == 6:
            raise ValueError()

        self.address = "{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}".format(
            int(splittedOID[0]),
            int(splittedOID[1]),
            int(splittedOID[2]),
            int(splittedOID[3]),
            int(splittedOID[4]),
            int(splittedOID[5]))

    def __str__(self):
        return self._separator.join(octet for octet in self.address)

    def __eq__(self, other):
        if self.address == other.address:
            return True
        return False


class NSCheckResult(Enum):
    DeviceUnknown = 0
    DeviceOnAnotherSwitch = 1
    DeviceDirectlyConnected = 2
    DeviceOnUnknownSwitch = 3


class NetworkSwitch():
    _ipaddress = None
    _snmp_community = ""
    _snmp_base_address = '1.3.6.1.2.1.17.4.3.1.2.'

    # List of known and suspected ports with another switch
    # Format:
    #         _connections[<port>] = NetworkSwitch()
    #         _potential_connections = set()

    _connections = dict()
    _potential_connections = set()

    def __init__(self, IPAddress=None, SNMPCommunity="public"):
        self._ipaddress = IPAddress
        self._snmp_community = SNMPCommunity

        if not self._isReachable():
            raise ConnectionError("Switch is not reachable")

    def _isReachable(self):
        command = ["ping","-q","-c","1","-W","2",self._ipaddress]

        result = subprocess.run(command,capture_output=True)
        if result.returncode == 0:
            return True
        return False

    @property
    def address(self):
        return self._ipaddress

    def identifyPotentialConnection(self, output_result=False):
        localtemp = dict()
        for result in snmp_walk(self._ipaddress, "1.3.6.1.2.1.17.4.3.1.2.",
                                self._snmp_community):
            if str(result[1]) not in localtemp.keys():
                localtemp[str(result[1])] = 1
            else:
                localtemp[str(result[1])] += 1

        for key, value in localtemp.items():
            if value >= 2 and key not in self._connections.keys():
                self._potential_connections.add(key)

        # This can be used during the creation of the topology file
        if output_result:
            print()
            print(f"Switch with the IP {self._ipaddress} has the following potentical connections:"  )
            pp(self._potential_connections)
            print()

    def addConnection(self, port=None, nextswitch=None):
        if not isinstance(nextswitch, (NetworkSwitch)):
            raise ValueError()
        if not isinstance(port, (int, str)):
            raise ValueError()

        switchport = str(port)
        self._connections[switchport] = nextswitch

    def getDevicePort(self, mac=None):
        if not mac:
            raise ValueError()
        if not isinstance(mac, (MACAddress)):
            raise ValueError()

        checkresult = self.isDeviceConnected(mac)
        if checkresult == NSCheckResult.DeviceDirectlyConnected:
            return snmp_get(self._ipaddress,
                            self._snmp_base_address + mac.convertToOID(),
                            self._snmp_community)[1]

        if checkresult == NSCheckResult.DeviceOnAnotherSwitch:
            result = snmp_get(self._ipaddress,
                              self._snmp_base_address + mac.convertToOID(),
                              self._snmp_community)
            return self._connections[result[1]]

        # TODO: For now, just return the port of this switch as information
        #       where the device is connected to.
        #       This is not fully acurate
        if checkresult == NSCheckResult.DeviceOnUnknownSwitch:
            return snmp_get(self._ipaddress,
                            self._snmp_base_address + mac.convertToOID(),
                            self._snmp_community)[1]

    def isDeviceConnected(self, mac=None):
        if not mac:
            raise ValueError()
        if not isinstance(mac, (MACAddress)):
            raise ValueError()

        result = snmp_get(self._ipaddress,
                          self._snmp_base_address + mac.convertToOID(),
                          self._snmp_community)

        if not result:
            return NSCheckResult.DeviceUnknown

        if not result[1]:
            return NSCheckResult.DeviceUnknown

        if str(result[1]) in self._connections.keys():
            return NSCheckResult.DeviceOnAnotherSwitch

        if str(result[1]) in self._potential_connections:
            return NSCheckResult.DeviceOnUnknownSwitch

        # TODO: Practically this is the else clause.
        #       so it should be enough to assume that it is connected directly
        return NSCheckResult.DeviceDirectlyConnected


if __name__ == "__main__":
    pass