from dataclasses import dataclass, field


@dataclass(frozen=True)
class GroupTypeDefinition:
    """
    Represents a type of group in Keycloak. This is used to define the allowed structure of groups in Keycloak. For example, a "Region" group type might have a child category "Kanton", which means that under a "Region" group, you can only have groups of type "Kanton".
    
    Attributes:
        type_key: A unique key for this group type, used for lookup and reference.
        display_name: A human-readable name for this group type, used for display purposes.
        allowed_roles: A set of role names that are allowed to be assigned to groups of this type.
        default_roles: A set of role names that should be assigned by default to groups of this type when they are created.
        keycloak_sync: If True, groups of this type will be created/updated in Keycloak. If False, they will only exist in the local model and not be synced to Keycloak. This can be useful for defining abstract group types that are only used for categorization and don't have a direct representation in Keycloak.
        children: A set of ChildCategoryDefinition instances that define the allowed child categories under groups of this type.
        collections: CollectionDefinition instances that are created under every group of this type.
    """
    type_key: str
    display_name: str
    allowed_roles: frozenset[str] = field(default_factory=frozenset)
    default_roles: frozenset[str] = field(default_factory=frozenset)
    keycloak_sync: bool = True
    children: frozenset["ChildCategoryDefinition"] = field(default_factory=frozenset)
    collections: tuple["CollectionDefinition", ...] = field(default_factory=tuple)
    
    
@dataclass(frozen=True)
class ChildCategoryDefinition:
    """
    Represents a category of groups that can be children of a GroupTypeDefinition. This is used to define the allowed structure of groups in Keycloak. For example, a "Region" group type might have a child category "Kanton", which means that under a "Region" group, you can only have groups of type "Kanton".
    
    Attributes:
        key: A unique key for this child category, used for lookup and reference.
        label: A human-readable label for this child category, used for display purposes.
        allowed_types: A set of GroupTypeDefinition.type_key values that are allowed as children in this category.
        create_folder_in_keycloak: If True, a folder will be created in Keycloak for this category. If False, the groups of the allowed types will be assigned directly under the parent group without an intermediate folder.
    """
    key: str
    # Used when creating
    label: str
    allowed_types: frozenset[str]
    # Optional: Whether to create a folder in Keycloak for this category, or just assign the groups directly under the parent.
    create_folder_in_keycloak: bool = True
    # Optional: Whether to enforce that all children of this category must have the same type. If False, children can have any allowed type, but if True, all children must have the same type (which is determined by the first child added).
    stack_same_category: bool = False


@dataclass(frozen=True)
class CollectionDefinition:
    """
    Represents a collection group in Keycloak. A user is assigned to the collection if they have at least one of
    the given roles in the group where the collection is located or in any group below it.
    For example, an "Alle Leitenden" collection on an Abteilung might include the Einheitsleitung roles of all Stufen.

    Attributes:
        key: A unique key for this collection within its group, used for lookup and reference.
        label: The name of the collection group in Keycloak.
        roles: The role values (e.g. "Group::Pfadi::Einheitsleitung") that grant membership in this collection.
    """
    key: str
    label: str
    roles: frozenset[str]
