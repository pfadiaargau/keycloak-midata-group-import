from enum import Enum

from model.groups.MidataGroups import MidataGroups


class KantonalverbandRoles(Enum):
    GROUP_TYPE = MidataGroups.KANTONALVERBAND.value
    GROUP_PREFIX = GROUP_TYPE + "::"
    
    ADRESSVERWALTUNG = GROUP_PREFIX + "Adressverwaltung"
    POWER_USER = GROUP_PREFIX + "PowerUser"
    BEISITZ = GROUP_PREFIX + "Beisitz"
    COACH = GROUP_PREFIX + "Coach"
    EHRENMITGLIED = GROUP_PREFIX + "Ehrenmitglied"
    KANTONSLEITUNG = GROUP_PREFIX + "Kantonsleitung"
    KASSIER = GROUP_PREFIX + "Kassier"
    RECHNUNGEN = GROUP_PREFIX + "Rechnungen"
    LEITUNGSKURSBETREUUNG = GROUP_PREFIX + "Leitungskursbetreuung"
    MEDIENSPRECHER = GROUP_PREFIX + "Mediensprecher"
    MITARBEITER = GROUP_PREFIX + "Mitarbeiter"
    MITGLIED_KRISENTEAM = GROUP_PREFIX + "MitgliedKrisenteam"
    KRISENVERANTWORTLICHER = GROUP_PREFIX + "Krisenverantwortlicher"
    PASSIVMITGLIED = GROUP_PREFIX + "Passivmitglied"
    SELBSTREGISTRIERT = GROUP_PREFIX + "Selbstregistriert"
    PRAESIDIUM = GROUP_PREFIX + "Praesidium"
    PRASIDIUM_APV = GROUP_PREFIX + "PraesidiumApv"
    REDAKTOR = GROUP_PREFIX + "Redaktor"
    REVISOR = GROUP_PREFIX + "Revisor"
    SEKRETARIAT = GROUP_PREFIX + "Sekretariat"
    SPEZIALFUNKTION = GROUP_PREFIX + "Spezialfunktion"
    UEBERSETZER = GROUP_PREFIX + "Uebersetzer"
    VERANTWORTUNG_ABTEILUNGEN = GROUP_PREFIX + "VerantwortungAbteilungen"
    VERANTWORTUNG_ANIMATION_SPIRITUELLE = GROUP_PREFIX + "VerantwortungAnimationSpirituelle"
    VERANTWORTUNG_AUSBILDUNG = GROUP_PREFIX + "VerantwortungAusbildung"
    VERANTWORTUNG_BETREUUNG = GROUP_PREFIX + "VerantwortungBetreuung"
    VERANTWORTUNG_BIBERSTUFE = GROUP_PREFIX + "VerantwortungBiberstufe"
    VERANTWORTUNG_INTEGRATION = GROUP_PREFIX + "VerantwortungIntegration"
    VERANTWORTUNG_INTERNATIONALES = GROUP_PREFIX + "VerantwortungInternationales"
    VERANTWORTUNG_SUCHTPRAEVENTIONSPROGRAMM = GROUP_PREFIX + "VerantwortungSuchtpraeventionsprogramm"
    VERANTWORTUNG_KANTONSARCHIV = GROUP_PREFIX + "VerantwortungKantonsarchiv"
    VERANTWORTUNG_KRISENTEAM = GROUP_PREFIX + "VerantwortungKrisenteam"
    VERANTWORTUNG_EHRENAMT = GROUP_PREFIX + "VerantwortungEhrenamt"
    VERANTWORTUNG_LAGERMELDUNG = GROUP_PREFIX + "VerantwortungLagermeldung"
    VERANTWORTUNG_LAGERPLAETZE = GROUP_PREFIX + "VerantwortungLagerplaetze"
    VERANTWORTUNG_MATERIALVERKAUFSSTELLE = GROUP_PREFIX + "VerantwortungMaterialverkaufsstelle"
    VERANTWORTUNG_PFADI_TROTZ_ALLEM = GROUP_PREFIX + "VerantwortungPfadiTrotzAllem"
    VERANTWORTUNG_PFADISTUFE = GROUP_PREFIX + "VerantwortungPfadistufe"
    VERANTWORTUNG_PIOSTUFE = GROUP_PREFIX + "VerantwortungPiostufe"
    VERANTWORTUNG_PR = GROUP_PREFIX + "VerantwortungPr"
    VERANTWORTUNG_PRAEVENTION_SEXUELLER_AUSBEUTUNG = GROUP_PREFIX + "VerantwortungPraeventionSexuellerAusbeutung"
    VERANTWORTUNG_IT = GROUP_PREFIX + "VerantwortungIT"
    VERANTWORTUNG_PROGRAMM = GROUP_PREFIX + "VerantwortungProgramm"
    VERANTWORTUNG_ROVERSTUFE = GROUP_PREFIX + "VerantwortungRoverstufe"
    VERANTWORTUNG_WOLFSTUFE = GROUP_PREFIX + "VerantwortungWolfstufe"
    VIZE_PRASIDIUM = GROUP_PREFIX + "VizePraesidium"
    WEBMASTER = GROUP_PREFIX + "Webmaster"
    VERANTWORTUNG_NACHHALTIGKEIT = GROUP_PREFIX + "VerantwortungNachhaltigkeit"
    
    
    
    
            
                    
        