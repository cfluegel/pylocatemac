from snmp import snmp_walk, snmp_get
from enum import Enum

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
    def separator(self, newseparator = None):
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
        if not isinstance(MAC,(str)):
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

        oid_formatted_mac = str(int("0x"+str(self.address[0]), base=16)) + "." + \
            str(int("0x"+str(self.address[1]), base=16)) + "." + \
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

        self.address = "{:02X}:{:02X}:{:02X}:{:02X}:{:02X}:{:02X}".format(int(splittedOID[0]), \
            int(splittedOID[1]), \
            int(splittedOID[2]), \
            int(splittedOID[3]), \
            int(splittedOID[4]), \
            int(splittedOID[5]))

    def __str__(self):
        return self._separator.join(octet for octet in self.address)

    def __eq__(self, other):
        if self.address == other.address:
            return True
        return False

class NSCheckResult(Enum):
    DEVICEUNKNOWN = 0
    DEVICEONOTHERSWITCH = 1
    DEVICECONNECTED = 2

class NetworkSwitch():
    _address = None
    _snmp_community = "public"
    _snmp_base_address = '1.3.6.1.2.1.17.4.3.1.2.'
    _connections = dict()

    def __init__(self, IPAddress=None, SNMPCommunity="public"):
        self._address = IPAddress
        self._snmp_community = SNMPCommunity

    def __iter__(self):
        return self

    def __next__(self):
        # TODO: Implement an iteration over all network switches...
        raise StopIteration()

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
        if checkresult == NSCheckResult.DEVICECONNECTED:
            return snmp_get(self._address, self._snmp_base_address + mac.convertToOID(), self._snmp_community)[1]
        if checkresult == NSCheckResult.DEVICEONOTHERSWITCH:
            result = snmp_get(self._address, self._snmp_base_address + mac.convertToOID(), self._snmp_community)
            return self._connections[ result[1] ]
        return None

    def isDeviceConnected(self, mac=None):
        if not mac:
            raise ValueError()
        if not isinstance(mac, (MACAddress)):
            raise ValueError()
        result = snmp_get(self._address, self._snmp_base_address + mac.convertToOID(), self._snmp_community)

        if result[1] and result[1] in self._connections.keys():
            return NSCheckResult.DEVICEONOTHERSWITCH
        if result[1] and result[1] not in self._connections.keys():
            return NSCheckResult.DEVICECONNECTED
        return NSCheckResult.DEVICEUNKNOWN

if __name__ == "__main__":
    from pprint import pprint as pp

    # mac1 = MACAddress("48:2a:e3:30:ac:64")
    # mac2 = MACAddress("04:d4:c4:21:d6:1f")
    # mac3 = MACAddress()
    # print(mac1)
    # print(mac1.convertToOID())
    # print(mac1.address)

    # print(mac2.convertToOID())
    # mac3.convertFromOID("4.212.196.33.214.31")
    # print(mac3)

    homeswitch = NetworkSwitch("192.168.42.10", "home")
    testdevice = MACAddress("04:d4:c4:21:d6:1e")
    pp(homeswitch.isDeviceConnected(testdevice))
