from pyramid.view import view_config

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views.settings import SettingsView
from phoenix.grid import MyGrid

import logging
logger = logging.getLogger(__name__)

class CatalogService(SettingsView):
    def __init__(self, request):
        super(CatalogService, self).__init__(
            request, name='catalog_settings', title='Catalog Service')
        self.csw = self.request.csw
        self.description = "%s (%s)" % (self.csw.identification.title, self.csw.url)
        
    def generate_service_form(self, formid="deform"):
        from phoenix.schema import CatalogAddServiceSchema
        schema = CatalogAddServiceSchema()
        return Form(
            schema,
            buttons=(Button(name='add_service', title='Add Service'),),
            formid=formid)

    def process_service_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            url = appstruct.get('url')
            self.request.csw.harvest(
                source=url,
                resourcetype=appstruct.get('resource_type'))
            self.session.flash('Added WPS %s' % (url), queue="success")
        except ValidationFailure, e:
            logger.exception('validation of catalog form failed')
            return dict(form = e.render())
        except Exception, e:
            logger.exception('could not harvest wps.')
            self.session.flash('Could not add WPS %s. %s' % (url, e), queue="error")
        return HTTPFound(location=self.request.route_url('catalog_settings'))

    def generate_dataset_form(self, formid="deform"):
        from phoenix.schema import PublishSchema
        schema = PublishSchema().bind(email=self.user_email())
        return Form(
            schema,
            buttons=(Button(name='add_dataset', title='Add Dataset'),),
            formid=formid)

    def process_dataset_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)

            from mako.template import Template
            import os
            # TODO: fix location and usage of publish templates
            import phoenix
            templ_dc = Template(filename=os.path.join(os.path.dirname(phoenix.__file__), "templates", "dc.xml"))
            record = templ_dc.render(**appstruct)
            logger.debug('record=%s', record)
            self.csw.transaction(ttype="insert", typename='csw:Record', record=str(record))
            self.session.flash('Added Dataset %s' % (appstruct.get('title')), queue="success")
        except ValidationFailure, e:
            logger.exception('validation of catalog form failed')
            return dict(form = e.render())
        except Exception, e:
            logger.exception('could not harvest wps.')
            self.session.flash('Could not add Dataset %s. %s' % (appstruct.get('source'), e), queue="error")
        return HTTPFound(location=self.request.route_url('catalog_settings'))

    @view_config(route_name='remove_all_records')
    def remove_all(self):
        try:
            self.csw.getrecords(maxrecords=0)
            count = self.csw.results.get('matches'),
            # TODO: self destruction is out of order ... see exception
            self.csw.transaction(ttype='delete', typename='csw:Record')
            self.session.flash("%d Records deleted." % count, queue='info')
        except Exception,e:
            logger.exception('could not remove datasets.')
            self.session.flash('Ooops ... self destruction out of order. %s' % e, queue="error")
        return HTTPFound(location=self.request.route_url('catalog_settings'))
 
    @view_config(route_name='remove_record')
    def remove(self):
        try:
            recordid = self.request.matchdict.get('recordid')
            self.csw.transaction(ttype='delete', typename='csw:Record', identifier=recordid )
            self.session.flash('Removed record %s.' % recordid, queue="info")
        except Exception,e:
            logger.exception("Could not remove record")
            self.session.flash('Could not remove record. %s' % e, queue="error")
        return HTTPFound(location=self.request.route_url('catalog_settings'))

    def get_csw_items(self):
        results = []
        try:
            self.csw.getrecords(esn="full")
            logger.debug('csw results %s', self.csw.results)
            for rec in self.csw.records:
                myrec = self.csw.records[rec]
                results.append(dict(
                    source = myrec.source,
                    identifier = myrec.identifier,
                    title = myrec.title,
                    abstract = myrec.abstract,
                    subjects = myrec.subjects,
                    format = myrec.format,
                    creator = myrec.creator,
                    modified = myrec.modified,
                    bbox = myrec.bbox,
                    references = myrec.references,
                    ))
        except:
            logger.exception('could not get items for csw.')
        return results

    @view_config(route_name="catalog_settings", renderer='phoenix:templates/settings/catalog.pt')
    def view(self):
        service_form = self.generate_service_form()
        dataset_form = self.generate_dataset_form()
        if 'add_service' in self.request.POST:
            return self.process_service_form(service_form)
        elif 'add_dataset' in self.request.POST:
            return self.process_dataset_form(dataset_form)
        items = self.get_csw_items()
            
        grid = CSWGrid(
                self.request,
                items,
                ['title', 'creator', 'modified', 'format', ''],
            )
        self.csw.getrecords(maxrecords=0)
        return dict(
            datasets_found=self.csw.results.get('matches'),
            grid=grid,
            items=items,
            service_form=service_form.render(),
            dataset_form=dataset_form.render())

class CSWGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(CSWGrid, self).__init__(request, *args, **kwargs)
        self.column_formats[''] = self.action_td
        self.column_formats['title'] = self.title_td
        self.column_formats['format'] = self.format_td
        self.column_formats['modified'] = self.modified_td

    def title_td(self, col_num, i, item):
        return self.render_title_td(item['title'], item['abstract'], item.get('subjects'))

    def format_td(self, col_num, i, item):
        return self.render_format_td(item['format'], item['source'])

    def modified_td(self, col_num, i, item):
        return self.render_timestamp_td(timestamp=item.get('modified'))

    def action_td(self, col_num, i, item):
        buttongroup = []
        buttongroup.append(
            ("remove", item.get('identifier'), "icon-trash", "",
            self.request.route_url('remove_record', recordid=item.get('identifier')),
            False) )
        return self.render_action_td(buttongroup)
       
