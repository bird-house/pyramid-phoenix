from pyramid_layout.panel import panel_config
from deform import Form, ValidationFailure

from owslib.fes import PropertyIsEqualTo

from phoenix.catalog import THREDDS_TYPE
from phoenix.events import SettingsChanged
from phoenix.utils import skip_csrf_token

import logging
LOGGER = logging.getLogger("PHOENIX")

import colander
import deform


class Schema(deform.schema.CSRFSchema):
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
        appstruct = self.request.db.settings.find_one() or {}
        return skip_csrf_token(appstruct)

    @panel_config(name='solr_params', renderer='phoenix:templates/panels/form.pt')
    def panel(self):
        form = Form(schema=Schema().bind(request=self.request), buttons=('update',))
        if 'update' in self.request.POST:
            try:
                controls = self.request.POST.items()
                appstruct = form.validate(controls)
                settings = self.request.db.settings.find_one() or {}
                settings.update(skip_csrf_token(appstruct))
                self.request.db.settings.save(settings)
                self.request.registry.notify(SettingsChanged(self.request, appstruct))
            except ValidationFailure, e:
                LOGGER.exception('validation of form failed.')
                return dict(title="Parameters", form=e.render())
            except Exception, e:
                LOGGER.exception('update failed.')
                self.request.session.flash('Update of Solr parameters failed.', queue='danger')
            else:
                self.request.session.flash("Solr parameters updated.", queue='success')
        return dict(title="Parameters", form=form.render(self.appstruct()))
