from Products.ZenRRD.ComponentCommandParser import ComponentCommandParser

class ipmitool_sdr(ComponentCommandParser):
    componentSplit = '\n'
    componentScanValue = 'snmpindex'
    componentScanner = '^[^|]+\|\s*0*(?P<component>[0-9a-fA-F]+)h\s*\|'
    scanners = [
        r'\|\s*(?P<celsius>\d+) degrees C\s*$',
        r'\|\s*(?P<rpm>\d+) RPM\s*$',
    ]
