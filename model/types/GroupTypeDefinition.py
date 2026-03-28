from dataclasses import dataclass, field


@dataclass(frozen=True)
class GroupTypeDefinition:
    type_key: str
    display_name: str
    allowed_roles: frozenset[str] = field(default_factory=frozenset)
    default_roles: frozenset[str] = field(default_factory=frozenset)
    keycloak_sync: bool = True
    children: frozenset["ChildCategoryDefinition"] = field(default_factory=frozenset)
    
    
@dataclass(frozen=True)
class ChildCategoryDefinition:
    key: str
    label: str
    allowed_types: frozenset[str]
    create_folder_in_keycloak: bool = True
    stack_same_category: bool = False