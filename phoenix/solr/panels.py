from pyramid_layout.panel import panel_config
from deform import Form, ValidationFailure

from owslib.fes import PropertyIsEqualTo

from phoenix.catalog import THREDDS_TYPE
from phoenix.events import SettingsChanged

import logging
logger = logging.getLogger(__name__)

import colander
import deform


class Schema(colander.MappingSchema):
    maxrecords = colander.SchemaNode(
        colander.Int(),
        name='solr_maxrecords',
        missing=-1,
        default=-1,
        validator=colander.Range(-1),
        description="Maximum number of documents to index. Default: -1 (no limit)")
    depth = colander.SchemaNode(
        colander.Int(),
        name='solr_depth',
        missing=2,
        default=2,
        validator=colander.Range(1, 100),
        description="Maximum depth level for crawling Thredds catalogs. Default: 2")


class SolrPanel(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request


class SolrIndexPanel(SolrPanel):

    @panel_config(name='solr_index', renderer='templates/panels/solr_index.pt')
    def panel(self):
        tasksdb = self.request.db.tasks

        items = []
        for rec in self.request.catalog.get_services(service_type=THREDDS_TYPE):
            item = dict(title=rec.title, status='new', service_id=rec.identifier)
            task = tasksdb.find_one({'url': rec.source})
            if task:
                item['status'] = task['status']
            items.append(item)
        return dict(items=items)


class SolrParamsPanel(SolrPanel):

    def appstruct(self):
        return self.request.db.settings.find_one() or {}

    @panel_config(name='solr_params', renderer='phoenix:templates/panels/form.pt')
    def panel(self):
        form = Form(schema=Schema(), buttons=('update',))
        if 'update' in self.request.POST:
            try:
                controls = self.request.POST.items()
                appstruct = form.validate(controls)
                settings = self.request.db.settings.find_one() or {}
                settings.update(appstruct)
                self.request.db.settings.save(settings)
                self.request.registry.notify(SettingsChanged(self.request, appstruct))
            except ValidationFailure, e:
                logger.exception('validation of form failed.')
                return dict(title="Parameters", form=e.render())
            except Exception, e:
                logger.exception('update failed.')
                self.request.session.flash('Update of Solr parameters failed. %s' % (e), queue='danger')
            else:
                self.request.session.flash("Solr parameters updated.", queue='success')
        return dict(title="Parameters", form=form.render(self.appstruct()))
