
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class ElternratRoles(Enum):
    GROUP_TYPE = MidataGroups.ELTERNRAT.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    PRAESIDIUM = GROUP_PREFIX + "Praesidium"
    MITGLIED = GROUP_PREFIX + "Mitglied"