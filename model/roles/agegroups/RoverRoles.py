
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class RoverRoles(Enum):
    GROUP_TYPE = MidataGroups.ABTEILUNGS_ROVER.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    EINHEITSLEITUNG = GROUP_PREFIX + "Einheitsleitung"
    MITLEITUNG = GROUP_PREFIX + "Mitleitung"
    ADRESSVERWALTUNG = GROUP_PREFIX + "Adressverwaltung"
    ROVER = GROUP_PREFIX + "Rover"