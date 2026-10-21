from model.groups.MidataGroups import MidataGroups
from model.roles.abteilung import AbteilungRoles
from model.roles.agegroups import (BiberRoles, PfadiRoles, PioRoles, PtaRoles,
                                   RoverRoles, WoelfeRoles)
from model.roles.bund import (BundesGremiumRoles, BundesKommissionRoles,
                              BundRoles)
from model.roles.kanton import (InternesKantonalesGremiumRoles,
                                KantonaleKommissionRoles,
                                KantonalesGremiumRoles, KantonalverbandRoles)
from model.roles.other import EhemaligeRoles, ElternratRoles, RootRoles
from model.roles.region import (InternesRegionalesGremiumRoles,
                                RegionaleKommissionRoles, RegionaleRoverRoles,
                                RegionalesGremiumRoles)
from model.roles.registry import GROUP_TYPE_ROLES, ROLE_TO_GROUP_TYPE
from model.types.GroupTypeDefinition import (ChildCategoryDefinition,
                                             CollectionDefinition,
                                             GroupTypeDefinition)

# Participant roles (children and youth in the age groups)
TN_ROLES = frozenset({
    BiberRoles.BIBER.value,
    WoelfeRoles.WOLF.value,
    WoelfeRoles.LEITWOLF.value,
    PfadiRoles.PFADI.value,
    PfadiRoles.LEITPFADI.value,
    PioRoles.PIO.value,
    RoverRoles.ROVER.value,
    RegionaleRoverRoles.ROVER.value,
    PtaRoles.MITGLIED.value,
})

# Parent roles
PARENT_ROLES = frozenset({
    ElternratRoles.PRAESIDIUM.value,
    ElternratRoles.MITGLIED.value,
    AbteilungRoles.PRASEIDIUM_ELTERNRAT.value,
})

# Roles without an active function
INACTIVE_ROLES = frozenset(
    role for role in ROLE_TO_GROUP_TYPE
    if role.split("::")[-1] in {"Selbstregistriert", "Passivmitglied", "Ehrenmitglied"}
) | frozenset({
    EhemaligeRoles.MITGLIED.value,
})

# Collection of all roles except participants, parents and inactive roles. The role list contains all known roles,
# but only roles in the collection's group and below are counted.
LEADERS_COLLECTION = CollectionDefinition(
    key="leaders",
    label="Leitende",
    roles=frozenset(ROLE_TO_GROUP_TYPE) - TN_ROLES - PARENT_ROLES - INACTIVE_ROLES,
)

# Leaders at Kanton level: explicit list, so that new roles are not added automatically.
# Leaders of age groups and Abteilungen. Coaches are not included.
KANTONAL_LEADERS_COLLECTION = CollectionDefinition(
    key=LEADERS_COLLECTION.key,
    label=LEADERS_COLLECTION.label,
    roles=frozenset(
        role.value
        for age_group_roles in (BiberRoles, WoelfeRoles, PfadiRoles, PioRoles, RoverRoles, PtaRoles,
                                RegionaleRoverRoles)
        for role in (age_group_roles.EINHEITSLEITUNG, age_group_roles.MITLEITUNG)
    ) | frozenset({
        AbteilungRoles.ABTEILUNGSLEITUNG.value,
        AbteilungRoles.ABTEILUNGSLEITUNG_STV.value,
        AbteilungRoles.STUFENLEITUNG_BIBER.value,
        AbteilungRoles.STUFENLEITUNG_WOELFE.value,
        AbteilungRoles.STUFENLEITUNG_PFADI.value,
        AbteilungRoles.STUFENLEITUNG_PIO.value,
        AbteilungRoles.STUFENLEITUNG_ROVER.value,
        AbteilungRoles.STUFENLEITUNG_PTA.value,
    }),
)

ABTEILUNGSLEITENDE_COLLECTION = CollectionDefinition(
    key="abteilungsleitende",
    label="Abteilungsleitende",
    roles=frozenset({
        AbteilungRoles.ABTEILUNGSLEITUNG.value,
        AbteilungRoles.ABTEILUNGSLEITUNG_STV.value,
    }),
)

