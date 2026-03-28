
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class WoelfeRoles(Enum):
    GROUP_TYPE = MidataGroups.WOELFE.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    EINHEITSLEITUNG = GROUP_PREFIX + "Einheitsleitung"
    MITLEITUNG = GROUP_PREFIX + "Mitleitung"
    ADRESSVERWALTUNG = GROUP_PREFIX + "Adressverwaltung"
    LEITWOLF = GROUP_PREFIX + "Leitwolf"
    WOLF = GROUP_PREFIX + "Wolf"