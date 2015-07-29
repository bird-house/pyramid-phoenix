from pyramid_layout.panel import panel_config
from deform import Form, ValidationFailure

from owslib.fes import PropertyIsEqualTo

import logging
logger = logging.getLogger(__name__)

import colander
import deform
class Schema(colander.MappingSchema):
    maxrecords = colander.SchemaNode(
        colander.Integer(),
        default = -1)
    depth = colander.SchemaNode(
        colander.Integer(),
        default = 5)

    
class SolrPanel(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request


class SolrIndexPanel(SolrPanel):
    def __init__(self, context, request):
        super(SolrIndexPanel, self).__init__(context, request)
        self.csw = self.request.csw
        self.tasksdb = self.request.db.tasks

        
    @panel_config(name='solr_index', renderer='phoenix:templates/panels/solr_index.pt')
    def panel(self):
        query = PropertyIsEqualTo('dc:format', 'THREDDS')
        self.csw.getrecords2(esn="full", constraints=[query], maxrecords=100)
        items = []
        for rec in self.csw.records.values():
            item = dict(title=rec.title, status='new', service_id=rec.identifier)
            task = self.tasksdb.find_one({'url': rec.source})
            if task:
                item['status'] = task['status']
            items.append(item)
        return dict(items=items)


class SolrParamsPanel(SolrPanel):

    def appstruct(self):
        appstruct = {}
        return appstruct

    
    def generate_form(self):
        form = Form(schema=Schema(), buttons=('update',))
        return form

    
    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
        except ValidationFailure, e:
            logger.exception('validation of form failed.')
            return dict(form=e.render())
        except Exception, e:
            logger.exception('update failed.')
            self.request.session.flash('Update of Solr parameters failed. %s' % (e), queue='danger')
        else:
            self.request.session.flash("Solr parameters updated.", queue='success')

            
    @panel_config(name='solr_params', renderer='phoenix:templates/panels/form.pt')
    def panel(self):
        form = self.generate_form()
        if 'update' in self.request.POST:
            self.process_form(form)
        return dict(title="Parameters", form=form.render())

