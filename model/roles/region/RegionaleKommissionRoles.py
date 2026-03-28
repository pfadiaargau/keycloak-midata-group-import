from enum import Enum

from model.groups.MidataGroups import MidataGroups


class RegionaleKommissionRoles(Enum):
    GROUP_TYPE = MidataGroups.REGIONALE_KOMMISSION.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    LEITUNG = GROUP_PREFIX + "Leitung"
    MITGLIED = GROUP_PREFIX + "Mitglied"