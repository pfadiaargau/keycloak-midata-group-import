
from enum import Enum

from model.groups.MidataGroups import MidataGroups


class AbteilungRoles(Enum):
    GROUP_TYPE = MidataGroups.ABTEILUNG.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    ABTEILUNGSLEITUNG = GROUP_PREFIX + "Abteilungsleitung"
    ABTEILUNGSLEITUNG_STV = GROUP_PREFIX + "AbteilungsleitungStv"
    ADRESSVERWALTUNG = GROUP_PREFIX + "Adressverwaltung"
    POWER_USER = GROUP_PREFIX + "PowerUser"
    BEISITZ = GROUP_PREFIX + "Beisitz"
    COACH = GROUP_PREFIX + "Coach"
    EHRENMITGLIED = GROUP_PREFIX + "Ehrenmitglied"
    HEIMVERWALTUNG = GROUP_PREFIX + "Heimverwaltung"
    KASSIER = GROUP_PREFIX + "Kassier"
    RECHNUNGEN = GROUP_PREFIX + "Rechnungen"
    MATERIALWART = GROUP_PREFIX + "Materialwart"
    PASSIVMITGLIED = GROUP_PREFIX + "Passivmitglied"
    SELBSTREGISTRIERT = GROUP_PREFIX + "Selbstregistriert"
    PRAESES = GROUP_PREFIX + "Praeses"
    PRAESIDIUM = GROUP_PREFIX + "Praesidium"
    PRAESIDIUM_APV = GROUP_PREFIX + "PraesidiumApv"
    PRASEIDIUM_ELTERNRAT = GROUP_PREFIX + "PraesidiumElternrat"
    REDAKTOR = GROUP_PREFIX + "Redaktor"
    REVISOR = GROUP_PREFIX + "Revisor"
    SEKRETARIAT = GROUP_PREFIX + "Sekretariat"
    SPEZIALFUNKTION = GROUP_PREFIX + "Spezialfunktion"
    STUFENLEITUNG_BIBER = GROUP_PREFIX + "StufenleitungBiber"
    STUFENLEITUNG_WOELFE = GROUP_PREFIX + "StufenleitungWoelfe"
    STUFENLEITUNG_PFADI = GROUP_PREFIX + "StufenleitungPfadi"
    STUFENLEITUNG_PIO = GROUP_PREFIX + "StufenleitungPio"
    STUFENLEITUNG_ROVER = GROUP_PREFIX + "StufenleitungRover"
    STUFENLEITUNG_PTA = GROUP_PREFIX + "StufenleitungPta"
    VERANTWORTUNG_MATERIALVERKAUFSSTELLE = GROUP_PREFIX + "VerantwortungMaterialverkaufsstelle"
    VERANTWORTUNG_PFADI_TROTZ_ALLEM = GROUP_PREFIX + "VerantwortungPfadiTrotzAllem"
    VERANTWORTUNG_PR = GROUP_PREFIX + "VerantwortungPr"
    VERANTWORTUNG_IT = GROUP_PREFIX + "VerantwortungIT"
    VIZE_PRASIDIUM = GROUP_PREFIX + "VizePraesidium"
    WEBMASTER = GROUP_PREFIX + "Webmaster"
    
        
            
    