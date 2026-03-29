from model.groups.MidataGroups import MidataGroups
from model.roles.abteilung import AbteilungRoles
from model.roles.agegroups import (BiberRoles, PfadiRoles, PioRoles, PtaRoles,
                                   RoverRoles, WoelfeRoles)
from model.roles.bund import (BundesGremiumRoles, BundesKommissionRoles,
                              BundRoles)
from model.roles.kanton import (InternesKantonalesGremiumRoles,
                                KantonaleKommissionRoles,
                                KantonalesGremiumRoles, KantonalverbandRoles)
from model.roles.other import RootRoles
from model.roles.region import (InternesRegionalesGremiumRoles,
                                RegionaleKommissionRoles, RegionaleRoverRoles,
                                RegionalesGremiumRoles)
from model.roles.registry import GROUP_TYPE_ROLES
from model.types.GroupTypeDefinition import (ChildCategoryDefinition,
                                             GroupTypeDefinition)


def build_agegroup_definition(
    type_key: str,
    display_name: str,
    address_role: str,
    co_lead_role: str,
) -> GroupTypeDefinition:
    return GroupTypeDefinition(
        type_key=type_key,
        display_name=display_name,
        allowed_roles=GROUP_TYPE_ROLES.get(type_key, frozenset()),
        default_roles=frozenset({
            address_role,
            co_lead_role,
        }),
        children=(
            ChildCategoryDefinition(
                key="committees",
                label="Gremien",
                allowed_types=frozenset({
                    MidataGroups.ABTEILUNGS_GREMIUM.value,
                    MidataGroups.INTERNES_ABTEILUNGS_GREMIUM.value,
                }),
            ),
            
            ChildCategoryDefinition(
                key="agegroups",
                label="Stufen",
                allowed_types=frozenset({
                    MidataGroups.BIBER.value,
                    MidataGroups.WOELFE.value,
                    MidataGroups.PFADI.value,
                    MidataGroups.PIO.value,
                    MidataGroups.ABTEILUNGS_ROVER.value,
                    MidataGroups.PTA.value,
                }),
                create_folder_in_keycloak=False,
                stack_same_category=True,
            ),
        ),
    )
    
def build_committee_definition(
    type_key: str,
    display_name: str,
    allowed_types: frozenset[str],
) -> GroupTypeDefinition:
    return GroupTypeDefinition(
        type_key=type_key,
        display_name=display_name,
        allowed_roles=GROUP_TYPE_ROLES.get(type_key, frozenset()),
        default_roles=frozenset(),
        children=({
            ChildCategoryDefinition(
                key="committees",
                label="Gremien",
                allowed_types=allowed_types,
                create_folder_in_keycloak=False,
                stack_same_category=True,
            ),
        }),
    )

