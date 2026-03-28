
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class EhemaligeRoles(Enum):
    GROUP_TYPE = MidataGroups.EHEMALIGE.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    MITGLIED = GROUP_PREFIX + "Mitglied"    