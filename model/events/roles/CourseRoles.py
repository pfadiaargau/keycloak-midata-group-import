from enum import Enum

from .CampRoles import CampRoles
from .EventRoles import EventRoles


class CourseRoles(Enum):
    EVENT_TYPE = "Event::Course"
    EVENT_PREFIX = EVENT_TYPE + "::Role::"
    
    COURSE_LEADER = EVENT_PREFIX + "Leader"
    COURSE_CLASSLEADER = EVENT_PREFIX + "ClassLeader"
    COURSE_HELPER = EVENT_PREFIX + "Helper"
    COURSE_PARTICIPANT = EVENT_PREFIX + "Participant"
    COURSE_SPEAKER = EventRoles.EVENT_SPEAKER.value
    COURSE_COOK = EventRoles.EVENT_COOK.value
    COURSE_LEADER_MOUNTAIN_SECURITY = CampRoles.CAMP_LEADER_MOUNTAIN_SECURITY.value
    COURSE_LEADER_WATER_SECURITY = CampRoles.CAMP_LEADER_WATER_SECURITY.value
    COURSE_LEADER_SNOW_SECURITY = CampRoles.CAMP_LEADER_SNOW_SECURITY.value
        