STUFENLEITENDE_COLLECTION = CollectionDefinition(
    key="stufenleitende",
    label="Stufenleitende",
    roles=frozenset({
        AbteilungRoles.STUFENLEITUNG_BIBER.value,
        AbteilungRoles.STUFENLEITUNG_WOELFE.value,
        AbteilungRoles.STUFENLEITUNG_PFADI.value,
        AbteilungRoles.STUFENLEITUNG_PIO.value,
        AbteilungRoles.STUFENLEITUNG_ROVER.value,
        AbteilungRoles.STUFENLEITUNG_PTA.value,
    }) | frozenset(
        role.value
        for age_group_roles in (BiberRoles, WoelfeRoles, PfadiRoles, PioRoles, RoverRoles, PtaRoles)
        for role in (age_group_roles.EINHEITSLEITUNG, age_group_roles.ADRESSVERWALTUNG)
    ),
)


def build_agegroup_leaders_collection(key: str, label: str, age_group_roles, stufenleitung: str) -> CollectionDefinition:
    return CollectionDefinition(
        key=key,
        label=label,
        roles=frozenset({
            age_group_roles.EINHEITSLEITUNG.value,
            age_group_roles.MITLEITUNG.value,
            age_group_roles.ADRESSVERWALTUNG.value,
            stufenleitung,
        }),
    )


AGEGROUP_LEADERS_COLLECTIONS = (
    build_agegroup_leaders_collection("leaders_biber", "Biberstufe Leitende",
                                      BiberRoles, AbteilungRoles.STUFENLEITUNG_BIBER.value),
    build_agegroup_leaders_collection("leaders_woelfe", "Wolfsstufe Leitende",
                                      WoelfeRoles, AbteilungRoles.STUFENLEITUNG_WOELFE.value),
    build_agegroup_leaders_collection("leaders_pfadi", "Pfadistufe Leitende",
                                      PfadiRoles, AbteilungRoles.STUFENLEITUNG_PFADI.value),
    build_agegroup_leaders_collection("leaders_pio", "Piostufe Leitende",
                                      PioRoles, AbteilungRoles.STUFENLEITUNG_PIO.value),
)


