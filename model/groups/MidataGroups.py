from enum import Enum


class MidataGroups(Enum):
    ROOT = "Group::Root"
    
    BUND = "Group::Bund"
    BUNDES_GREMIUM = "Group::BundesGremium"
    BUNDES_KOMMISSION = "Group::BundesKommission"
    AUSBILDUNGSKOMMISSION = "Group::Ausbildungskommission"
    
    KANTONALVERBAND = "Group::Kantonalverband"
    KANTONALES_GREMIUM = "Group::KantonalesGremium"
    INTERNES_KANTONALES_GREMIUM = "Group::InternesKantonalesGremium"
    KANTONALE_KOMMISSION = "Group::KantonaleKommission"
    KANTONALE_GREMIEN = (KANTONALES_GREMIUM, INTERNES_KANTONALES_GREMIUM)
    
    REGION = "Group::Region"
    REGIONALES_GREMIUM = "Group::RegionalesGremium"
    INTERNES_REGIONALES_GREMIUM = "Group::InternesRegionalesGremium"
    REGIONALE_KOMMISSION = "Group::RegionaleKommission"
    REGIONALE_ROVER = "Group::RegionaleRover"
    REGIONALE_GREMIEN = (REGIONALES_GREMIUM, INTERNES_REGIONALES_GREMIUM)
    
    ABTEILUNG = "Group::Abteilung"
    ABTEILUNGS_GREMIUM = "Group::AbteilungsGremium"
    INTERNES_ABTEILUNGS_GREMIUM = "Group::InternesAbteilungsGremium"
    ABTEILUNGS_GREMIEN = (ABTEILUNGS_GREMIUM, INTERNES_ABTEILUNGS_GREMIUM)
    
    # Agegroups
    BIBER = "Group::Biber"
    WOELFE = "Group::Woelfe"
    PFADI = "Group::Pfadi"
    PIO = "Group::Pio"
    ABTEILUNGS_ROVER = "Group::AbteilungsRover"
    PTA = "Group::Pta"
    
    # Other
    EHEMALIGE = "Group::Ehemalige"
    ELTERNRAT = "Group::Elternrat"
    ERZIEHUNGSBERECHTIGTEN_GREMIUM = "Group::ErziehungsberechtigtenGremium"