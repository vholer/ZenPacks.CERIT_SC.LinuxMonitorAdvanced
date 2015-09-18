from Products.ZenRRD.ComponentCommandParser import ComponentCommandParser

class ipmitool_sdr_csv(ComponentCommandParser):
    componentSplit = '\n'
    componentScanValue = 'id'
    componentScanner = '^(?P<component>[^,]+),'
    scanners = [
        r'(?P<celsius>\d+),degrees C,(?P<state>.*)$',
        r'(?P<rpm>\d+),RPM,(?P<state>.*)$',
        r'(?P<percent>[\d\.]+),unspecified,(?P<state>.*)$',
    ]
