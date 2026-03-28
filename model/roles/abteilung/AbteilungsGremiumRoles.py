
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class AbteilungsGremiumRoles(Enum):
    GROUP_TYPE = MidataGroups.ABTEILUNGS_GREMIUM.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    LEITUNG = GROUP_PREFIX + "Leitung"
    MITGLIED = GROUP_PREFIX + "Mitglied"
    SELBSTREGISTRIERT = GROUP_PREFIX + "Selbstregistriert"