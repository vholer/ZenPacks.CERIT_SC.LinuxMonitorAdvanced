from Products.ZenRRD.ComponentCommandParser import ComponentCommandParser

class ipmitool_sdr(ComponentCommandParser):
    componentSplit = '\n'
    componentScanValue = 'id'
    componentScanner = '^(?P<component>[^,]+),'
    scanners = [
        r'(?P<celsius>\d+),degrees C,(?P<status>.*)$',
        r'(?P<rpm>\d+),RPM,(?P<status>.*)$',
    ]
