from enum import Enum


class GroupType(Enum):
    KANTONALVERBAND = "Group::Kantonalverband"
    KANTONALES_GREMIUM = "Group::KantonalesGremium"
    INTERNES_KANTONALES_GREMIUM = "Group::InternesKantonalesGremium"
    
    REGION = "Group::Region"
    REGIONALES_GREMIUM = "Group::RegionalesGremium"
    INTERNES_REGIONALES_GREMIUM = "Group::InternesRegionalesGremium"
    REGIONALE_ROVER = "Group::RegionaleRover"
    
    ABTEILUNG = "Group::Abteilung"
    ABTEILUNGS_GREMIUM = "Group::AbteilungsGremium"
    INTERNES_ABTEILUNGS_GREMIUM = "Group::InternesAbteilungsGremium"
    
    # Agegroups
    BIBER = "Group::Biber"
    WOELFE = "Group::Woelfe"
    PFADI = "Group::Pfadi"
    PIO = "Group::Pio"
    ABTEILUNGS_ROVER = "Group::AbteilungsRover"    