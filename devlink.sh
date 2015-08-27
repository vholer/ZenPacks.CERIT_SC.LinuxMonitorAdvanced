#!/bin/bash
cd $(dirname $0)/..
serviced service run zope zenpack uninstall ZenPacks.CERIT_SC.LinuxMonitorAdvanced
serviced service attach zope rm -r -f /var/zenoss/ZenPackSource/ZenPacks.CERIT_SC.LinuxMonitorAdvanced
serviced service attach zope rm -r -f /var/zenoss/ZenPacks/ZenPacks.CERIT-SC.LinuxMonitorAdvanced.egg-link
serviced service restart Zenoss.core
serviced service run zope zenpack link ZenPacks.CERIT_SC.LinuxMonitorAdvanced
serviced service restart Zenoss.core
