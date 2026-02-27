#!/usr/bin/python3
# coding=utf-8

import json
import logging
import os
import smtplib
import sys
import time
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from random import randint

import passgen
import requests
from ldap3 import (ALL, HASHED_SALTED_SHA, MODIFY_ADD, MODIFY_DELETE,
                   MODIFY_REPLACE, Connection, Server)
from ldap3.utils.hashed import hashed
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# define Mailserver
mailuser = 'noreply@pfadiaargau.ch'
mailpwd = '08vFYy1coOKm5zl1hIMU'
mailserver = 'mail.pfadiaargau.ch'
mailport = 465
errorNotificationEmail = 'webteam@pfadiaargau.ch'

def main():

    # authToken from KV
    authToken = '5LQaz2i2oJzS_dmx8y5SLx-1KjsjJy1gb9a4QqzLTJuCNnnDCg'  # Midata API-Key (Test MiData Abteilungen)

    # KV groups
    sync_groups_KV = [
        {'id': 4691, 'short_name': 'PfadiAargau', 'subgroups': [
            {'id': 5539, 'short_name': 'KaLei'},
            {'id': 5548, 'short_name': 'Vorstand'},
            {'id': 5547, 'short_name': ''},
            {'id': 5952, 'short_name': 'BiPA'},
            {'id': 5540, 'short_name': 'WUDU'},
            {'id': 5543, 'short_name': 'PST'},
            {'id': 5541, 'short_name': 'PStres'},
            {'id': 5542, 'short_name': 'Staar'},
            {'id': 5544, 'short_name': 'AKUT'},
            {'id': 5546, 'short_name': ''},
            {'id': 5780, 'short_name': ''},
            {'id': 5783, 'short_name': ''},
            {'id': 5782, 'short_name': 'Webteam'},
            {'id': 7337, 'short_name': 'Topf'},
            {'id': 6711, 'short_name': ''},
            {'id': 9244, 'short_name': 'Projekt Jubilaeumsjahr 2020'},
#            {'id': 8802, 'short_name': 'Pfaditechnik Teich'},
            {'id': 9908, 'short_name': ''},
            {'id': 8399, 'short_name': ''},
            {'id': 10140, 'short_name': ''}, # Liste Krisencoachs
            {'id': 10292, 'short_name': ''}, # AL-Gremium
            {'id': 10475, 'short_name': 'Aktivitaetenvorschlaege_PT'}, # Aktivitätenvorschläge PT
            {'id': 10624, 'short_name': 'Projekt_Wasserzunft'}, # Projekt Wasserzunft 
            {'id': 11962, 'short_name': 'Projekt_Rover_Grossanlass'}, # Projekt Rover Grossanlass (STAAR)
            {'id': 12396, 'short_name': 'Umweltteam'}, # Umwelt
            ]
        }
    ]

    # Abteilungen groups
    #   'extraGroups' : ['Elternrat', 'BiberstufeTN', 'WolfsstufeTN', 'PfadistufeTN', 'PiostufeTN', 'RoverstufeTN', 'PTA_TN']
    #       if using extraGroups and anything else than 'Elternat', an abteilungs-specific authToken is needed!
    #   'authToken': 'XYZ1234'
    #   'skeleton': True
    #       create only groups, with no users at all
    sync_groups_ABT = [
        {'id': 5416, 'short_name': 'SGA', 'extraGroups' : ['Bott 26 OK']},
        #{'id': 4760, 'short_name': 'Nussbaumen', 'extraGroups' : ['Elternrat', 'PiostufeTN'], 'authToken': 'zYifgX3kCBFzLT4r6ecVHAsKmbker6sNts7Pzxx544MWU82yFw'},
        {'id': 4760, 'short_name': 'Nussbaumen', 'extraGroups' : ['Elternrat']},
        {'id': 5418, 'short_name': 'Thierstein'},
        {'id': 5402, 'short_name': 'Adler'},
        {'id': 5412, 'short_name': 'AlphaCentauri', 'extraGroups' : ['Elternrat']},
        {'id': 5403, 'short_name': 'Baregg', 'skeleton': True},
        {'id': 5419, 'short_name': 'Wildegg'},
        {'id': 5404, 'short_name': 'BigHorn'},
        {'id': 5405, 'short_name': 'Blaustein'},
        {'id': 5406, 'short_name': 'Burghorn'},
        {'id': 5408, 'short_name': 'Erdmaenli'},
        {'id': 5413, 'short_name': 'Lenzburg'},
        {'id': 5411, 'short_name': 'Hochwacht', 'skeleton': True},
        {'id': 5425, 'short_name': 'PTA'},
        {'id': 5409, 'short_name': 'Brugg', 'extraGroups' : ['Elternrat']},
        {'id': 5410, 'short_name': 'Hallwyl'},
        {'id': 5407, 'short_name': 'Schoeftle', 'skeleton': True},
        {'id': 5368, 'short_name': 'Sins'},
        {'id': 5415, 'short_name': 'Wohle'},
        {'id': 5420, 'short_name': 'Zofige'},
        {'id': 5414, 'short_name': 'Riko', 'extraGroups' : ['Elternrat']},
        {'id': 4698, 'short_name': 'Heitersberg'},
        {'id': 4697, 'short_name': 'Sodales'},
        {'id': 5424, 'short_name': 'Rymenzburg'},
        {'id': 5421, 'short_name': 'Kulm'},
        {'id': 5422, 'short_name': 'Wyna'},
        {'id': 5417, 'short_name': 'Safenwil'},
        {'id': 11377, 'short_name': 'Pfasyl Aargau'},
    ]
    
    # Event groups (Kurse & Events)
    sync_events = [
        {'group_id': 3, 'event_id': 14405, 'short_name': 'AG051-21'},
        {'group_id': 3, 'event_id': 14056, 'short_name': 'AG111-21'},
        {'group_id': 3, 'event_id': 14060, 'short_name': 'AG121-21'},
        {'group_id': 3, 'event_id': 14061, 'short_name': 'AG122-21'},
        {'group_id': 3, 'event_id': 14276, 'short_name': 'AG551-21'},
        {'group_id': 3, 'event_id': 14058, 'short_name': 'SO222-21'},    
        {'group_id': 3, 'event_id': 14058, 'short_name': 'SO222-21'},     
        {'group_id': 3, 'event_id': 14055, 'short_name': 'SO221-21'},        
        {'group_id': 3, 'event_id': 14063, 'short_name': 'SO212-21'},
        {'group_id': 3, 'event_id': 18065, 'short_name': 'SO112-22'},
        {'group_id': 3, 'event_id': 18222, 'short_name': 'AG551-22'},
        {'group_id': 3, 'event_id': 18057, 'short_name': 'SO122-22'},
        {'group_id': 3, 'event_id': 18061, 'short_name': 'AG261-22'},
        {'group_id': 3, 'event_id': 18059, 'short_name': 'AG221-22'},
        {'group_id': 3, 'event_id': 18054, 'short_name': 'SO121-22'},
        {'group_id': 3, 'event_id': 18060, 'short_name': 'SO111-22'},
        {'group_id': 3, 'event_id': 19880, 'short_name': 'AG056-22'},
        {'group_id': 3, 'event_id': 20434, 'short_name': 'MF_COACH_22'},
        {'group_id': 3, 'event_id': 20798, 'short_name': 'SO221-23'},
        {'group_id': 3, 'event_id': 20797, 'short_name': 'SO211-23'},
        {'group_id': 3, 'event_id': 20811, 'short_name': 'AG121-23'},
        {'group_id': 3, 'event_id': 20812, 'short_name': 'AG122-23'},
        {'group_id': 3, 'event_id': 21372, 'short_name': 'AG554-23'},
        {'group_id': 3, 'event_id': 20800, 'short_name': 'SO251-23'},
        {'group_id': 3, 'event_id': 20799, 'short_name': 'AG111-23'},
        {'group_id': 3, 'event_id': 23227, 'short_name': 'MF_COACH_23'},
        {'group_id': 3, 'event_id': 24114, 'short_name': 'SO111-24'},
        {'group_id': 3, 'event_id': 24161, 'short_name': 'SO051-24'},
        {'group_id': 3, 'event_id': 24117, 'short_name': 'SO122-24'},
        {'group_id': 3, 'event_id': 24121, 'short_name': 'AG222-24'},
        {'group_id': 3, 'event_id': 24115, 'short_name': 'SO112-24'},
        {'group_id': 3, 'event_id': 24120, 'short_name': 'AG221-24'},
        {'group_id': 3, 'event_id': 27832, 'short_name': 'SO252-25'},
        {'group_id': 3, 'event_id': 27830, 'short_name': 'AG121-25'},
        {'group_id': 3, 'event_id': 27837, 'short_name': 'AG111-25'},
        {'group_id': 3, 'event_id': 27831, 'short_name': 'SO221-25'},
        {'group_id': 3, 'event_id': 28224, 'short_name': 'AG122-25'},
        {'group_id': 3, 'event_id': 27838, 'short_name': 'AG112-25'},
        {'group_id': 3, 'event_id': 28421, 'short_name': 'AG556-25'},
        {'group_id': 3, 'event_id': 29699, 'short_name': 'AG051-25'},
        {'group_id': 3, 'event_id': 28464, 'short_name': 'AG021-25'},
        {'group_id': 3, 'event_id': 29069, 'short_name': 'SO555-25'},
        {'group_id': 3, 'event_id': 31598, 'short_name': 'AG221-26'},
        {'group_id': 3, 'event_id': 31599, 'short_name': 'AG251-26'},
        {'group_id': 3, 'event_id': 31600, 'short_name': 'AG211-26'},
        {'group_id': 3, 'event_id': 31603, 'short_name': 'SO122-26'},
        {'group_id': 3, 'event_id': 31596, 'short_name': 'SO052-26'}
    ]
    
    # Start logging
    logName = datetime.now().strftime('syncLDAP_%Y%m%d_%H%M%S.log')
    logFile = '/opt/scripts/logSyncLDAP/' + logName
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(filename=logFile,level=logging.DEBUG) # Set log level (DEBUG, INFO, WARNING, ERROR)    
    logging.getLogger().addHandler(logging.StreamHandler()) # Print simultaneously to the command line tool 
    t1 = datetime.now()
    logging.info('SYNC LDAP started at ' + t1.strftime('%H:%M:%S, %d.%m.%Y'))

    # Delete old log files
    logHistoryDays = 30 # log files older than this will be deleted automatically [days]
    now = time.time()
    for f in os.listdir('/opt/scripts/logSyncLDAP'): # check every file
        if os.stat(os.path.join('/opt/scripts/logSyncLDAP', f)).st_mtime < now - logHistoryDays * 86400: # if too old
            logging.debug('log ' + str(f) + ' is older than ' + str(logHistoryDays) + ' days and will be deleted')
            if os.path.isfile(os.path.join('/opt/scripts/logSyncLDAP', f)): # only delete, if it's a file
                with open(os.path.join('/opt/scripts/logSyncLDAP', f), 'r') as file: # open too old file
                    if 'ERROR' in file.read(): # if the log file contains an error, it might be interesting in the future, so keep it
                        logging.info('log ' + str(f) + ' contains an error and will not be deleted')
                        file.close()
                    else:
                        file.close()
                        os.remove(os.path.join('/opt/scripts/logSyncLDAP', f))
    
    # # define LDAP server
    ldapServer = Server('cloud.pfadiaargau.ch', get_info=ALL)
    ldapUser = 'cn=admin,dc=pfadiaargau,dc=ch'
    ldapPassword = 'alcDQ3dKZrsBqD0NfBXJ'
    groupDomainEvent = 'ou=Events,ou=Gruppen,dc=pfadiaargau,dc=ch'
    groupDomainKV = 'ou=Gruppen,dc=pfadiaargau,dc=ch'
    groupDomainAbt = 'ou=Gruppen,dc=pfadiaargau,dc=ch'
    userDomain = 'ou=Benutzer,dc=pfadiaargau,dc=ch'
    
    # define TEST LDAP server
    # ldapServer = Server('localhost', get_info=ALL)
    # ldapUser = 'cn=Manager,dc=maxcrc,dc=com'
    # ldapPassword = 'secret'
    # groupDomainEvent = 'ou=Events,ou=Gruppen,dc=maxcrc,dc=com'
    # groupDomainKV = 'ou=Gruppen,dc=maxcrc,dc=com'
    # groupDomainAbt = 'ou=Gruppen,dc=maxcrc,dc=com'
    # userDomain = 'ou=Benutzer,dc=maxcrc,dc=com'
    
    # open connection to LDAP server
    conn = Connection(ldapServer, ldapUser, ldapPassword, auto_bind=True)
    gidNumber = 9001

    people = {}
    
    sync_KV = 1
    if sync_KV:
        logging.info('Start syncing KV')
        queried_teams = []
        for KV in sync_groups_KV: # search through all Kantonalverbände
            logging.info('Querying KV ' + KV['short_name'] + ' (id: ' + str(KV['id']) + ')')
            mainKV = {'id': KV['id'], 'name': KV['short_name'], 'people': []} # group for whole Kantonalverband, every people found will be added to this group
            # Synchronize Kantonsleiter and Präsident
            # Disabled, since it could lead to chaos if someone changes something in Midata accidently!
            # Kantonsleiter = {'id': 100, 'name': 'Kantonsleiter', 'people': []} # group for Kantonsleiter
            # Praesident = {'id': 200, 'name': 'Präsident', 'people': []} # group for Präsident
            # group = query_group_people(KV['id'], authToken) # query for the top group of the Kantonalverband
            # for person in group['people']: # for every found person in the subgroup
                # for role in group['linked']['roles']: # find all roles for this person (roles in this group!)
                    # if role['id'] in person['links']['roles']:
                        # rt = role['role_type']
                        # if rt == 'Kantonsleiter*in':
                            # Kantonsleiter['people'].append(person['nickname'])
                            # mainKV['people'].append(person['id'])
                        # if rt == 'Präsident*in':
                            # Praesident['people'].append(person['nickname'])
                            # mainKV['people'].append(person['id'])
            for team in KV['subgroups']: # search through all subgroups of the Kantonalverband
                logging.info('Querying team ' + team['short_name'] + ' (id: ' + str(team['id']) + ')')
                group_info = query_group_info(team['id'], authToken)
                group = query_group_people(team['id'], authToken)
                queried_team = {}
                queried_team['id'] = group_info['groups'][0]['id']
                if team['short_name'] == '':
                    queried_team['name'] = group_info['groups'][0]['name']
                else:
                    queried_team['name'] = team['short_name']
                logging.debug('Teamname defined as ' + str(queried_team['name']))
                queried_team['people'] = []
                for person in group['people']:
                    add_person_to_people(person, people, 'PfadiAargau')
                    queried_team['people'].append(person['id'])
                    mainKV['people'].append(person['id'])
                queried_teams.append(queried_team)
                ldap_sync_group(conn, queried_team, groupDomainKV)
                logging.info('Filled group ' + str(queried_team['name']) + ' (' + str(len(queried_team['people'])) + '): ' + str(queried_team['people']))
            mainKV['people'] = list(set(mainKV['people'])) # create first a set of the list, removing all the duplicates. Then convert it back to a list
            queried_teams.append(mainKV)
            ldap_sync_group(conn, mainKV, groupDomainKV)
            logging.info('Filled group ' + str(KV['short_name']) + ' (' + str(len(mainKV['people'])) + '): ' + str(mainKV['people']))
    else:
        logging.info('Syncing KV disabled')
         
    sync_ABT = 1
    if sync_ABT:
        logging.info('Start syncing abteilungen')
        hierarchy = query_midata_hierarchy(authToken)
        #logging.debug(hierarchy)
        for abteilung in sync_groups_ABT:
            logging.info('Querying Abteilung ' + abteilung['short_name'] + ' (id: ' + str(abteilung['id']) + ')')
            ldap_sync_ou(conn, abteilung['short_name'], groupDomainAbt) # create ou in ldap if it does not exist yet
            if 'authToken' in abteilung: # use authToken from abteilung if available (to see all users)
                logging.debug('authToken from Abteilung available')
            else:
                logging.debug('No authToken from Abteilung available')
            groups_id = find_all_subgroups(hierarchy, abteilung['id'])

            groups = {}
            groups['Abteilungsleiter'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Abteilungsleiter', 'people':[]}
            groups['Abteilungsstab'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Abteilungsstab', 'people':[]}
            groups['Alle_Leiter'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Alle_Leiter', 'people':[]}
            groups['Coach'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Coach', 'people':[]}
            groups['Kassier'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Kassier', 'people':[]}
            groups['Materialwart'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Materialwart', 'people':[]}
            groups['PR'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_PR', 'people':[]}
            groups['Praeses'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Praeses', 'people':[]}
            groups['Stufenleiter'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Stufenleiter', 'people':[]}
            groups['Biberstufe'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Biberstufe', 'people':[]}
            groups['Wolfsstufe'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Wolfsstufe', 'people':[]}
            groups['Pfadistufe'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Pfadistufe', 'people':[]}
            groups['Piostufe'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Piostufe', 'people':[]}
            groups['Roverstufe'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Roverstufe', 'people':[]}
            if 'extraGroups' in abteilung:
                if 'Elternrat' in abteilung['extraGroups']:
                    groups['Elternrat'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Elternrat', 'people':[]}
                if 'BiberstufeTN' in abteilung['extraGroups']:
                    groups['BiberstufeTN'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_BiberstufeTN', 'people':[]}
                if 'WolfsstufeTN' in abteilung['extraGroups']:
                    groups['WolfsstufeTN'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_WolfsstufeTN', 'people':[]}
                if 'PfadistufeTN' in abteilung['extraGroups']:
                    groups['PfadistufeTN'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_PfadistufeTN', 'people':[]}
                if 'PiostufeTN' in abteilung['extraGroups']:
                    groups['PiostufeTN'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_PiostufeTN', 'people':[]}
                if 'RoverstufeTN' in abteilung['extraGroups']:
                    groups['RoverstufeTN'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_RoverstufeTN', 'people':[]}
                if 'PTA_TN' in abteilung['extraGroups']:
                    groups['PTA_TN'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_PTA_TN', 'people':[]}
            #if abteilung['id'] == 5415: # Wohle   15.11.2024, omni: remove wohle special stuff, joker(wohle) gave ok
            #    groups['Bienli'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Bienli', 'people':[]}
            #    groups['Woelfe'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Woelfe', 'people':[]}
            #    groups['Pfader'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Pfader', 'people':[]}
            #    groups['Pfadisli'] = {'id':str(abteilung['id']), 'name':abteilung['short_name']+'_Pfadisli', 'people':[]}
            logging.info('Groups to be synchronized: ' + str(groups))
            
            for group_id in groups_id: # search through every subgroup
                group_info = query_group_info(group_id, authToken)['groups'][0]
                #logging.info('Group type: ' + group_info['group_type'])
                if group_info['group_type'] == 'Gremium' or group_info['group_type'] == 'Internes Gremium':
                    logging.debug('Gremium and Internes Gremium will not be synchronized: ' + str(group_id) + ', ' + group_info['name'])
                elif group_id in [5659]:
                    #This (disabled) group(s) can somehow not be queried and will be exempted
                    logging.debug('Group will not be synchronized: ' + str(group_id) + ', ' + group_info['name'])
                else: # not Gremium, so continue to search
                    if 'authToken' in abteilung: # use authToken from abteilung if available (to see all users)
                        # logging.info('group_id (token from Abteilung): ' + str(group_id)) # TEMPORARY, 11.11.2021
                        group = query_group_people(group_id, abteilung['authToken'])
                    else:
                        group = query_group_people(group_id, authToken)
                    for person in group['people']: # for every found person in the subgroup
                        # logging.info('person: ' + str(person['id'])) # TEMPORARY, 08.11.2021
                        
                        # if str(person['id']) == '50702':
                        #     logging.info(str(person['links']['roles']))

                        # if str(person['id']) == '132746':
                        #     logging.info(str(person['links']['roles']))

                        #if 'roles' in group['linked']:  # TEMPORARY, 08.11.2021
                        for role in group['linked']['roles']: # find all roles for this person (roles in this group!)
                            # if 'roles' in person['links']:  # TEMPORARY, 08.11.2021
                            if 'roles' in person['links'] and role['id'] in person['links']['roles']:  # 
                                rt = role['role_type']
                                
                                if group_info['group_type'] == 'Abteilung':
                                    if rt in ['Abteilungsleiter*in', 'Abteilungsleiter*in Stv']: # will be added to more groups if not skeleton, see below
                                        groups['Abteilungsleiter']['people'].append(person['id'])
                                        add_person_to_people(person, people, 'Abteilung')
                                    if 'skeleton' not in abteilung: # only create skeleton (no users will be created, only groups) or do full sync
                                        if rt in ['Abteilungsleiter*in', 'Abteilungsleiter*in Stv']:
                                            groups['Abteilungsstab']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Stufenleiter*in Biber', 'Stufenleiter*in Wölfe', 'Stufenleiter*in Pfadi', 'Stufenleiter*in Pio', 'Stufenleiter*in Rover', 'Stufenleiter*in PTA']:
                                            groups['Stufenleiter']['people'].append(person['id'])
                                            groups['Abteilungsstab']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Materialwart*in']:
                                            groups['Materialwart']['people'].append(person['id'])
                                            groups['Abteilungsstab']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id']) 
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Coach']:
                                            groups['Coach']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id']) 
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Präses']:
                                            groups['Praeses']['people'].append(person['id'])
                                            groups['Abteilungsstab']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id']) 
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Kassier*in']:
                                            groups['Kassier']['people'].append(person['id'])
                                            groups['Abteilungsstab']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Verantwortliche*r PR', 'Webmaster', 'Redaktor*in']:
                                            groups['PR']['people'].append(person['id'])
                                            groups['Abteilungsstab']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Sekretariat', 'Adressverwalter*in', 'Präsident*in', 'Vize Präsident*in', 'Verantwortliche*r Pfadi Trotz Allem', 'Spezialfunktion']:
                                            groups['Abteilungsstab']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Revisor*in', 'Verantwortliche*r Materialverkaufsstelle', 'Präsident*in APV', 'Heimverwalter*in']:
                                            groups['Alle_Leiter']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                            
                                if 'skeleton' not in abteilung: # only create skeleton (no users will be created, only groups) or do full sync       
                                    if group_info['group_type'] == 'Biber':
                                        if rt in ['Einheitsleiter*in', 'Mitleiter*in', 'Adressverwalter*in']:
                                            groups['Biberstufe']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Biber'] and 'BiberstufeTN' in groups:
                                            groups['BiberstufeTN']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                            
                                    if group_info['group_type'] == 'Wölfe':
                                        if rt in ['Einheitsleiter*in', 'Mitleiter*in', 'Adressverwalter*in']:
                                            groups['Wolfsstufe']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Wolf'] and 'WolfsstufeTN' in groups:
                                            groups['WolfsstufeTN']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                            
                                    #if group_id in [5460]: # Bienli Pfadi Wohle special case   15.11.2024, omni: remove Wohle special stuff
                                    #    if rt in ['Einheitsleiter*in', 'Mitleiter*in', 'Adressverwalter*in']:
                                    #        groups['Bienli']['people'].append(person['id'])
                                    #        groups['Alle_Leiter']['people'].append(person['id'])
                                    #        add_person_to_people(person, people, 'Abteilung')
                                    #    if rt in ['Wolf'] and 'WolfsstufeTN' in groups:
                                    #        groups['WolfsstufeTN']['people'].append(person['id'])
                                    #        add_person_to_people(person, people, 'Abteilung')
                                            
                                    #if group_id in [5463, 7965, 7971, 7972]: # Wölfe Pfadi Wohle special case   15.11.2024, omni: remove Wohle special stuff
                                    #    if rt in ['Einheitsleiter*in', 'Mitleiter*in', 'Adressverwalter*in']:
                                    #        groups['Woelfe']['people'].append(person['id'])
                                    #        groups['Alle_Leiter']['people'].append(person['id'])
                                    #        add_person_to_people(person, people, 'Abteilung')
                                    #    if rt in ['Wolf'] and 'WolfsstufeTN' in groups:
                                    #        groups['WolfsstufeTN']['people'].append(person['id'])
                                    #        add_person_to_people(person, people, 'Abteilung')
                                            
                                    if group_info['group_type'] == 'Pfadi':
                                        if rt in ['Einheitsleiter*in', 'Mitleiter*in', 'Adressverwalter*in']:
                                            groups['Pfadistufe']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Pfadi'] and 'PfadistufeTN' in groups:
                                            groups['PfadistufeTN']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                            
                                    #if group_id in [5470, 5494, 5495, 5496, 5532]: # Pfader Pfadi Wohle special case   15.11.2024, omni: remove Wohle special stuff
                                    #    if rt in ['Einheitsleiter*in', 'Mitleiter*in', 'Adressverwalter*in']:
                                    #        groups['Pfader']['people'].append(person['id'])
                                    #        groups['Alle_Leiter']['people'].append(person['id'])
                                    #        add_person_to_people(person, people, 'Abteilung')
                                    #    if rt in ['Pfadi'] and 'PfadistufeTN' in groups:
                                    #        groups['PfadistufeTN']['people'].append(person['id'])
                                    #        add_person_to_people(person, people, 'Abteilung')
                                            
                                    #if group_id in [5466, 5497, 5498, 5499, 5533]: # Pfadisli Pfadi Wohle special case   15.11.2024, omni: remove Wohle special stuff
                                    #    if rt in ['Einheitsleiter*in', 'Mitleiter*in', 'Adressverwalter*in']:
                                    #        groups['Pfadisli']['people'].append(person['id'])
                                    #        groups['Alle_Leiter']['people'].append(person['id'])
                                    #        add_person_to_people(person, people, 'Abteilung')
                                    #    if rt in ['Pfadi'] and 'PfadistufeTN' in groups:
                                    #        groups['PfadistufeTN']['people'].append(person['id'])
                                    #        add_person_to_people(person, people, 'Abteilung')
                                            
                                    if group_info['group_type'] == 'Pio':
                                        if rt in ['Einheitsleiter*in', 'Mitleiter*in', 'Adressverwalter*in']:
                                            groups['Piostufe']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Pio'] and 'PiostufeTN' in groups:
                                            groups['PiostufeTN']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                            
                                    if group_info['group_type'] == 'Rover':
                                        if rt in ['Einheitsleiter*in', 'Mitleiter*in', 'Adressverwalter*in']:
                                            groups['Roverstufe']['people'].append(person['id'])
                                            groups['Alle_Leiter']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Rover'] and 'RoverstufeTN' in groups:
                                            groups['RoverstufeTN']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                            
                                    if group_info['group_type'] == 'PTA':
                                        if rt in ['Einheitsleiter*in', 'Mitleiter*in', 'Adressverwalter*in']:
                                            groups['Alle_Leiter']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                        if rt in ['Mitglied'] and 'PTA_TN' in groups:
                                            groups['PTA-TN']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')
                                            
                                    if group_info['group_type'] == 'Elternrat' and 'Elternrat' in groups:
                                        if rt in ['Präsident*in', 'Mitglied']:
                                            groups['Elternrat']['people'].append(person['id'])
                                            add_person_to_people(person, people, 'Abteilung')


            for group in groups: # delete all duplicates within a group
                groups[group]['people'] = list(set(groups[group]['people'])) # create first a set of the list, removing all the duplicates. Then convert it back to a list
                ldap_sync_group(conn, groups[group], 'ou=' + abteilung['short_name'] + ',' + groupDomainAbt)
                logging.info('Filled group ' + str(group) + ' (' + str(len(groups[group])) + '): ' + str(groups[group]))
    else:
        logging.info('Syncing abteilungen disabled')
            
    sync_Events = 1
    if sync_Events:
        logging.info('Start syncing events')
        queried_events = []
        for event in sync_events:
            logging.info('Querying group ' + event['short_name'] + ' (id: ' + str(event['event_id']) + ')')
            group = query_event_people(event['group_id'], event['event_id'], authToken)
            queried_event = {}
            queried_event['id'] = event['event_id']
            queried_event['name'] = event['short_name']
            queried_event['people'] = []
            for person in group:
                for role in person['roles']:
                    if role['name'] != 'Teilnehmer/-in':
                        person['id'] = person['links']['person'] # for an event, the participant receives a new ID. The original ID is in ['links']['person']
                        add_person_to_people(person, people, 'PfadiAargau')
                        queried_event['people'].append(person['id'])
            queried_events.append(queried_event)
            logging.info('Filled group ' + str(queried_event['name']) + ' (' + str(len(queried_event['people'])) + '): ' + str(queried_event['people']))
            ldap_sync_group(conn, queried_event, groupDomainEvent)
    else:
        logging.info('Syncing events disabled')
    
    logging.info('Number of people to synchronize with LDAP: ' + str(len(people)))
    
    sync_people_with_ldap = 1
    if sync_people_with_ldap:
        for id in people:
            person = people[id]
            
            # change mailaddress from person['email'] to 'syncldap+' + str(person['id'] + '@pfadiaargau.ch' -> will be redirected to adreju@pfadiaargau.ch
            #if person['email'] != None:
            #    person['email'] = 'syncldap+' + str(person['id']) + '@pfadiaargau.ch'
            
            ldap_sync_user(conn, person, userDomain)

    # Check if an error occured, if so, send email to address below
    with open(logFile, 'r') as file: # open log file
        if 'ERROR' in file.read(): # if the log file contains an error, send email
            mail_error(logFile, logName, errorNotificationEmail)
            file.close()

    t2 = datetime.now()
    logging.info('{0:0.0f} people synced.'.format(len(people)))
    logging.info('SYNC LDAP finished at ' + t2.strftime('%H:%M:%S, %d.%m.%Y'))
    logging.info('Execution took {0:0.0f} s'.format((t2 - t1).total_seconds()))
    
    
    
def ldap_sync_ou(conn, ou, domain):
    if conn.search(domain, '(ou=' + ou + ')', attributes=['ou']): # if ou does not exist yet
        logging.info('ou already exists in ldap')
    else:
        logging.info('Create ou \'' + ou + '\' in ldap')
        res = conn.add('ou=' + ou + ',' + domain, attributes={'objectClass': ['organizationalUnit'], 'ou': ou})
    return
    
def ldap_sync_group(conn, group, domain):
    # Sync group
    if conn.search(domain, '(cn=' + group['name'] + ')', attributes=['cn']): # if group does not exist yet
        logging.info('Team already exists in ldap')
    else:
        logging.info('Create group group in ldap: ' + group['name'] + ' id: ' + str(group['id']))
        res = conn.add('cn=' + group['name'] + ',' + domain, attributes={'objectClass': ['posixGroup'], 'cn': group['name'], 'gidNumber': str(group['id'])+str(randint(100000, 999999))})
    # Sync memberUids of group
    conn.search(domain, '(cn=' + group['name'] + ')', attributes=['memberUID']) # get all memberUids of the group
    memberUids = []
    for i in conn.response[0]['raw_attributes']['memberUid']: # convert bytes list (from ldap) to str list
        memberUids.append(i.decode('ascii'))
    for id in group['people']: # add memberUid if necessary
        if not id in memberUids:
            logging.info('    Add memberUid to ldap group: ' + id)    
            (conn.modify('cn=' + group['name'] + ',' + domain,{'memberUid': [(MODIFY_ADD, id)]})) # Add memberUid to the group
    for id in memberUids: # delete memberUid if necessary
        if not id in group['people']: # person need to be removed from the group
            logging.info('    MemberUid not in group people, will delete entry: ' + id)
            conn.modify('cn=' + group['name'] + ',' + domain,{'memberUid': [(MODIFY_DELETE, id)]}) # Add all memberUid to the group
    return
    
def ldap_sync_user(conn, person, userDomain):
    logging.info('Syncing ' + person['id'] + ': ' + person['first_name'] + " " + person['last_name'] + " v/o " + person['nickname'])
    if person['email'] == None or len(person['last_name']) == 0: # only create, if mail and last_name available
        logging.info('  User does not have email or last name, thus no user will be created!')
        return
    if conn.search(userDomain, '(uid=' + person['id'] + ')', attributes=['mail', 'o']): # check if user exists
        res = str(conn.entries[0]).splitlines()
        if res[1].rsplit('mail: ')[1].strip('\r\n') == person['email']: # check if the midata and ldap mail address is the same
            logging.debug('  User exists already in LDAP, mailaddress is the same')
        else:
            logging.debug('  User exists already in LDAP, mailaddress is different')
            # mail_mailChange(person) # Notify user about mailchange in Midata (Attention: Will send an email every time the script executes!!!)
            # uncomment line below to always synchronize mailaddress. Attention, could confuse people!
            # conn.modify('uid=' + person['id'] + ',' + userDomain, {'mail': [(MODIFY_REPLACE, [person['email']])]}) # update the mailaddress in ldap
        try:
            if res[2].rsplit('o: ')[1].strip('\r\n') == person['level']: # check if the authorization level is still correct
                logging.debug('  User exists already in LDAP, authorization level is the same')
            else:
                logging.info('  User exists already in LDAP, authorization level is different')
                conn.modify('uid=' + person['id'] + ',' + userDomain, {'o': [(MODIFY_REPLACE, [person['level']])]})
                if person['level'] == 'PfadiAargau': # new access to reservation system and website
                    mail_levelUpgrade(person)
        except: # o attribute not available (switching from old sync script to new sync script)
                logging.debug('  User exists already in LDAP, authorization level attribute is not existent, create new attribute')
                conn.modify('uid=' + person['id'] + ',' + userDomain, {'o': [(MODIFY_ADD, [person['level']])]})
    else:
        logging.debug('  User does not exist in LDAP, create new user')
        return ldap_create_user(conn, person, userDomain) # user does not exist, create new one
    
def ldap_create_user(conn, person, userDomain):
    # create cn, homeDirectory and displayName
    if len(person['nickname']) > 0:
        cn = person['first_name'] + " " + person['last_name'] + " v/o " + person['nickname']
        homeDirectory = '/home/' + person['last_name'].lower() + person['nickname'].lower()
        displayName = person['nickname']
    else:
        cn = person['first_name'] + " " + person['last_name']
        homeDirectory = '/home/' + person['last_name'].lower() + person['first_name'].lower()
        displayName = person['first_name'] + " " + person['last_name']
        
    # generate password
    userPasswordClear = passgen.passgen(12)
    userPassword = hashed(HASHED_SALTED_SHA, userPasswordClear)
    
    conn.add('uid=' + str(person['id']) + ',' + userDomain,
                attributes={
                    'objectClass': ['inetOrgPerson', 'posixAccount'],
                    'givenName': person['first_name'],
                    'sn': person['last_name'],
                    'uid': person['id'],
                    'cn': cn,
                    'homeDirectory': homeDirectory,
                    'uidNumber': person['id'],
                    'displayName': displayName,
                    'mail': person['email'],
                    'userPassword': userPassword,
                    'gidNumber': 9000,
                    'o': person['level']
                    }
            )
    if conn.search(userDomain, '(uid=' + person['id'] + ')', attributes=['mail']): # check if user exists
        logging.info('  User successfully created in LDAP')
        mail_welcome(person, userPasswordClear)
    else:
        logging.error('  Could not create user in LDAP!')
    return True
            
def replace_special_characters(text):
    if text is None:
        return ''
    return text.replace('ä', 'ae').replace('ü', 'ue').replace('ö', 'oe').replace('é', 'e').replace('è', 'e').replace(
        'à', 'a').replace('Ï', 'i').replace('æ', 'ae').replace('ñ', 'n').replace('õ', 'o').replace('ï', 'i').replace(
        'ž', 'z').replace('á', 'a').replace('í', 'i').replace('É', 'E').replace('û', 'u').replace('Ü', 'Ue').replace(
        'Ä', 'Ae').replace('Ö', 'Oe').replace('ë', 'e')


def query_midata(request, authToken):
    baseurl = "https://db.scout.ch/"
    headers = {"Accept": "application/json"}
    try:
        res = session.get(baseurl + request + ".json?token=" + authToken, headers=headers)
    except:
        logging.error('Failed to get data from Midata!')
        raise
    if 'error' in res.json():
        logging.error('No access to Midata or wrong request!')
        raise Exception("No access to Midata or wrong request!")
    else:
        return res.json()

def query_group_people(group_id, authToken):
    return query_midata('groups/' + str(group_id) + '/people', authToken)
    
def query_group_person(group_id, person_id, authToken):
    return query_midata('groups/' + str(group_id) + '/people/' + str(person_id), authToken)

def query_group_info(group_id, authToken):
    return query_midata('groups/' + str(group_id), authToken)
    
def query_midata_hierarchy(authToken):
    return query_midata("/list_groups", authToken)['groups']
    
def query_event_people(group_id, event_id, authToken):
    return query_midata('groups/' + str(group_id) + '/events/' + str(event_id) + '/participations', authToken)['event_participations']
    
def find_all_subgroups(list, group_id):
    logging.debug('Find subgroups of group ' + str(group_id))
    groups = [group_id]
    pattern = [group_id]
    while 1:
        results = []
        for item in list:
            if item['parent_id'] in pattern:
                logging.debug('Found subgroup ' + str(item['id']))
                results.append(item['id'])
        if results == []:
            return groups
        else:
            pattern = results
            groups.extend(results)
    return groups
    
def add_person_to_people(person, people, level):
    if person['id'] in people:
        logging.debug('Person exists in People: ' + str(person['id']) + ', ' + str(person['nickname']))
        if level == 'PfadiAargau':
            logging.debug('Set level PfadiAargau for ' + str(person['id']) + ', ' + str(person['nickname']))
            people[person['id']]['level'] = level
    else:
        # replace Umlaute
        person['nickname'] = replace_special_characters(person['nickname'])
        person['first_name'] = replace_special_characters(person['first_name'])
        person['last_name'] = replace_special_characters(person['last_name'])
        
        people[person['id']] = {}
        people[person['id']]['id'] = person['id']
        people[person['id']]['first_name'] = person['first_name']
        people[person['id']]['last_name'] = person['last_name']
        people[person['id']]['nickname'] = person['nickname']
        people[person['id']]['email'] = person['email']
        people[person['id']]['level'] = level
        logging.info('    Add to people: ' + str(person['id']) + ', ' + str(person['first_name']) + ' ' + str(person['last_name']) + ' v/o ' + str(person['nickname']) + ', ' + str(person['email']) + ', ' + level)
    return

def mail_welcome(person, password):
    if person['level'] == 'PfadiAargau':
        SUBJECT = 'Zugangsdaten PfadiCloud, Reservationssystem und Website Pfadi Aargau'
        TEXT = 'Guten Tag ' + getName(person) + '<br /><br />Die Pfadi Aargau stellt den Abteilungen, den kantonalen Teams und den Ausbildungskursen unter ' \
            '<a href=\"https://cloud.pfadiaargau.ch\">cloud.pfadiaargau.ch</a> eine zentrale Dateiablage zur Verf&uuml;gung (&auml;hnlich wie Dropbox).' \
            '   Eine Anleitung findest du im Anhang, Informationen zur Verwendung in deinem Team erh&auml;ltst du von deinem Team- oder Kursleiter.<br /><br />' \
            ' Wenn du die Dateien mit deinem Computer oder Smartphone synchronisieren m&ouml;chtest,' \
            ' findest du die ben&ouml;tigte Software unter <a href=\"https://nextcloud.com/install/#install-clients\">nextcloud.com/install/</a>.' \
            '<br /><br />Dein Benutzername für die PfadiCloud ist: ' + person['email'] + '<br />' \
            'Du musst dir beim ersten Login mit der Passwort vergessen/Passwort zurücksetzen Funktion ein Passwort setzen. '\
            'Du wirst dann eine Email auf die obige Adresse zum setzen eines Passwortes erhalten. <br />'\
            'Mit dem gleichen Login kannst du dann auch die Sitzungszimmer der Pfadi Aargau <a href=\"https://reservation.pfadiaargau.ch/Web/?">reservieren.</a> '\
            'Falls du einem Team der Pfadi Aargau hinzugefügt wurdest, kann du ab nun auch deine Teamseite auf der <a href=\"http://www.pfadiaargau.ch/wp-admin">Website</a> bearbeiten.<br /><br />'\
            'Noch Fragen?<br /><blockquote>— DeinE Team- oder KursleiterIn hilft dir gerne weiter.</blockquote>' \
            '<blockquote>— Bei technischen Problemen unterstützt dich das <a href=\"mailto:webteam@pfadiaargau.ch\">Webteam</a>.</blockquote><br />' \
            'Viele Gr&uuml;sse<br />Webteam Pfadi Aargau'
    else:
        SUBJECT = 'Zugangsdaten PfadiCloud Pfadi Aargau'
        TEXT = 'Guten Tag ' + getName(person) + '<br /><br />Die Pfadi Aargau stellt den Abteilungen und kantonalen Teams unter ' \
            '<a href=\"https://cloud.pfadiaargau.ch\">cloud.pfadiaargau.ch</a> eine zentrale Dateiablage zur Verf&uuml;gung (&auml;hnlich wie Dropbox).' \
            '   Eine Anleitung findest du im Anhang, Informationen zur Verwendung in deiner Abteilung erh&auml;ltst du von deinem Abteilungs- oder Stufenleiter.<br /><br />' \
            ' Wenn du die Dateien mit deinem Computer oder Smartphone synchronisieren m&ouml;chtest,' \
            ' findest du die ben&ouml;tigte Software unter <a href=\"https://nextcloud.com/install/#install-clients\">nextcloud.com/install/</a>.' \
            '<br /><br />Dein Benutzername für die PfadiCloud ist: ' + person['email'] + '<br />' \
            'Du musst dir beim ersten Login mit der Passwort vergessen/Passwort zurücksetzen Funktion ein Passwort setzen. '\
            'Du wirst dann eine Email auf die obige Adresse zum setzen eines Passwortes erhalten. <br />'\
            'Noch Fragen?<br /><blockquote>— DeinE Abteilungs- oder StufenleiterIn hilft dir gerne weiter.</blockquote>' \
            '<blockquote>— Bei technischen Problemen unterstützt dich das <a href=\"mailto:webteam@pfadiaargau.ch\">Webteam</a>.</blockquote><br />' \
            'Viele Gr&uuml;sse<br />Webteam Pfadi Aargau'

    # Attach Cover Letter to the email
    cover_letter = MIMEApplication(open("/opt/scripts/PfadiCloud.pdf", "rb").read())
    cover_letter.add_header('Content-Disposition', 'attachment', filename="PfadiCloud.pdf")

    if mail_send(person, SUBJECT, TEXT, cover_letter):
        logging.info('  Welcome mail sent to ' + person['email'])
    else:
        logging.error('  Error while sending the welcome email!')
        
def mail_error(file, name, email):

    SUBJECT = 'Error beim syncLDAP Skript'
    TEXT = 'Hallo<br />Beim Versuch, das LDAP mit der Midata zu synchronisieren, ist ein Fehler aufgetreten. Mehr Infos gibt es im Anhang.'

    # Attach Cover Letter to the email
    cover_letter = MIMEApplication(open(file, "rb").read())
    cover_letter.add_header('Content-Disposition', 'attachment', filename=name)
    
    person = {'email': email}

    if mail_send(person, SUBJECT, TEXT, cover_letter):
        logging.info('  Error mail sent to ' + email)
    else:
        logging.error('  Error while sending the error email!')
    
def mail_levelUpgrade(person):
    SUBJECT = 'Zugang zum Reservationssystem und Website der Pfadi Aargau'
    TEXT = 'Guten Tag ' + getName(person) + '<br /><br />Du wurdest vor kurzem einem Team der Pfadi Aargau oder einem Ausbildungskurs auf Midata hinzugefügt.'\
        ' Mit deinem bisherigen Login der Pfadicloud kannst du ab sofort auch die Sitzungszimmer der Pfadi Aargau <a href=\"https://reservation.pfadiaargau.ch/Web/?">reservieren</a>.'\
        ' Falls du einem Team der Pfadi Aargau hinzugefügt wurdest, kann du ab nun auch deine Teamseite auf der <a href=\"http://www.pfadiaargau.ch/wp-admin">Website</a> bearbeiten.<br /><br />'\
        'Noch Fragen?<br /><blockquote>— DeinE Team- oder KursleiterIn hilft dir gerne weiter.</blockquote>' \
        '<blockquote>— Bei technischen Problemen unterstützt dich das <a href=\"mailto:webteam@pfadiaargau.ch\">Webteam</a>.</blockquote><br />' \
        'Viele Gr&uuml;sse<br />Webteam Pfadi Aargau'

    if mail_send(person, SUBJECT, TEXT):
        logging.info('  Upgrade mail sent to ' + person['email'])
    else:
        logging.error('  Error while sending the upgrade email!')

def mail_mailChange(person):
    SUBJECT = 'Änderung deiner Midata Mailadresse'
    if person['level'] == 'PfadiAargau':
        TEXT = 'Guten Tag ' + getName(person) + '<br /><br />Du hast vor kurzem deine Mailadresse auf Midata geändert. Wir möchten dich darauf hinweisen, dass du dich'\
            ' weiterhin mit deiner vorherigen Mailadresse auf der Pfadicloud, der Pfadi Aargau Website und dem'\
            ' Sitzungszimmer-Reservationstool anmelden musst. Falls du die Mailadresse auch dort anpassen willst, melde dich bitte beim <a href=\"mailto:webteam@pfadiaargau.ch\">Webteam der Pfadi Aargau</a>.'
    else:
        TEXT = 'Guten Tag ' + getName(person) + '<br /><br />Du hast vor kurzem deine Mailadresse auf Midata geändert. Wir möchten dich darauf hinweisen, dass du dich'\
            ' weiterhin mit deiner vorherigen Mailadresse auf der Pfadicloud anmelden musst. Falls du die Mailadresse auch dort anpassen willst,'\
            ' melde dich bitte beim <a href=\"mailto:webteam@pfadiaargau.ch\">Webteam der Pfadi Aargau</a>.'
    if mail_send(person, SUBJECT, TEXT):
        logging.info('  Mailchange email sent to ' + person['email'])
    else:
        logging.error('  Error while sending the mailchange email!')

def mail_send(person, SUBJECT, TEXT, cover_letter = None):

    #return 1# Disable emails

    msg = MIMEMultipart()
    msg['Subject'] = SUBJECT
    msg['From'] = mailuser
    msg['To'] = person['email']
    body = MIMEText(TEXT, 'html')
    msg.attach(body)
    
    if cover_letter != None:
        msg.attach(cover_letter)
        
    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (mailuser, person['email'], SUBJECT, TEXT)
    try:
        server_ssl = smtplib.SMTP_SSL(mailserver, mailport)
        server_ssl.ehlo()
        server_ssl.login(mailuser, mailpwd)
        server_ssl.sendmail(mailuser, person['email'], msg.as_string())
        server_ssl.close()
    except:
        return 0 # not successful
        
    return 1 # successful

def getName(person):
    if len(person['nickname']) > 0:
        return(person['nickname'])
    else:
        return(person['first_name'] + " " + person['last_name'])

if __name__ == "__main__":
    main()
    if len(person['nickname']) > 0:
        return(person['nickname'])
    else:
        return(person['first_name'] + " " + person['last_name'])

if __name__ == "__main__":
    main()