def build_agegroup_definition(
    type_key: str,
    display_name: str,
    default_roles: frozenset[str],
) -> GroupTypeDefinition:
    return GroupTypeDefinition(
        type_key=type_key,
        display_name=display_name,
        allowed_roles=GROUP_TYPE_ROLES.get(type_key, frozenset()),
        default_roles=default_roles,
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
            KantonalverbandRoles.POWER_USER.value,
            KantonalverbandRoles.COACH.value,
            KantonalverbandRoles.KANTONSLEITUNG.value,
            KantonalverbandRoles.KASSIER.value,
            KantonalverbandRoles.MEDIENSPRECHER.value,
            KantonalverbandRoles.PRAESIDIUM.value,
            KantonalverbandRoles.SEKRETARIAT.value,
            KantonalverbandRoles.VERANTWORTUNG_AUSBILDUNG.value,
            KantonalverbandRoles.VERANTWORTUNG_BETREUUNG.value,
            KantonalverbandRoles.VERANTWORTUNG_BIBERSTUFE.value,
            KantonalverbandRoles.VERANTWORTUNG_WOLFSTUFE.value,
            KantonalverbandRoles.VERANTWORTUNG_PFADISTUFE.value,
            KantonalverbandRoles.VERANTWORTUNG_PIOSTUFE.value,
            KantonalverbandRoles.VERANTWORTUNG_ROVERSTUFE.value,
            KantonalverbandRoles.VERANTWORTUNG_PROGRAMM.value,
            KantonalverbandRoles.VERANTWORTUNG_IT.value,
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
        collections=(
            KANTONAL_LEADERS_COLLECTION,
            ABTEILUNGSLEITENDE_COLLECTION,
            STUFENLEITENDE_COLLECTION,
            *AGEGROUP_LEADERS_COLLECTIONS,
        ),
    ),
    
    MidataGroups.ABTEILUNG.value: GroupTypeDefinition(
        type_key=MidataGroups.ABTEILUNG.value,
        display_name="Abteilung",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.ABTEILUNG.value, frozenset()),
        default_roles=frozenset({
            AbteilungRoles.ABTEILUNGSLEITUNG.value,
            AbteilungRoles.ABTEILUNGSLEITUNG_STV.value,
            AbteilungRoles.ADRESSVERWALTUNG.value,
            AbteilungRoles.COACH.value,
            AbteilungRoles.KASSIER.value,
            AbteilungRoles.MATERIALWART.value,
            AbteilungRoles.PRAESES.value,
            AbteilungRoles.SEKRETARIAT.value,
            AbteilungRoles.STUFENLEITUNG_BIBER.value,
            AbteilungRoles.STUFENLEITUNG_WOELFE.value,
            AbteilungRoles.STUFENLEITUNG_PFADI.value,
            AbteilungRoles.STUFENLEITUNG_PIO.value,
            AbteilungRoles.STUFENLEITUNG_ROVER.value,
            AbteilungRoles.STUFENLEITUNG_PTA.value,
            AbteilungRoles.VERANTWORTUNG_IT.value,
            AbteilungRoles.WEBMASTER.value,
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
                    key="elternrat",
                    label="Elternrat",
                    allowed_types=frozenset({
                        MidataGroups.ELTERNRAT.value,
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
        # AGEGROUP_LEADERS_COLLECTIONS result in <Abteilung>_<Stufe>_Leitende. Disable "Emit Stufe leaders"
        # in the group name mapper, otherwise the name comes from two sources.
        collections=(
            LEADERS_COLLECTION,
            STUFENLEITENDE_COLLECTION,
            *AGEGROUP_LEADERS_COLLECTIONS,
        ),
    ),
    
    MidataGroups.BIBER.value: build_agegroup_definition(
        type_key=MidataGroups.BIBER.value,
        display_name="Biber",
        default_roles=frozenset({
            BiberRoles.ADRESSVERWALTUNG.value,
            BiberRoles.EINHEITSLEITUNG.value,
            BiberRoles.MITLEITUNG.value,
            BiberRoles.BIBER.value,
        }),
    ),
    MidataGroups.WOELFE.value: build_agegroup_definition(
        type_key=MidataGroups.WOELFE.value,
        display_name="Wölfe",
        default_roles=frozenset({
            WoelfeRoles.ADRESSVERWALTUNG.value,
            WoelfeRoles.EINHEITSLEITUNG.value,
            WoelfeRoles.MITLEITUNG.value,
            WoelfeRoles.LEITWOLF.value,
            WoelfeRoles.WOLF.value,
        }),
    ),
    MidataGroups.PFADI.value: build_agegroup_definition(
        type_key=MidataGroups.PFADI.value,
        display_name="Pfadi",
        default_roles=frozenset({
            PfadiRoles.ADRESSVERWALTUNG.value,
            PfadiRoles.EINHEITSLEITUNG.value,
            PfadiRoles.MITLEITUNG.value,
            PfadiRoles.LEITPFADI.value,
            PfadiRoles.PFADI.value,
        }),
    ),
    MidataGroups.PIO.value: build_agegroup_definition(
        type_key=MidataGroups.PIO.value,
        display_name="Pio",
        default_roles=frozenset({
            PioRoles.ADRESSVERWALTUNG.value,
            PioRoles.EINHEITSLEITUNG.value,
            PioRoles.MITLEITUNG.value,
            PioRoles.PIO.value,
        }),
    ),
    MidataGroups.PTA.value: build_agegroup_definition(
        type_key=MidataGroups.PTA.value,
        display_name="PTA",
        default_roles=frozenset({
            PtaRoles.ADRESSVERWALTUNG.value,
            PtaRoles.EINHEITSLEITUNG.value,
            PtaRoles.MITLEITUNG.value,
            PtaRoles.MITGLIED.value,
        }),
    ),
    MidataGroups.ABTEILUNGS_ROVER.value: build_agegroup_definition(
        type_key=MidataGroups.ABTEILUNGS_ROVER.value,
        display_name="Rover",
        default_roles=frozenset({
            RoverRoles.ADRESSVERWALTUNG.value,
            RoverRoles.EINHEITSLEITUNG.value,
            RoverRoles.MITLEITUNG.value,
            RoverRoles.ROVER.value,
        }),
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
            RegionaleRoverRoles.EINHEITSLEITUNG.value,
            RegionaleRoverRoles.MITLEITUNG.value,
            RegionaleRoverRoles.ROVER.value,
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
    MidataGroups.ELTERNRAT.value: GroupTypeDefinition(
        type_key=MidataGroups.ELTERNRAT.value,
        display_name="Elternrat",
        allowed_roles=GROUP_TYPE_ROLES.get(MidataGroups.ELTERNRAT.value, frozenset()),
        default_roles=frozenset({
            ElternratRoles.PRAESIDIUM.value,
            ElternratRoles.MITGLIED.value,
        }),
        children=(),
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