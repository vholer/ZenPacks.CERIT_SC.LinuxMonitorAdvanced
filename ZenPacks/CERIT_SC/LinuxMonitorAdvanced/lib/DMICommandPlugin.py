import re
from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin

class DMICommandPlugin(CommandPlugin):
    """
    A CommandPlugin that parses dmidecode output into hash structure:

    { $handle_id: {
        'id':$handle_id,
        'type':$type,
        'size':$size,
        'name':$name,
        'data': {
            'key1':'value1',
            'key2':'value2',
            ...
    } } }

    example of DMI table content of type 1 (System Information):
    { '0x0100': {
        'id':   '0x0100',
        'type': '1',
        'name': 'System Information',
        'size': '27',
        'data': {
            'SKU Number': 'Not Specified',
            'UUID': 'D07A1E5B-A507-467B-BE2F-F8B10E763B79',
            'Family': 'Not Specified',
            'Serial Number': 'Not Specified',
            'Version': 'Not Specified',
            'Product Name': 'Bochs',
            'Wake-up Type': 'Power Switch',
            'Manufacturer': 'Bochs'
    } } }
    """

    def preprocess(self, results, log):
        myresults=super(DMICommandPlugin,self).preprocess(results,log)
        hre=re.compile('^Handle (0x[a-zA-Z0-9]+), DMI type (\d+), (\d+) bytes$')
        dmidata={}

        # process each section separated by empty line
        for s in myresults.split("\n\n"):
            section=s.split("\n")
            if len(section)<2: continue

            # first two lines in section are metadata:
            # > Handle 0x0010, DMI type 1, 27 bytes
            # > System Information
            handle,name=section.pop(0),section.pop(0)
            match=hre.match(handle)
            if not match: continue

            items={}
            k,v=None,None
            for line in section:
                # multiline values, e.g.:
                # > Flags:
                # >   FPU (Floating-point unit on-chip)
                # >   VME (Virtual mode extension)
                # >   DE (Debugging extension)
                if line.find(':') == -1:
                    if isinstance(v,list):
                        v.append(line.strip())
                    else:
                        v=[line.strip()]

                # common key:value entries, e.g.:
                # > Manufacturer: Intel(R) Corporation
                else:
                    if not k is None:
                        items[k.strip()]=v
                    k,v=line.strip().split(':',1)
                    v=v.strip()
    
            # save last unprocessed item
            if not k is None:
                items[k.strip()]=v
    
            dmidata[match.group(1)] = {
                'id':   match.group(1),
                'type': match.group(2),
                'size': match.group(3),
                'name': name,
                'data': items
            }

        return dmidata
