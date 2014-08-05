from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPFound

from deform import Form
from deform import ValidationFailure

import models

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class Wizard:
    def __init__(self, request):
        self.request = request
        self.session = self.request.session
        self.csw = self.request.csw
        self.catalogdb = models.Catalog(self.request)

    # csw function
    def search_csw(self, query=''):
        keywords = [k for k in map(str.strip, str(query).split(' ')) if len(k)>0]

        results = []
        try:
            self.csw.getrecords(keywords=keywords)
            logger.debug('csw results %s', self.csw.results)
            for rec in self.csw.records:
                myrec = self.csw.records[rec]
                results.append(dict(
                    identifier = myrec.identifier,
                    title = myrec.title,
                    abstract = myrec.abstract,
                    subjects = myrec.subjects,
                    format = myrec.format,
                    creator = myrec.creator,
                    modified = myrec.modified,
                    bbox = myrec.bbox,
                    ))
        except:
            logger.exception('could not get items for csw.')
        return results

    @view_config(renderer='json', name='select.csw')
    def select_csw(self):
        # TODO: refactor this ... not efficient
        identifier = self.request.params.get('identifier', None)
        logger.debug('called with %s', identifier)
        if identifier is not None:
            if 'csw_selection' in self.session:
                if identifier in self.session['selection']:
                    self.session['csw_selection'].remove(identifier)
                else:
                    self.session['csw_selection'].append(identifier)
            else:
                self.session['csw_selection'] = [identifier]
        return {}

    def generate_form(self, formid='deform'):
        from .schema import SelectWPSSchema
        schema = SelectWPSSchema(title="Select WPS").bind(
            wps_list = self.catalogdb.all_as_tuple())
        options = """
        {success:
           function (rText, sText, xhr, form) {
             deform.processCallbacks();
             deform.focusFirstInput();
             var loc = xhr.getResponseHeader('X-Relocate');
                if (loc) {
                  document.location = loc;
                };
             }
        }
        """
        return Form(
            schema,
            buttons=('previous', 'next', 'cancel'),
            formid=formid,
            use_ajax=True,
            ajax_options=options,
            )
    def process_form(self, form):
        controls = self.request.POST.items()
        try:
            captured = form.validate(controls)
            url = captured.get('url', '')
            session = self.request.session
            session['wizard_wps_url'] = url
            session.changed()
        except ValidationFailure, e:
            logger.exception('validation of wps view failed.')
            return dict(title="Select WPS", description="", form=e.render())
        return HTTPFound(location=self.request.route_url('wizard_csw'))

    @view_config(route_name='wizard_wps', renderer='templates/wizard/wps.pt')
    def wps_view(self):
        form = self.generate_form()
        
        if 'previous' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_wps'))
        elif 'next' in self.request.POST:
            return self.process_form(form)
        elif 'cancel' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_wps'))

        return dict(
            title="Select WPS",
            description="",
            form=form.render())

    @view_config(route_name='wizard_csw', renderer='templates/wizard/csw.pt')
    def csw_view(self):
        if 'previous' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_wps'))
        elif 'next' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_csw'))
        elif 'cancel' in self.request.POST:
            return HTTPFound(location=self.request.route_url('wizard_csw'))

        query = self.request.params.get('query', None)
        checkbox = self.request.params.get('checkbox', None)
        logger.debug(checkbox)
        items = self.search_csw(query)
        for item in items:
            
            if 'csw_selection' in self.session and  item['identifier'] in self.session['csw_selection']:
                item['selected'] = True
            else:
                item['selected'] = False

        from .grid import CatalogSearchGrid    
        grid = CatalogSearchGrid(
                self.request,
                items,
                ['title', 'subjects', 'selected'],
            )

        return dict(
            title="Catalog Search", 
            description="Search in Catalog Service",
            grid=grid,
            items=items,
        )
