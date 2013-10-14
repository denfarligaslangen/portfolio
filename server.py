#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import flask
import jinja2
import os
import data

env = jinja2.Environment(loader=jinja2.FileSystemLoader( searchpath=os.getcwd()+"/template" ))

app = flask.Flask(__name__)

app.debug = True

@app.route('/')
def root():
    db = data.load("data.json")
    small_image, project_name, short = data.get_random_projects(db)
    
    template_file = "root.jinja"
    template = env.get_template( template_file )
    templateVars = { "project" : str(project_name), "thumb" : small_image, "short_desc" : short  }
    
    return template.render( templateVars )

@app.route('/list', methods=['GET', 'POST'])
def mylist():
    database = data.load("data.json")
    tech_list = data.get_techniques(database)
    search_text = None
    field_list = []
    checked_tech_list = []

    if flask.request.method == 'POST':
        sort_o = u'desc'
        sort_by_field = 'start_date'
        key_number = 0
        tech_number = 0
        
        for key in database[0].keys():
            key_number += 1
            try:
                field_list.append(flask.request.form['field_'+key])
            except:
                if key_number == len(database[0]) and field_list == []:
                    field_list = None
                print("except herk")

        for tech in tech_list:
            tech_number += 1
            try:
                checked_tech_list.append(flask.request.form['tech_'+tech])
            except:
                if tech_number == len(tech_list) and checked_tech_list == []:
                    checked_tech_list = None
                print("Except 5")

        try:
            sort_by_field = (flask.request.form['sort_by_field'])
        except:
            print("Except4")
        
        try:
            search_text = flask.request.form['free_text']
            if search_text == "":
                search_text = None
        except:
            print("except")

        try:
            sort_o = flask.request.form['ascending']
        except:
            print("except2")
        
        result = data.search(db=database, sort_by=sort_by_field, sort_order=sort_o, search=search_text, techniques=checked_tech_list, search_fields=field_list)
        
    else:
        result = data.search(db=database)

    if search_text == None: search_text = ""

    template_file = "list.jinja"
    template = env.get_template( template_file )
    templateVars = { "result" : result, "db" : database, "search_text" : search_text, "techs": tech_list, "checked_fields": field_list, "checked_techs": checked_tech_list }

    return template.render( templateVars )

@app.route('/techniques')
def techniques():
    db = data.load("data.json")
    techs = data.get_techniques(db)

    template_file = "techniques.jinja"
    template = env.get_template( template_file )
    templateVars = { "techs" : techs, "stats" : data.get_technique_stats(db) }

    return template.render( templateVars )

@app.route('/project/<projectID>')
def project(projectID):
    db = data.load('data.json')
    p = data.get_project(db, int(projectID))

    template_file = "project.jinja"
    template = env.get_template( template_file )
    templateVars = { "project": p }

    return template.render( templateVars )

if __name__ == '__main__':
    app.run()
