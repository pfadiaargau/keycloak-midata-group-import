from enum import Enum


class CampRoles(Enum):
    EVENT_TYPE = "Event::Camp"
    EVENT_PREFIX = EVENT_TYPE + "::Role::"
    
    CAMP_ASSISTANT_LEADER = EVENT_PREFIX + "AssistantLeader"
    CAMP_ABTEILUNGSLEITUNG = EVENT_PREFIX + "Abteilungsleitung"
    CAMP_COACH = EVENT_PREFIX + "Coach"
    CAMP_LEADER = EVENT_PREFIX + "Leader"
    CAMP_HELPER = EVENT_PREFIX + "Helper"
    CAMP_LEADER_MOUNTAIN_SECURITY = EVENT_PREFIX + "LeaderMountainSecurity"
    CAMP_LEADER_WATER_SECURITY = EVENT_PREFIX + "LeaderWaterSecurity"
    CAMP_LEADER_SNOW_SECURITY = EVENT_PREFIX + "LeaderSnowSecurity"  
    CAMP_PARTICIPANT = EVENT_PREFIX + "Participant"