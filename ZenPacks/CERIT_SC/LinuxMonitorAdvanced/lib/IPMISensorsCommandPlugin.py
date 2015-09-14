import re
from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin

class IPMISensorsCommandPlugin(CommandPlugin):
    """
    A CommandPlugin parses ipmitool sensor/sdr output into hash structure, e.g.:

    { '2c': {
        'id':       '2c',
        'name':     'Ambient Temp',
        'entityId': '12.1',
        'entity':   'Front Panel Board',
        'dataType': 'analog',
        'type':     'Temperature',
        'value':    '25',
        'units':    'degrees C',
        'state':    'ok',
        'lowerNC':  'na',
        'lowerC':   'na',
        'lowerNR':  'na',
        'upperNC':  '38.000',
        'upperC':   '41.000',
        'upperNR':  '45.000',
        'other': {
            'Assertion Events': '',
            'Assertions Enabled': 'unc+ ucr+ unr+',
            'Deassertions Enabled': 'unc+ ucr+ unr+',
        }
    }
    """

    sensor_re = (
        re.compile('^Sensor ID\s*: (?P<name>.+) \(0x(?P<id>[0-9a-fA-F]+)\)$'),
        re.compile('^(?P<name>[^:]+) \(0x(?P<id>[0-9a-fA-F]+)\)$'), #for split by re
        re.compile('^\s+Entity ID\s*: (?P<entityId>[\d\.]+) \((?P<entity>.+)\)$'),
        re.compile('^\s+Sensor Type \((?P<dataType>Analog|Discrete)\)\s*: (?P<type>.*)$'),
        re.compile('^\s+Sensor Reading\s*: (?P<value>[\d\.]+) \(\+/- [\d\.]+\) (?P<units>.*)$'),
    )

    sensor_keys = {
        'ENTITY ID': 'entityId', 
        'SENSOR READING': 'value',
        'STATUS': 'state',
        'LOWER NON-CRITICAL': 'lowerNC',
        'LOWER CRITICAL': 'lowerC',
        'LOWER NON-RECOVERABLE': 'lowerNR',
        'UPPER NON-CRITICAL': 'upperNC',
        'UPPER CRITICAL': 'upperC',
        'UPPER NON-RECOVERABLE': 'upperNR',
    }

    def preprocess(self, results, log):
        myresults = super(IPMISensorsCommandPlugin, self).preprocess(results, log)

        data = {}

        # process each section separated by empty line
        for section in re.split('Sensor ID\s+:\s*', myresults.strip()):
            if not section.strip(): 
                continue

            last_other = None
            sensor = {'other': {}}
            for line in section.split("\n"):
                # match RE (sensor_re)
                match = None
                for sre in self.sensor_re:
                    match = sre.match(line)
                    if match:
                        sensor.update(match.groupdict())
                        last_other = None
                        break

                if not match: 
                    if line.find(':') == -1:
                        if last_other:
                            sensor['other'][last_other] += '\n'+line.strip()
                        continue
                    last_other = None

                    k, v = line.strip().split(':', 1)
                    k = k.strip()
                    v = v.strip()

                    # match translation table sensor_keys
                    if self.sensor_keys.has_key(k.upper()):
                        sensor[self.sensor_keys[k.upper()]] = v
                    else:
                        sensor['other'][k] = v
                        last_other = k

            if sensor.has_key('id'):
                if sensor.has_key('dataType'):
                    sensor['dataType'] = sensor['dataType'].lower()
                sensor['id'] = sensor['id'].lower()
                data[sensor['id']] = sensor

        return data
