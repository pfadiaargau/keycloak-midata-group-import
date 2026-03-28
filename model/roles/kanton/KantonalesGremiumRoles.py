
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class KantonalesGremiumRoles(Enum):
    GROUP_TYPE = MidataGroups.KANTONALES_GREMIUM.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    LEITUNG = GROUP_PREFIX + "Leitung"
    MITGLIED = GROUP_PREFIX + "Mitglied"
    SELBSTREGISTRIERT = GROUP_PREFIX + "Selbstregistriert"