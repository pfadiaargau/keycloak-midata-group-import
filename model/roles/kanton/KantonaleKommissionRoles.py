from enum import Enum

from model.groups.MidataGroups import MidataGroups


class KantonaleKommissionRoles(Enum):
    GROUP_TYPE = MidataGroups.KANTONALE_KOMMISSION.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    LEITUNG = GROUP_PREFIX + "Leitung"
    MITGLIED = GROUP_PREFIX + "Mitglied"