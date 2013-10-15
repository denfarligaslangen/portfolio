#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random

def load(file_name):
    """Loads a .json file with a given filename. Returns None if file is not found. Returns a list if all is well."""
    try:
        with open(file_name,"r") as f:
            data = json.load(f)
            return data
    
    except:
        return None

def add_project():
    herk

def remove_project(file_name,db,ID):
    for i in range(len(db)):
        if db[i]['project_no'] == ID:
            db.pop(i)
            break
        elif i == len(db) - 1:
            return None

    with open(file_name, "w") as f:
        f.write("{}".format(json.dumps(db, indent=2)))

    return db

def edit_project():
    herp

def get_project_count(db):
    """Returns the current number of projects as an integer"""
    return len(db)

def get_project(db, id):
    """Returns specific project by a given ID"""
    for i in range(len(db)):
        project_data = db[i]
        if project_data.get('project_no') == id:
            return project_data

    return None

def search(db, sort_by=u'start_date', sort_order=u'desc', techniques=None, search=None, search_fields=None):
    """Searches given database for free text or a given technique and sorts it, returns a list"""
    search_result = list(db)
    remove_result = []  

    if search_fields == []:
        return []

    if techniques != None:
        tech_search(search_result, remove_result, techniques)
    
    if search != None and search_fields == None:
        free_search(search, search_result, remove_result)
    
    elif search != None:
        field_search(search_result, search, search_fields, remove_result)
                                         
    remove_result.sort(reverse = True)

    for n in remove_result:
        search_result.pop(n)

    search_result = sorted(search_result, key=lambda k: k[sort_by], reverse = sort_order == u'desc')

    return search_result

def tech_search(search_result, remove_result, techniques):
    """Compares a given list of techniques with the techniques of each project in 'search_result'-list. If the technique doesn't exist in the project, the projects index is added to the remove_result list."""
    for i in range(len(search_result)):
            techniques_used = search_result[i].get('techniques_used')
            for tech in techniques:
                if tech not in techniques_used and i not in remove_result:
                   remove_result.insert(0, i)

def free_search(search, search_result, remove_result):
    """Searches all fields in the search_result list for a given freetext string. If no field matches the string, the project id is added to the remove_result list."""
    for i in range(len(search_result)):
            search_result_dict = search_result[i].values()
            search_result_dict = set(str(v).lower() for v in search_result_dict)
            tech_found = False

            for tech in search_result[i]['techniques_used']:
                if tech.lower() == search.lower():
                    tech_found = True

            if search.lower() not in search_result_dict and tech_found == False and i not in remove_result:
                remove_result.insert(0, i)

def field_search(search_result, search, search_fields, remove_result):
    """Searches the search_result list, in the fields given in the search_fields list, for a given freetext string. If no field matches the string, the project id is added to the remove_result list."""
    for i in range(len(search_result)):
            field_count = 0
            for field in search_fields:
                field_content = search_result[i].get(field)
                if field != 'techniques_used' and search.lower() not in str(field_content).lower() and i not in remove_result:
                    field_count += 1
                    if field_count == len(search_fields):
                        remove_result.insert(0, i)
                
                elif field == 'techniques_used':
                    found_tech = False
                    for j in range(len(field_content)):
                        if search.lower() in field_content[j].lower():
                            found_tech = True
                    if not found_tech:
                        field_count += 1
                        if field_count == len(search_fields):
                            remove_result.insert(0, i)

def get_techniques(db):
    """Returns a summary of all techniques used in all projects as a list."""
    all_techniques = []
    for i in range(len(db)):
        project_data = db[i]
        techs = project_data.get('techniques_used')
        for j in techs:
            if j not in all_techniques: 
                all_techniques.append(j)

    return sorted(all_techniques)

def get_technique_stats(db):
    """Returns a dict of techniques and corresponding projects"""
    all_techniques = get_techniques(db)
    tech_dict = {}
    for technique in all_techniques:
        project_list = []
        for i in range(len(db)):
            project_data = db[i]
            techs = project_data.get('techniques_used')
            if technique in techs: 
                project_name = project_data.get('project_name')
                project_no = project_data.get('project_no')
                stat_dict = {u'id': project_no, u'name': project_name}
                project_list.insert(0, stat_dict)

        tech_dict[technique] = project_list

    return tech_dict

def get_random_projects(db):
    """Picks a random project, returns small-image-url and project-name"""
    proj_i = random.randint(0,len(db)-1)
    image = db[proj_i]["small_image"]
    name = db[proj_i]["project_name"]
    short = db[proj_i]["short_description"]
    return image, name, short

