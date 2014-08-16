import colander

from deform.widget import (
    RadioChoiceWidget,
    TextInputWidget,
    PasswordWidget,
    TextAreaWidget,
    SelectWidget 
    )
from .widget import (
    TagsWidget,
    EsgSearchWidget,
    EsgFilesWidget
    )

import logging
logger = logging.getLogger(__name__)

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
        widget = TextInputWidget(template='readonly/textinput'),
        )
    password = colander.SchemaNode(
        colander.String(),
        title = 'Password',
        description = 'Password for this OpenID',
        missing = '',
        default = '',
        widget = PasswordWidget(size=30))

class MyAccountSchema(colander.MappingSchema):
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
        widget = TextInputWidget(template='readonly/textinput'),
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
    credentials = colander.SchemaNode(
        colander.String(),
        title = "Credentials",
        description = "URL to ESGF Proxy Certificate",
        validator = colander.url,
        missing = '',
        widget = TextInputWidget(template='readonly/textinput'),
        )
    cert_expires = colander.SchemaNode(
        colander.String(),
        title = "Expires",
        description = "When your Proxy Certificate expires",
        missing = '',
        widget = TextInputWidget(template='readonly/textinput'),
        )

@colander.deferred
def deferred_wps_list_widget(node, kw):
    wps_list = kw.get('wps_list', [])
    choices = []
    for wps in wps_list:
        title = "%s (%s) [%s]" % (wps.get('title'), wps.get('abstract'), wps.get('source'))
        choices.append((wps.get('source'), title))
    return RadioChoiceWidget(values = choices)

class ChooseWPSSchema(colander.MappingSchema):
    url = colander.SchemaNode(
        colander.String(),
        title = 'WPS service',
        description = "Select WPS",
        widget = deferred_wps_list_widget
        )

@colander.deferred
def deferred_choose_process_widget(node, kw):
    processes = kw.get('processes', [])

    choices = []
    for process in processes:
        title = "%s [%s]" % (process.title, process.identifier)
        choices.append( (process.identifier, title) )
    return RadioChoiceWidget(values = choices)

class SelectProcessSchema(colander.MappingSchema):
    identifier = colander.SchemaNode(
        colander.String(),
        title = "WPS Process",
        widget = deferred_choose_process_widget)

@colander.deferred
def deferred_choose_input_parameter_widget(node, kw):
    process = kw.get('process', [])

    choices = []
    for dataInput in process.dataInputs:
        if dataInput.dataType == 'ComplexData':
            title = dataInput.title
            title += " [%s]" % (', '.join([value.mimeType for value in dataInput.supportedValues]))
            title += " (%d-%d)" % (dataInput.minOccurs, dataInput.maxOccurs)
            choices.append( (dataInput.identifier, title) )
    return RadioChoiceWidget(values = choices)

class ChooseInputParamterSchema(colander.MappingSchema):
    identifier = colander.SchemaNode(
        colander.String(),
        title = "Input Parameter",
        widget = deferred_choose_input_parameter_widget)

class ChooseSourceSchema(colander.MappingSchema):
    choices = [('wizard_csw', "CSW Catalog Search"), ('wizard_esgf', "ESGF Source")]
    source = colander.SchemaNode(
        colander.String(),
        widget = RadioChoiceWidget(values = choices))

def esgsearch_validator(node, value):
    import json
    search = json.loads(value)
    if search.get('hit-count', 0) > 20:
        raise Invalid(node, 'More than 20 datasets selected: %r.' %  search['hit-count'])

class ESGFSearchSchema(colander.MappingSchema):
    selection = colander.SchemaNode(
        colander.String(),
        validator = esgsearch_validator,
        title = 'ESGF Search',
        #missing = '{"query": "project:CORDEX"}',
        #default = '{"query": "project:CORDEX"}',
        widget = EsgSearchWidget(url="/esg-search"))

@colander.deferred
def deferred_esgf_files_widget(node, kw):
    import json
    selection = kw.get('selection', {})
    search = json.loads(selection)
    return EsgFilesWidget(url="/esg-search", search_type='File', search=search)
class ESGFFilesSchema(colander.MappingSchema):
    url = colander.SchemaNode(
        colander.Set(),
        description = 'URL',
        widget = deferred_esgf_files_widget)

class CatalogSearchSchema(colander.MappingSchema):
    pass
    
class DoneSchema(colander.MappingSchema):
    pass

class CatalogAddServiceSchema(colander.MappingSchema):
    url = colander.SchemaNode(
        colander.String(),
        title = 'Service URL',
        description = 'Add URL of OGC service (WPS, WMS, ...). Example: http://localhost:8091/wps',
        default = 'http://localhost:8091/wps',
        validator = colander.url,
        widget = TextInputWidget())
    resource_type = colander.SchemaNode(
        colander.String(),
        description = "Choose OGC service resource type.",
        default = 'http://www.opengis.net/wps/1.0.0',
        widget = RadioChoiceWidget(
            values=[('http://www.opengis.net/wps/1.0.0', "OGC:WPS 1.0.0"),
                    ('http://www.opengis.net/wms', "OGC:WMS 1.1.1"),
                    ('http://www.opengis.net/cat/csw/2.0.2', "OGC:CSW 2.0.2")])
        )

class PublishSchema(colander.MappingSchema):
    import uuid

    @colander.deferred
    def deferred_default_creator(node, kw):
        return kw.get('email')

    @colander.deferred
    def deferred_default_format(node, kw):
        return kw.get('format', "application/x-netcdf")
        
    identifier = colander.SchemaNode(
        colander.String(),
        default = uuid.uuid4().get_urn())
    title = colander.SchemaNode(colander.String())
    abstract = colander.SchemaNode(
        colander.String(),
        missing = '',
        default = '',
        validator = colander.Length(max=150),
        widget = TextAreaWidget(rows=2, cols=80))
    creator = colander.SchemaNode(
        colander.String(),
        validator = colander.Email(),
        default = deferred_default_creator,)
    source = colander.SchemaNode(
        colander.String(),
        description = 'URL to the source',
        validator = colander.url)
    format = colander.SchemaNode(
        colander.String(),
        default = deferred_default_format,
        description = 'Format of your source. Example: NetCDF',
        )
    subjects = colander.SchemaNode(
        colander.String(),
        default = 'test',
        missing = 'test',
        description = "Keywords: tas, temperature, ...",
        widget = TagsWidget(),
        )
    rights = colander.SchemaNode(
        colander.String(),
        missing = 'Unknown',
        default = 'Free for non-commercial use',
        )

class UserSchema(colander.MappingSchema):
    name = colander.SchemaNode(
        colander.String(),
        title = "Name",
        missing = colander.drop,
        )
    email = colander.SchemaNode(
        colander.String(),
        validator = colander.Email(),
        widget = TextInputWidget(),
        )
    openid = colander.SchemaNode(
        colander.String(),
        title = "OpenID",
        validator = colander.url,
        missing = colander.drop,
        )
    organisation = colander.SchemaNode(
        colander.String(),
        title = "Organisation",
        missing = colander.drop,
        )
    notes = colander.SchemaNode(
        colander.String(),
        title = "Notes",
        missing = colander.drop,
        )


