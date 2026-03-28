from dataclasses import dataclass, field


@dataclass(frozen=True)
class HierarchyNode:
    key: str
    label: str
    allowed_group_types: frozenset[str] = field(default_factory=frozenset)
    create_folder_in_keycloak: bool = True
    children: tuple["HierarchyNode", ...] = ()
    stack_on_same_category: bool = False