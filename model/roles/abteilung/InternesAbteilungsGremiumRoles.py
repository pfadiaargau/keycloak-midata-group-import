
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class InternesAbteilungsGremiumRoles(Enum):
    GROUP_TYPE = MidataGroups.INTERNES_ABTEILUNGS_GREMIUM.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    LEITUNG = GROUP_PREFIX + "Leitung"
    MITGLIED = GROUP_PREFIX + "Mitglied"
