from pysnmp.hlapi import *
from pprint import pprint as pp


def snmp_walk(address=None, oid=None, community ="public"):
    # OID if Mac Address Table: '1.3.6.1.2.1.17.4.3.1.2.'
    if not oid:
        return None

    if not address:
        return None

    RetTable = list()
    for (errorIndication,
        errorStatus,
        errorIndex,
        varBinds) in nextCmd(SnmpEngine(),
                            CommunityData( community ),
                            UdpTransportTarget((str(address), 161)),
                            ContextData(),
                            ObjectType(ObjectIdentity(str(oid))),
                            lexicographicMode=False):

        if errorIndication:
            raise Exception(f"Errorstatus ist {errorStatus}")

        for varBind in varBinds:
            # print(' = '.join([x.prettyPrint() for x in varBind]))
            _oid="." + ".".join(str(x) for x in varBind[0].getOid().asTuple())
            # ausgabe vorbereiten
            RetTable.append( (_oid, varBind[1]._value ) )
    return RetTable

def snmp_get(address=None, oid=None, community="public"):
    if not oid:
        return None

    if not address:
        return None

    result = getCmd(SnmpEngine(),
                    CommunityData(community),
                    UdpTransportTarget((str(address), 161)),
                    ContextData(),
                    ObjectType(ObjectIdentity(str(oid))))
    _result = next(result)[3][0]
    return ( "." + ".".join(str(x) for x in _result[0].getOid().asTuple()), _result[1]._value )

if __name__ == "__main__":
    pp(snmp_walk("192.168.42.10", '1.3.6.1.2.1.17.4.3.1.2.', "home"))
    pp(snmp_get("192.168.42.10", '1.3.6.1.2.1.17.4.3.1.2.244.109.4.172.103.31', "home"))