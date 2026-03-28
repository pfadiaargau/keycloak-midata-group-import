
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class PioRoles(Enum):
    GROUP_TYPE = MidataGroups.PIO.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    EINHEITSLEITUNG = GROUP_PREFIX + "Einheitsleitung"
    MITLEITUNG = GROUP_PREFIX + "Mitleitung"
    ADRESSVERWALTUNG = GROUP_PREFIX + "Adressverwaltung"
    PIO = GROUP_PREFIX + "Pio"