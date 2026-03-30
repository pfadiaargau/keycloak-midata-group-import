from enum import Enum

from model.events.EventTypes import EventTypes


class EventRoles(Enum):
    EVENT_TYPE = EventTypes.EVENT.value
    EVENT_PREFIX = EVENT_TYPE + "::Role::"
    
    EVENT_ASSISTANT_LEADER = EVENT_PREFIX + "AssistantLeader"
    EVENT_LEADER = EVENT_PREFIX + "Leader"
    EVENT_COOK = EVENT_PREFIX + "Cook"
    EVENT_HELPER = EVENT_PREFIX + "Helper"
    EVENT_TRESSURER = EVENT_PREFIX + "Tressurer"
    EVENT_SPEAKER = EVENT_PREFIX + "Speaker"
    EVENT_PARTICIPANT = EVENT_PREFIX + "Participant"