# schema.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


import colander
import deform
from deform.widget import OptGroup

import logging
logger = logging.getLogger(__name__)

from .wps import get_wps


class CredentialsSchema(colander.MappingSchema):
    """
    ESGF user credentials schema
    """
    openid = colander.SchemaNode(
        colander.String(),
        title = "OpenID",
        description = "OpenID from your ESGF provider",
        validator = colander.url,
        missing = '',
        default = '',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    password = colander.SchemaNode(
        colander.String(),
        title = 'Password',
        description = 'Password for this OpenID',
        missing = '',
        default = '',
        widget = deform.widget.PasswordWidget(size=20))

class AccountSchema(colander.MappingSchema):
    """
    User account schema
    """
    name = colander.SchemaNode(
        colander.String(),
        title = "Name",
        description = "Your Name",
        missing = '',
        default = '',
        )
    email = colander.SchemaNode(
        colander.String(),
        title = "EMail",
        description = "eMail used for login",
        validator = colander.Email(),
        missing = '',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    openid = colander.SchemaNode(
        colander.String(),
        title = "OpenID",
        description = "OpenID to access ESGF data",
        validator = colander.url,
        missing = '',
        default = '',
        )
    organisation = colander.SchemaNode(
        colander.String(),
        title = "Organisation",
        description = "Your Organisation",
        missing = '',
        default = '',
        )
    notes = colander.SchemaNode(
        colander.String(),
        title = "Notes",
        description = "Some Notes about you",
        missing = '',
        default = '',
        )
    token = colander.SchemaNode(
        colander.String(),
        title = "Token",
        description = "Access Token",
        missing = '',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    credentials = colander.SchemaNode(
        colander.String(),
        title = "Credentials",
        description = "URL to ESGF Proxy Certificate",
        validator = colander.url,
        missing = '',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    cert_expires = colander.SchemaNode(
        colander.String(),
        title = "Expires",
        description = "When your Proxy Certificate expires",
        missing = '',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )

# process list
# ------------

@colander.deferred
def deferred_select_process_widget(node, kw):
    wps = get_wps(kw.get('wps_url'))
    allow_admin = kw.get('allow_admin')

    test_group = []
    csc_group = []
    dkrz_group = []
    base_group = []
    c3grid_group = []
    other_group = []
    for process in wps.processes:
        if 'test' in process.identifier:
            test_group.append( (process.identifier, process.title) )
        elif 'de.csc' in process.identifier:
            csc_group.append( (process.identifier, process.title) )
        elif 'de.dkrz' in process.identifier:
            dkrz_group.append( (process.identifier, process.title) )
        elif 'org.malleefowl' in process.identifier:
            base_group.append( (process.identifier, process.title) )
        elif 'de.c3grid' in process.identifier:
            c3grid_group.append( (process.identifier, process.title) )
        else:
            other_group.append( (process.identifier, process.title) )
    choices = [ ('', 'Select Process') ]
    if allow_admin and len(base_group) > 0:
        choices.append( OptGroup('Base', *base_group) )
    if len(test_group) > 0:
        choices.append( OptGroup('Test', *test_group) )
    if len(c3grid_group) > 0:
        choices.append( OptGroup('C3Grid', *c3grid_group) )
    if len(csc_group) > 0:
        choices.append( OptGroup('CSC', *csc_group) )
    if len(dkrz_group) > 0:
        choices.append( OptGroup('DKRZ', *dkrz_group) )
    if len(other_group) > 0:
        choices.append( OptGroup('Other', *other_group) )
    
    return deform.widget.SelectWidget(
        values = choices,
        long_label_generator = lambda group, label: ' - '.join((group, label))
        )

class ProcessSchema(colander.MappingSchema):
    process = colander.SchemaNode(
        colander.String(),
        title = "WPS Process",
        widget = deferred_select_process_widget)

@colander.deferred
def deferred_wps_list_widget(node, kw):
    wps_list = kw.get('wps_list', [])
    return deform.widget.RadioChoiceWidget(
        values =wps_list,
        )

class SelectWPSSchema(colander.MappingSchema):
   
    url = colander.SchemaNode(
        colander.String(),
        title = 'WPS',
        description = "Select WPS",
        widget = deferred_wps_list_widget
        )

# catalog
# -------

class CatalogSchema(colander.MappingSchema):
    url = colander.SchemaNode(
        colander.String(),
        title = 'URL',
        description = 'Add WPS URL',
        missing = '',
        default = '',
        validator = colander.url,
        widget = deform.widget.TextInputWidget())

    username = colander.SchemaNode(
        colander.String(),
        title = 'Username',
        description = 'Username to access WPS (optional)',
        missing = '',
        default = '',
        widget = deform.widget.TextInputWidget())

    password = colander.SchemaNode(
        colander.String(),
        title = 'Password',
        description = 'Password to access WPS (optional)',
        missing = '',
        default = '',
        widget = deform.widget.PasswordWidget(size=20))
    
    notes = colander.SchemaNode(
        colander.String(),
        title = 'Notes',
        description = 'Add some notes for this WPS',
        missing = '',
        default = '',
        widget = deform.widget.TextInputWidget())


# Admin
# -----

def user_choices(user_list):
    choices = []
    for user in user_list:
        label = "%s (%s, %s, %s, %s, %s, %s)" % (user.get('user_id'),
                                                 user.get('name', ''),
                                                 user.get('openid', ''),
                                                 user.get('organisation', ''),
                                                 user.get('notes', ''),
                                                 user.get('activated', ''),
                                                 user.get('token', ''))
        choices.append( (user.get('user_id'), label) )
    return choices

@colander.deferred
def deferred_all_users_widget(node, kw):
    request = kw.get('request')
    from .models import all_users
    return deform.widget.CheckboxChoiceWidget(values=user_choices(all_users(request)))

@colander.deferred
def deferred_deactivated_users_widget(node, kw):
    request = kw.get('request')
    from .models import deactivated_users
    return deform.widget.CheckboxChoiceWidget(values=user_choices(deactivated_users(request)))

@colander.deferred
def deferred_activated_users_widget(node, kw):
    request = kw.get('request')
    from .models import activated_users
    return deform.widget.CheckboxChoiceWidget(values=user_choices(activated_users(request)))

class AdminUserEditSchema(colander.MappingSchema):
    user_id = colander.SchemaNode(
        colander.Set(),
        title = "Users",
        widget = deferred_all_users_widget,
        validator=colander.Length(min=1),
        )

class AdminUserEditTaskSchema(colander.MappingSchema):
    name = colander.SchemaNode(
        colander.String(),
        title = "User Name",
        description = "Enter User Name",
        missing = '',
        default = '',
        )
    email = colander.SchemaNode(
        colander.String(),
        title = "EMail",
        description = "Enter eMail used for login",
        validator = colander.Email(),
        missing = '',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    openid = colander.SchemaNode(
        colander.String(),
        title = "OpenID",
        description = "Enter OpenID for data access",
        validator = colander.url,
        missing = '',
        default = '',
        )
    organisation = colander.SchemaNode(
        colander.String(),
        title = "Organisation",
        description = "The Organisation the User is working for",
        missing = '',
        default = '',
        )
    notes = colander.SchemaNode(
        colander.String(),
        title = "Notes",
        description = "Some Notes about this User",
        missing = '',
        default = '',
        )
    activated = colander.SchemaNode(
        colander.Boolean(),
        title = "Activated",
        description = "Check if user is allowed to use system",
        missing = False,
        default = False,
        )


class AdminUserRegisterSchema(colander.MappingSchema):
    name = colander.SchemaNode(
        colander.String(),
        title = "User Name",
        description = "Enter User Name",
        missing = '',
        default = '',
        )
    email = colander.SchemaNode(
        colander.String(),
        title = "EMail",
        description = "Enter eMail used for login",
        validator = colander.Email(),
        )
    openid = colander.SchemaNode(
        colander.String(),
        title = "OpenID",
        description = "Enter OpenID for data access",
        validator = colander.url,
        missing = '',
        default = '',
        )
    organisation = colander.SchemaNode(
        colander.String(),
        title = "Organisation",
        description = "The Organisation the User is working for",
        missing = '',
        default = '',
        )
    notes = colander.SchemaNode(
        colander.String(),
        title = "Notes",
        description = "Some Notes about this User",
        missing = '',
        default = '',
        )

class AdminUserUnregisterSchema(colander.MappingSchema):
    user_id = colander.SchemaNode(
        colander.Set(),
        title = "Users",
        widget = deferred_all_users_widget)

class AdminUserActivateSchema(colander.MappingSchema):
    user_id = colander.SchemaNode(
        colander.Set(),
        title = "Users",
        widget = deferred_deactivated_users_widget)

class AdminUserDeactivateSchema(colander.MappingSchema):
    user_id = colander.SchemaNode(
        colander.Set(),
        title = "Users",
        widget = deferred_activated_users_widget)

# jobs
# ----


@colander.deferred
def deferred_job_widget(node, kw):
    request = kw.get('request')
    from .models import jobs_information 
    jobs = jobs_information(request)
    from .widget import JobsWidget
    return JobsWidget(jobs = jobs)

    

class JobsSchema(colander.MappingSchema):
    process = colander.SchemaNode(
        colander.String(),
        title = "Jobs",
        missing=unicode(''),
        widget = deferred_job_widget
        )

class TableSchema(colander.MappingSchema):

    from widget import GenericTableWidget
    table = colander.SchemaNode(
        colander.String(),
        missing='',#do not show the required *
        widget = GenericTableWidget(),

    )

    def set_title(self,title="Table"):
        self.children[0].title=title

