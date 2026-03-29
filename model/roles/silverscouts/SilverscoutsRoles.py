from enum import Enum

from model.groups.MidataGroups import MidataGroups


class SilverscoutsRoles(Enum):
    GROUP_TYPE = MidataGroups.SILVERSCOUTS.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    VERANTWORTUNG = GROUP_PREFIX + "Verantwortung"
    LESEZUGRIFF = GROUP_PREFIX + "Lesezugriff"
    POWER_USER = GROUP_PREFIX + "PowerUser"