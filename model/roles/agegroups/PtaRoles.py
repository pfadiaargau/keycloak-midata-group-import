
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class PtaRoles(Enum):
    GROUP_TYPE = MidataGroups.PTA.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    EINHEITSLEITUNG = GROUP_PREFIX + "Einheitsleitung"
    MITLEITUNG = GROUP_PREFIX + "Mitleitung"
    ADRESSVERWALTUNG = GROUP_PREFIX + "Adressverwaltung"
    MITGLIED = GROUP_PREFIX + "Mitglied"