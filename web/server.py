#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import flask
import jinja2
import os
import data
import logging

env = jinja2.Environment(loader=jinja2.FileSystemLoader( searchpath=os.getcwd()+"/templates" ))

app = flask.Flask(__name__, static_folder='style')

app.debug = True

logging.basicConfig(filename='log.txt', level=logging.INFO)

@app.route('/')
def root():
    status = 0
    db = data.load("data.json")
    if db == None: 
        status = 1
    else:
        small_image, project_name, short = data.get_random_projects(db)
    
    template_file = "root.jinja"
    template = env.get_template( template_file )
    if status == 0:
        templateVars = { "status": status, "project" : str(project_name), "thumb" : small_image, "short_desc" : short, "style": flask.url_for('static',filename='style.css')  }
    elif status == 1:
        templateVars = { "status": status, "style": flask.url_for('static',filename='style.css') }
    
    return template.render( templateVars )

@app.route('/list', methods=['GET', 'POST'])
def mylist():
    status = 0
    db = data.load("data.json")
    if db == None:
        status = 1
    else:
        tech_list = data.get_techniques(db)
        search_text = None
        field_list = []
        checked_tech_list = []

        if flask.request.method == 'POST':
            sort_o = u'desc'
            sort_by_field = 'start_date'
            key_number = 0
            tech_number = 0
        
            for key in db[0].keys():
                key_number += 1
                try:
                    field_list.append(flask.request.form['field_'+key])
                except:
                    if key_number == len(db[0]) and field_list == []:
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
        
            result = data.search(db=db, sort_by=sort_by_field, sort_order=sort_o, search=search_text, techniques=checked_tech_list, search_fields=field_list)
        
        else:
            result = data.search(db=db)

        if search_text == None: search_text = ""

    template_file = "list.jinja"
    template = env.get_template( template_file )
    if status == 0:
        templateVars = { "status": status, "result" : result, "db" : db, "search_text" : search_text, "techs": tech_list, "checked_fields": field_list, "checked_techs": checked_tech_list, "style": flask.url_for('static',filename='style.css') }
        logging.info('Searched for: '+search_text)
    elif status == 1:
        templateVars = { "status": status, "style" : flask.url_for('static',filename='style.css') }

    return template.render( templateVars )

@app.route('/techniques')
def techniques():
    status = 0
    db = data.load("data.json")
    if db == None:
        status = 1
    else:
        techs = data.get_techniques(db)

    template_file = "techniques.jinja"
    template = env.get_template( template_file )
    if status == 0:
        templateVars = { "status": status, "techs" : techs, "stats" : data.get_technique_stats(db), "style": flask.url_for('static',filename='style.css') }
    else:
        templateVars = { "status": status }

    return template.render( templateVars )

@app.route('/project/<projectID>')
def project(projectID):
    status = 0
    db = data.load('data.json')
    if db == None:
        status = 1
    else:
        p = data.get_project(db, int(projectID))
        if p == None:
            status = 2

    template_file = "project.jinja"
    template = env.get_template( template_file )
    if status == 0:
        templateVars = { "status": status, "project": p, "style": flask.url_for('static',filename='style.css') }
    else:
        templateVars = { "status": status }

    return template.render( templateVars )

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    db = data.load("data.json")
    is_logged_in = False
    user = ""
    passwd = ""
    if flask.request.method == 'POST':
        user = flask.request.form['user_name']
        passwd = flask.request.form['passwd']
        remove = flask.request.form['remove']
        
        if user == 'admin' and passwd == 'h':
            is_logged_in = True

        if remove.isdigit() and is_logged_in:
            db = data.remove_project(db,'data.json',int(remove))

    template_file = "admin.jinja"
    template = env.get_template( template_file )
    templateVars = { 'db':db, 'is_logged_in': is_logged_in, 'user_name': user, 'passwd': passwd }

    return template.render( templateVars )

@app.route('/admin/addit', methods=['GET', 'POST'])
def addit():
    db = data.load("data.json")
    projectdb = data.load('empty_project.json')
    project = projectdb[0]

    is_logged_in = False
    user = ""
    passwd = ""

    if flask.request.method == 'POST':
        user = flask.request.form['user_name']
        passwd = flask.request.form['passwd']
        edit = flask.request.form['edit']
        
        try:
            for key in project.keys():
                if key == 'project_no' and not edit.isdigit():
                    project[key] = flask.request.form[key]
                elif key == 'group_size' or key == 'project_no':
                    project[key] = int(flask.request.form[key])
                elif key == 'techniques_used':
                    project[key] = [s.strip("' ") for s in flask.request.form[key][1:-1].split(',')]
                else:
                    project[key] = flask.request.form[key]

            if not edit.isdigit():
                db = data.add_project(db,'data.json',project)
            else:
                db = data.edit_project(db,'data.json',int(flask.request.form['project_no']),project)
        except:
            print('except edit')

        if user == 'admin' and passwd == 'h':
            is_logged_in = True

        if edit.isdigit() and is_logged_in:
            project = data.get_project(db,int(edit))

    template_file = "addit.jinja"
    template = env.get_template( template_file )
    templateVars = { 'db':db, 'is_logged_in': is_logged_in, 'user_name': user, 'passwd': passwd, 'project': project }

    return template.render( templateVars )

if __name__ == '__main__':
    app.run()
