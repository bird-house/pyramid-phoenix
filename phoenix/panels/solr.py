from pyramid_layout.panel import panel_config
from deform import Form, ValidationFailure

from owslib.fes import PropertyIsEqualTo

from phoenix.models import load_settings, save_settings

import logging
logger = logging.getLogger(__name__)

import colander
import deform
class Schema(colander.MappingSchema):
    maxrecords = colander.SchemaNode(
        colander.Int(),
        missing = -1,
        default = -1,
        validator = colander.Range(-1),
        description = "Maximum number of documents to index. Default: -1 (no limit)")
    depth = colander.SchemaNode(
        colander.Int(),
        missing = 2,
        default = 2,
        validator = colander.Range(1,100),
        description = "Maximum depth level for crawling Thredds catalogs. Default: 2")

    
class SolrPanel(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request


class SolrIndexPanel(SolrPanel):
        
    @panel_config(name='solr_index', renderer='phoenix:templates/panels/solr_index.pt')
    def panel(self):
        csw = self.request.csw
        tasksdb = self.request.db.tasks
        
        query = PropertyIsEqualTo('dc:format', 'THREDDS')
        csw.getrecords2(esn="full", constraints=[query], maxrecords=100)
        items = []
        for rec in csw.records.values():
            item = dict(title=rec.title, status='new', service_id=rec.identifier)
            task = tasksdb.find_one({'url': rec.source})
            if task:
                item['status'] = task['status']
            items.append(item)
        return dict(items=items)


class SolrParamsPanel(SolrPanel):

    def appstruct(self):
        appstruct = {}
        settings = load_settings(self.request)
        appstruct['maxrecords'] = settings.get('solr_maxrecords', '-1')
        appstruct['depth'] = settings.get('solr_depth', '2')
        return appstruct

             
    @panel_config(name='solr_params', renderer='phoenix:templates/panels/form.pt')
    def panel(self):
        form = Form(schema=Schema(), buttons=('update',))
        if 'update' in self.request.POST:
            try:
                controls = self.request.POST.items()
                appstruct = form.validate(controls)
                settings = load_settings(self.request)
                settings['solr_maxrecords'] = appstruct['maxrecords']
                settings['solr_depth'] = appstruct['depth']
                save_settings(self.request, settings)
            except ValidationFailure, e:
                logger.exception('validation of form failed.')
                return dict(title="Parameters", form=e.render())
            except Exception, e:
                logger.exception('update failed.')
                self.request.session.flash('Update of Solr parameters failed. %s' % (e), queue='danger')
            else:
                self.request.session.flash("Solr parameters updated.", queue='success')
        return dict(title="Parameters", form=form.render(self.appstruct()))

