from dataclasses import dataclass, field


@dataclass(frozen=True)
class EventTypeDefinition:
    """
    Represents a type of event in the Midata system. This is used to define the allowed structure of events in Midata. For example, a "Course" event type might have specific roles and permissions associated with it.
    
    Attributes:
        type_key: A unique key for this event type, used for lookup and reference.
        display_name: A human-readable name for this event type, used for display purposes.
        allowed_roles: A set of role names that are allowed to be assigned to events of this type.
        default_roles: A set of role names that should be assigned by default to events of this type when they are created.
    """
    type_key: str
    display_name: str
    allowed_roles: frozenset[str] = field(default_factory=frozenset)
    categories: tuple["EventRoleCategoryDefinition", ...] = field(default_factory=tuple)
    
    
    
@dataclass(frozen=True)
class EventRoleCategoryDefinition:
    """
    Represents a category of event roles in the Midata system. This is used to define the allowed structure of event roles in Midata. For example, a "Course" event type might have specific roles and permissions associated with it.
    
    Attributes:
        key: A unique key for this event role category, used for lookup and reference.
        label: A human-readable label for this event role category, used for display purposes.
        event_roles: A set of EventTypeDefinition.type_key values that are allowed in this category.
    """
    key: str
    label: str
    event_roles: frozenset[str] = field(default_factory=frozenset)