from enum import Enum

from model.groups.MidataGroups import MidataGroups


class RootRoles(Enum):
    GROUP_TYPE = MidataGroups.ROOT.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    ADMIN = GROUP_PREFIX + "Admin"    