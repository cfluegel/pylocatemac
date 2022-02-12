from pysnmp.hlapi import *
from pprint import pprint as pp


def snmp_walk(address=None, oid=None, community ="public"):
    # OID if Mac Address Table: '1.3.6.1.2.1.17.4.3.1.2.'
    if not oid:
        raise ValueError()
    if not isinstance(oid, (str)):
        raise ValueError()

    if not address:
        raise ValueError()
    if not isinstance(address, (str)):
        raise ValueError()

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
            raise Exception(f"{errorIndication}")

        for varBind in varBinds:
            # print(' = '.join([x.prettyPrint() for x in varBind]))
            _oid=".".join(str(x) for x in varBind[0].getOid().asTuple())
            # ausgabe vorbereiten
            RetTable.append( (_oid, varBind[1]._value ) )
    return RetTable

def snmp_get(address=None, oid=None, community="public"):
    if not oid:
        return ValueError()
    if not isinstance(oid, (str)):
        raise ValueError()
    if not address:
        return ValueError()

    result = getCmd(SnmpEngine(),
                    CommunityData(community),
                    UdpTransportTarget((str(address), 161)),
                    ContextData(),
                    ObjectType(ObjectIdentity(str(oid))))
    try:
        _result = next(result)[3][0]
    except IndexError:
        _result = None

    if _result:
        return ( ".".join(str(x) for x in _result[0].getOid().asTuple()), _result[1]._value )

    return None

if __name__ == "__main__":
    pass
