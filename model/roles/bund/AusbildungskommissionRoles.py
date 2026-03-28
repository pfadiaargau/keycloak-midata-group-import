
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class AusbildungskommissionRoles(Enum):
    GROUP_TYPE = MidataGroups.AUSBILDUNGSKOMMISSION.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    MITGLIED = GROUP_PREFIX + "Mitglied"