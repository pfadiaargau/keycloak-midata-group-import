
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class RegionaleRoverRoles(Enum):
    GROUP_TYPE = MidataGroups.REGIONALE_ROVER.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    EINHEITSLEITUNG = GROUP_PREFIX + "Einheitsleitung"
    MITLEITUNG = GROUP_PREFIX + "Mitleitung"
    ADRESSVERWALTUNG = GROUP_PREFIX + "Adressverwaltung"
    ROVER = GROUP_PREFIX + "Rover"