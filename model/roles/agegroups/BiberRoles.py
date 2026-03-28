
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class BiberRoles(Enum):
    GROUP_TYPE = MidataGroups.BIBER.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    EINHEITSLEITUNG = GROUP_PREFIX + "Einheitsleitung"
    MITLEITUNG = GROUP_PREFIX + "Mitleitung"
    ADRESSVERWALTUNG = GROUP_PREFIX + "Adressverwaltung"
    BIBER = GROUP_PREFIX + "Biber"