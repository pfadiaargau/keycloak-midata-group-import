
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class PfadiRoles(Enum):
    GROUP_TYPE = MidataGroups.PFADI.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    EINHEITSLEITUNG = GROUP_PREFIX + "Einheitsleitung"
    MITLEITUNG = GROUP_PREFIX + "Mitleitung"
    ADRESSVERWALTUNG = GROUP_PREFIX + "Adressverwaltung"
    LEITPFADI = GROUP_PREFIX + "Leitpfadi"
    PFADI = GROUP_PREFIX + "Pfadi"