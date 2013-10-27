#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#This is the server program of SimThebl Portfolio. It sets up the server environment, all the pages and then runs the app.
#Authors: simgu002 and thebl297 2013

import flask
import jinja2
import os
import data
import logging

env = jinja2.Environment(loader=jinja2.FileSystemLoader( searchpath=os.getcwd()+"/templates" )) #Tells jinja where to find templates and how to load them.

app = flask.Flask(__name__) #Creates an instance of the flask class and names it.

app.debug = True

logging.basicConfig(filename='log.txt', level=logging.INFO)

@app.route('/')
def root():
    """The "home" page. Loads a database and displays a random project"""
    status = 0
    db = data.load("data.json")
    if db == None: 
        status = 1
    else:
        small_image, project_name, short, projectID = data.get_random_projects(db)
    
    template_file = "root.jinja"
    template = env.get_template( template_file )
    if status == 0:
        templateVars = { "status": status, "project" : str(project_name), "pid": projectID, "thumb" : small_image, "short_desc" : short, "style": flask.url_for('static',filename='style/style.css'), "pic": flask.url_for('static', filename="style/"), "projpic": flask.url_for('static', filename="images/") }
    elif status == 1:
        templateVars = { "status": status, "style": flask.url_for('static', filename="style.css") }
    
    return template.render( templateVars )

@app.route('/list', methods=['GET', 'POST'])
def mylist():
    """The "search" page. Displays all search option and all projects matching a search"""
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

            for tech in tech_list:
                tech_number += 1
                try:
                    checked_tech_list.append(flask.request.form['tech_'+tech])
                except:
                    if tech_number == len(tech_list) and checked_tech_list == []:
                        checked_tech_list = None

            try:
                sort_by_field = (flask.request.form['sort_by_field'])
            except:
                pass
        
            search_text = flask.request.form['free_text']
            if search_text == "":
                search_text = None

            try:
                sort_o = flask.request.form['ascending']
            except:
                pass
        
            result = data.search(db=db, sort_by=sort_by_field, sort_order=sort_o, search=search_text, techniques=checked_tech_list, search_fields=field_list)
        
        else:
            result = data.search(db=db)

        if search_text == None: search_text = ""

    template_file = "list.jinja"
    template = env.get_template( template_file )
    if status == 0:
        templateVars = { "status": status, "result" : result, "db" : db, "search_text" : search_text, "techs": tech_list, "checked_fields": field_list, "checked_techs": checked_tech_list, "style": flask.url_for('static',filename='style/style.css'), "projpic": flask.url_for('static', filename="images/") }
        logging.info('Searched for: '+search_text)
    elif status == 1:
        templateVars = { "status": status, "style" : flask.url_for('static',filename='style.css') }

    return template.render( templateVars )

@app.route('/techniques')
def techniques():
    """The "technique" page. Displays all techniques in a database and all projects related to them"""
    status = 0
    db = data.load("data.json")
    if db == None:
        status = 1
    else:
        techs = data.get_techniques(db)

    template_file = "techniques.jinja"
    template = env.get_template( template_file )
    if status == 0:
        templateVars = { "status": status, "techs" : techs, "stats" : data.get_technique_stats(db), "style": flask.url_for('static',filename='style/style.css') }
    else:
        templateVars = { "status": status }

    return template.render( templateVars )

@app.route('/project/<projectID>')
def project(projectID):
    """The "project" page. Displays a single project from a database by a given ID"""
    status = 0
    db = data.load('data.json')
    if db == None:
        status = 1
    else:
        if projectID.isdigit():
            projectID = int(projectID)

        p = data.get_project(db, projectID)

        if p == None:
            status = 2

    template_file = "project.jinja"
    template = env.get_template( template_file )
    if status == 0:
        templateVars = { "status": status, "project": p, "style": flask.url_for('static',filename='style/style.css') }
    else:
        templateVars = { "status": status }

    return template.render( templateVars )

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """The "admin" page. Displays a database to the admin with options to modify, add and remove projects"""
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
    """The "modify/add" page. Lets the admin modify an existing project, or add a new one"""
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
            logging.info('Error when trying to add or edit post in db')

        if user == 'admin' and passwd == 'h':
            is_logged_in = True

        if edit.isdigit() and is_logged_in:
            project = data.get_project(db,int(edit))

    template_file = "addit.jinja"
    template = env.get_template( template_file )
    templateVars = { 'db':db, 'is_logged_in': is_logged_in, 'user_name': user, 'passwd': passwd, 'project': project }

    return template.render( templateVars )

@app.errorhandler(404)
def error_page(error):
    """Displays an error message when error code 404 is encountered"""
    return "<h2>Quoth the server: 404 >:)</h2>"

if __name__ == '__main__':
    app.run()
