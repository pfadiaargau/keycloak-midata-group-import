from enum import Enum

from model.groups.MidataGroups import MidataGroups


class SilverscoutsRegionRoles(Enum):
    GROUP_TYPE = MidataGroups.SILVERSCOUTS_REGION.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    LEITUNG = GROUP_PREFIX + "Leitung"
    MITGLIED = GROUP_PREFIX + "Mitglied"