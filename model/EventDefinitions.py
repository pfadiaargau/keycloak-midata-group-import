from model.events.EventTypes import EventTypes
from model.events.roles import CampRoles, CourseRoles, EventRoles
from model.events.roles.registry import EVENT_TYPE_ROLES
from model.types.EventTypeDefinition import (EventRoleCategoryDefinition,
                                             EventTypeDefinition)

EVENT_DEFINITIONS = {
    EventTypes.CAMP.value: EventTypeDefinition(
        type_key=EventTypes.CAMP.value,
        display_name="Lager",
        allowed_roles=EVENT_TYPE_ROLES.get(EventTypes.CAMP.value, frozenset()),
        categories=(
            EventRoleCategoryDefinition(
                key="camp_leader",
                label="Leitung",
                event_roles=frozenset({
                    CampRoles.CAMP_LEADER.value,
                    CampRoles.CAMP_ASSISTANT_LEADER.value,
                    CampRoles.CAMP_LEADER_MOUNTAIN_SECURITY.value,
                    CampRoles.CAMP_LEADER_WATER_SECURITY.value,
                    CampRoles.CAMP_LEADER_SNOW_SECURITY.value,
                }),
            ),
            EventRoleCategoryDefinition(
                key="camp_supervision",
                label="Betreuung",
                event_roles=frozenset({
                    CampRoles.CAMP_ABTEILUNGSLEITUNG.value,
                    CampRoles.CAMP_COACH.value,
                }),
            ),
            EventRoleCategoryDefinition(
                key="camp_participants",
                label="Teilnehmende",
                event_roles=frozenset({
                    CampRoles.CAMP_PARTICIPANT.value,
                }),
            ),

        ),
    ),
    EventTypes.COURSE.value: EventTypeDefinition(
        type_key=EventTypes.COURSE.value,
        display_name="Kurs",
        allowed_roles=EVENT_TYPE_ROLES.get(EventTypes.COURSE.value, frozenset()),
        categories=(
            EventRoleCategoryDefinition(
                key="course_leader",
                label="Leitung",
                event_roles=frozenset({
                    CourseRoles.COURSE_LEADER.value,
                    CourseRoles.COURSE_CLASSLEADER.value,
                    CourseRoles.COURSE_HELPER.value,
                    CourseRoles.COURSE_LEADER_MOUNTAIN_SECURITY.value,
                    CourseRoles.COURSE_LEADER_WATER_SECURITY.value,
                    CourseRoles.COURSE_LEADER_SNOW_SECURITY.value,
                }),
            ),
            EventRoleCategoryDefinition(
                key="course_participants",
                label="Teilnehmende",
                event_roles=frozenset({
                    CourseRoles.COURSE_PARTICIPANT.value,
                }),
            ),
        ),
    ),
    "events": EventTypeDefinition(
        type_key="events",
        display_name="Anlässe",
        allowed_roles=EVENT_TYPE_ROLES.get(EventTypes.EVENT.value, frozenset()),
        categories=(
            EventRoleCategoryDefinition(
                key="event_leader",
                label="Leitung",
                event_roles=frozenset({
                    CampRoles.CAMP_LEADER.value,
                    CampRoles.CAMP_ASSISTANT_LEADER.value,
                    CampRoles.CAMP_LEADER_MOUNTAIN_SECURITY.value,
                    CampRoles.CAMP_LEADER_WATER_SECURITY.value,
                    CampRoles.CAMP_LEADER_SNOW_SECURITY.value,
                    
                    CourseRoles.COURSE_LEADER.value,
                    CourseRoles.COURSE_CLASSLEADER.value,
                    CourseRoles.COURSE_HELPER.value,
                    CourseRoles.COURSE_LEADER_MOUNTAIN_SECURITY.value,
                    CourseRoles.COURSE_LEADER_WATER_SECURITY.value,
                    CourseRoles.COURSE_LEADER_SNOW_SECURITY.value,
                    
                    EventRoles.EVENT_LEADER.value,
                    EventRoles.EVENT_ASSISTANT_LEADER.value,
                    EventRoles.EVENT_TRESSURER.value,
                }),
            ),
            EventRoleCategoryDefinition(
                key="event_participants",
                label="Teilnehmende",
                event_roles=frozenset({
                    CampRoles.CAMP_PARTICIPANT.value,
                    CourseRoles.COURSE_PARTICIPANT.value,
                    EventRoles.EVENT_PARTICIPANT.value,
                }),
            ),
        ),
    ),
    "default": EventTypeDefinition(
        type_key="default",
        display_name="Anlass",
        allowed_roles=frozenset(EVENT_TYPE_ROLES.get(EventTypes.EVENT.value, frozenset())),
        categories=(
            EventRoleCategoryDefinition(
                key="event_leader",
                label="Leitung",
                event_roles=frozenset({
                    EventRoles.EVENT_LEADER.value,
                    EventRoles.EVENT_ASSISTANT_LEADER.value,
                    EventRoles.EVENT_TRESSURER.value,
                }),
            ),
            EventRoleCategoryDefinition(
                key="event_participants",
                label="Teilnehmende",
                event_roles=frozenset({
                    EventRoles.EVENT_PARTICIPANT.value,
                }),
            ),
        ),
    ),
}