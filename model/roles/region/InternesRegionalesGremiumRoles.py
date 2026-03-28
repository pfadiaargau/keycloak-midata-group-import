from enum import Enum

from model.groups.MidataGroups import MidataGroups


class InternesRegionalesGremiumRoles(Enum):
    GROUP_TYPE = MidataGroups.INTERNES_REGIONALES_GREMIUM.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    LEITUNG = GROUP_PREFIX + "Leitung"
    MITGLIED = GROUP_PREFIX + "Mitglied"