GROUP_DEFINITIONS = {
    MidataGroups.BUND.value: GroupTypeDefinition(
        type_key=MidataGroups.BUND.value,
        display_name="Bund",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.BUND.value, frozenset()),
        default_roles=frozenset({
            BundRoles.ADRESSVERWALTUNG.value,
            BundRoles.SEKRETARIAT.value,
            BundRoles.GESCHAEFTSLEITUNG.value,
        }),
        children=(
            ChildCategoryDefinition(
                key="committees",
                label="Gremien",
                allowed_types=frozenset({
                    MidataGroups.BUNDES_GREMIUM.value,
                }),
                create_folder_in_keycloak=True,
                stack_same_category=True,
            ),
            ChildCategoryDefinition(
                key="comissions",
                label="Kommissionen",
                allowed_types=frozenset({
                    MidataGroups.BUNDES_KOMMISSION.value,
                }),
                create_folder_in_keycloak=True,
                stack_same_category=True,
            ),
            ChildCategoryDefinition(
                key="training_comissions",
                label="Ausbildungskommissionen",
                allowed_types=frozenset({
                    MidataGroups.AUSBILDUNGSKOMMISSION.value,
                }),
                create_folder_in_keycloak=True,
                stack_same_category=True,
            ),
            ChildCategoryDefinition(
                key="kantonalverbaende",
                label="Kantonalverbände",
                allowed_types=frozenset({
                    MidataGroups.KANTONALVERBAND.value,
                }),
                create_folder_in_keycloak=True,
            ),
        ),
    ),

    MidataGroups.KANTONALVERBAND.value: GroupTypeDefinition(
        type_key=MidataGroups.KANTONALVERBAND.value,
        display_name="Kantonalverband",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.KANTONALVERBAND.value, frozenset()),
        default_roles=frozenset({
            KantonalverbandRoles.ADRESSVERWALTUNG.value,
            KantonalverbandRoles.SEKRETARIAT.value,
            KantonalverbandRoles.KANTONSLEITUNG.value,
            KantonalverbandRoles.PRAESIDIUM.value,
            KantonalverbandRoles.WEBMASTER.value,
        }),
        children=(
            ChildCategoryDefinition(
                key="committees",
                label="Gremien",
                allowed_types=frozenset({
                    MidataGroups.KANTONALES_GREMIUM.value,
                    MidataGroups.INTERNES_KANTONALES_GREMIUM.value,
                }),
                create_folder_in_keycloak=True,
                stack_same_category=True,
            ),
            ChildCategoryDefinition(
                key="comissions",
                label="Kommissionen",
                allowed_types=frozenset({
                    MidataGroups.KANTONALE_KOMMISSION.value,
                }),
                create_folder_in_keycloak=True,
                stack_same_category=True,
            ),
            ChildCategoryDefinition(
                key="regions",
                label="Regionen",
                allowed_types=frozenset({
                    MidataGroups.REGION.value,
                }),
                create_folder_in_keycloak=True,
            ),
            ChildCategoryDefinition(
                key="scout_groups",
                label="Abteilungen",
                allowed_types=frozenset({
                    MidataGroups.ABTEILUNG.value,
                }),
                create_folder_in_keycloak=True,
            ),
        ),
    ),
    
    MidataGroups.ABTEILUNG.value: GroupTypeDefinition(
        type_key=MidataGroups.ABTEILUNG.value,
        display_name="Abteilung",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.ABTEILUNG.value, frozenset()),
        default_roles=frozenset({
            AbteilungRoles.ADRESSVERWALTUNG.value,
            AbteilungRoles.SEKRETARIAT.value,
        }),
        children=(
                ChildCategoryDefinition(
                    key="committees",
                    label="Gremien",
                    allowed_types=frozenset({
                        MidataGroups.ABTEILUNGS_GREMIUM.value,
                        MidataGroups.INTERNES_ABTEILUNGS_GREMIUM.value,
                    }),
                    create_folder_in_keycloak=True,
                    stack_same_category=True,
                ),
                ChildCategoryDefinition(
                    key="agegroups",
                    label="Stufen",
                    allowed_types=frozenset({
                        MidataGroups.BIBER.value,
                        MidataGroups.WOELFE.value,
                        MidataGroups.PFADI.value,
                        MidataGroups.PIO.value,
                        MidataGroups.ABTEILUNGS_ROVER.value,
                        MidataGroups.PTA.value,
                    }),
                    create_folder_in_keycloak=True,
                    stack_same_category=True,
                ),
            ),
    ),
    
    MidataGroups.BIBER.value: build_agegroup_definition(
        type_key=MidataGroups.BIBER.value,
        display_name="Biber",
        address_role=BiberRoles.ADRESSVERWALTUNG.value,
        co_lead_role=BiberRoles.MITLEITUNG.value,
    ),
    MidataGroups.WOELFE.value: build_agegroup_definition(
        type_key=MidataGroups.WOELFE.value,
        display_name="Wölfe",
        address_role=WoelfeRoles.ADRESSVERWALTUNG.value,
        co_lead_role=WoelfeRoles.MITLEITUNG.value,
    ),
    MidataGroups.PFADI.value: build_agegroup_definition(
        type_key=MidataGroups.PFADI.value,
        display_name="Pfadi",
        address_role=PfadiRoles.ADRESSVERWALTUNG.value,
        co_lead_role=PfadiRoles.MITLEITUNG.value,
    ),
    MidataGroups.PIO.value: build_agegroup_definition(
        type_key=MidataGroups.PIO.value,
        display_name="Pio",
        address_role=PioRoles.ADRESSVERWALTUNG.value,
        co_lead_role=PioRoles.MITLEITUNG.value,
    ),
    MidataGroups.PTA.value: build_agegroup_definition(
        type_key=MidataGroups.PTA.value,
        display_name="PTA",
        address_role=PtaRoles.ADRESSVERWALTUNG.value,
        co_lead_role=PtaRoles.MITLEITUNG.value,
    ),
    MidataGroups.ABTEILUNGS_ROVER.value: build_agegroup_definition(
        type_key=MidataGroups.ABTEILUNGS_ROVER.value,
        display_name="Rover",
        address_role=RoverRoles.ADRESSVERWALTUNG.value,
        co_lead_role=RoverRoles.MITLEITUNG.value,
    ),
    
    MidataGroups.REGION.value: GroupTypeDefinition(
        type_key=MidataGroups.REGION.value,
        display_name="Region",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.REGION.value, frozenset()),
        default_roles=frozenset(),
        children=(
            ChildCategoryDefinition(
                key="committees",
                label="Gremien",
                allowed_types=frozenset({
                    MidataGroups.REGIONALES_GREMIUM.value,
                    MidataGroups.INTERNES_REGIONALES_GREMIUM.value,
                }),
                create_folder_in_keycloak=True,
                stack_same_category=True,
            ),
            ChildCategoryDefinition(
                key="comissions",
                label="Kommissionen",
                allowed_types=frozenset({
                    MidataGroups.REGIONALE_KOMMISSION.value,
                }),
                create_folder_in_keycloak=True,
                stack_same_category=True,
            ),
            ChildCategoryDefinition(
                key="scout_groups",
                label="Abteilungen",
                allowed_types=frozenset({
                    MidataGroups.ABTEILUNG.value,
                }),
                create_folder_in_keycloak=True,
            ),
            ChildCategoryDefinition(
                key="agegroups",
                label="Stufen",
                allowed_types=frozenset({
                    MidataGroups.REGIONALE_ROVER.value,
                }),
                create_folder_in_keycloak=True,
            ),
        ),
    ),
    MidataGroups.REGIONALE_ROVER.value: GroupTypeDefinition(
        type_key=MidataGroups.REGIONALE_ROVER.value,
        display_name="Regionale Rover",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.REGIONALE_ROVER.value, frozenset()),
        default_roles=frozenset({
            RegionaleRoverRoles.ADRESSVERWALTUNG.value,
            RegionaleRoverRoles.MITLEITUNG.value,
        }),
        children=(
            ChildCategoryDefinition(
                key="committees",
                label="Gremien",
                allowed_types=frozenset({
                    MidataGroups.REGIONALES_GREMIUM.value,
                    MidataGroups.INTERNES_REGIONALES_GREMIUM.value,
                })
            ),
        ),
    ),
    
    MidataGroups.ROOT.value: GroupTypeDefinition(
        type_key=MidataGroups.ROOT.value,
        display_name="Root",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.ROOT.value, frozenset()),
        default_roles=frozenset({
            RootRoles.ADMIN.value,
        }),
        children=(
            ChildCategoryDefinition(
                key="bund",
                label="Bund",
                allowed_types=frozenset({
                    MidataGroups.BUND.value,
                }),
                create_folder_in_keycloak=True,
            ),
            
            ChildCategoryDefinition(
                key="silverscouts",
                label="Silverscouts",
                allowed_types=frozenset({
                    MidataGroups.SILVERSCOUTS.value,
                }),
                create_folder_in_keycloak=True,
            ),
        ),
    ),
    
    MidataGroups.AUSBILDUNGSKOMMISSION.value: GroupTypeDefinition(
        type_key=MidataGroups.AUSBILDUNGSKOMMISSION.value,
        display_name="Ausbildungskommission",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.AUSBILDUNGSKOMMISSION.value, frozenset()),
        default_roles=frozenset(),
        children=(
            ChildCategoryDefinition(
                key="commissions",
                label="Kommissionen",
                allowed_types=frozenset({
                    MidataGroups.AUSBILDUNGSKOMMISSION.value,
                }),
                create_folder_in_keycloak=False,
                stack_same_category=True,
            ),
        ),
    ),
    MidataGroups.BUNDES_KOMMISSION.value: GroupTypeDefinition(
        type_key=MidataGroups.BUNDES_KOMMISSION.value,
        display_name="Bundeskommission",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.BUNDES_KOMMISSION.value, frozenset()),
        default_roles=frozenset(),
        children=(
            ChildCategoryDefinition(
                key="commissions",
                label="Kommissionen",
                allowed_types=frozenset({
                    MidataGroups.BUNDES_KOMMISSION.value,
                }),
                create_folder_in_keycloak=False,
                stack_same_category=True,
            ),
        ),
    ), 
    MidataGroups.KANTONALE_KOMMISSION.value: GroupTypeDefinition(
        type_key=MidataGroups.KANTONALE_KOMMISSION.value,
        display_name="Kantonale Kommission",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.KANTONALE_KOMMISSION.value, frozenset()),
        default_roles=frozenset(),
        children=(
            ChildCategoryDefinition(
                key="commissions",
                label="Kommissionen",
                allowed_types=frozenset({
                    MidataGroups.KANTONALE_KOMMISSION.value,
                }),
                create_folder_in_keycloak=False,
                stack_same_category=True,
            ),
        ),
    ),
    MidataGroups.REGIONALE_KOMMISSION.value: GroupTypeDefinition(
        type_key=MidataGroups.REGIONALE_KOMMISSION.value,
        display_name="Regionale Kommission",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.REGIONALE_KOMMISSION.value, frozenset()),
        default_roles=frozenset(),
        children=(
            ChildCategoryDefinition(
                key="commissions",
                label="Kommissionen",
                allowed_types=frozenset({
                    MidataGroups.REGIONALE_KOMMISSION.value,
                }),
                create_folder_in_keycloak=False,
                stack_same_category=True,
            ),
        ),
    ),
    
    MidataGroups.BUNDES_GREMIUM.value: build_committee_definition(
        type_key=MidataGroups.BUNDES_GREMIUM.value,
        display_name="Bundesgremium",
        allowed_types=frozenset({
            MidataGroups.BUNDES_GREMIUM.value,
        }),
    ),
    MidataGroups.KANTONALES_GREMIUM.value: build_committee_definition(
        type_key=MidataGroups.KANTONALES_GREMIUM.value,
        display_name="Kantonales Gremium",
        allowed_types=frozenset({
            MidataGroups.KANTONALES_GREMIUM.value,
            MidataGroups.INTERNES_KANTONALES_GREMIUM.value,
        }),
    ),
    MidataGroups.INTERNES_KANTONALES_GREMIUM.value: build_committee_definition(
        type_key=MidataGroups.INTERNES_KANTONALES_GREMIUM.value,
        display_name="Internes Kantonales Gremium",
        allowed_types=frozenset({
            MidataGroups.INTERNES_KANTONALES_GREMIUM.value,
        }),
    ),
    MidataGroups.REGIONALES_GREMIUM.value: build_committee_definition(
        type_key=MidataGroups.REGIONALES_GREMIUM.value,
        display_name="Regionales Gremium",
        allowed_types=frozenset({
            MidataGroups.REGIONALES_GREMIUM.value,
            MidataGroups.INTERNES_REGIONALES_GREMIUM.value,
        }),
    ),
    MidataGroups.INTERNES_REGIONALES_GREMIUM.value: build_committee_definition(
        type_key=MidataGroups.INTERNES_REGIONALES_GREMIUM.value,
        display_name="Internes Regionales Gremium",
        allowed_types=frozenset({
            MidataGroups.INTERNES_REGIONALES_GREMIUM.value,
        }),
    ),
    MidataGroups.ABTEILUNGS_GREMIUM.value: build_committee_definition(
        type_key=MidataGroups.ABTEILUNGS_GREMIUM.value,
        display_name="Abteilungsgremium",
        allowed_types=frozenset({
            MidataGroups.ABTEILUNGS_GREMIUM.value,
            MidataGroups.INTERNES_ABTEILUNGS_GREMIUM.value,
        }),
    ),
    MidataGroups.INTERNES_ABTEILUNGS_GREMIUM.value: build_committee_definition(
        type_key=MidataGroups.INTERNES_ABTEILUNGS_GREMIUM.value,
        display_name="Internes Abteilungsgremium",
        allowed_types=frozenset({
            MidataGroups.INTERNES_ABTEILUNGS_GREMIUM.value,
        }),
    ),
    
    MidataGroups.SILVERSCOUTS.value: GroupTypeDefinition(
        type_key=MidataGroups.SILVERSCOUTS.value,
        display_name="Silverscouts",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.SILVERSCOUTS.value, frozenset()),
        default_roles=frozenset(),
        children=(
            ChildCategoryDefinition(
                key="regions",
                label="Regionen",
                allowed_types=frozenset({
                    MidataGroups.SILVERSCOUTS_REGION.value,
                }),
            ),
        ),
    ),
    MidataGroups.SILVERSCOUTS_REGION.value: GroupTypeDefinition(
        type_key=MidataGroups.SILVERSCOUTS_REGION.value,
        display_name="Silverscouts Region",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.SILVERSCOUTS_REGION.value, frozenset()),
        default_roles=frozenset(),
        children=(),
    ),
}