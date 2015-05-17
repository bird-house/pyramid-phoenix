from pyramid.view import view_config
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views.settings import SettingsView

import logging
logger = logging.getLogger(__name__)

class AddDataset(SettingsView):
    def __init__(self, request):
        super(AddDataset, self).__init__(
            request, name='settings_add_dataset', title='Add Dataset')
        self.csw = self.request.csw
        self.description = 'Add dataset to catalog.'

    def breadcrumbs(self):
        breadcrumbs = super(AddDataset, self).breadcrumbs()
        # TODO: fix breadcrumb
        breadcrumbs.append(dict(route_path=self.request.route_path('settings_catalog'), title="Catalog"))
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs
        
    def generate_form(self):
        from phoenix.schema import PublishSchema
        schema = PublishSchema().bind(email=authenticated_userid(self.request))
        return Form(schema, buttons=(Button(name='add_dataset', title='Add Dataset'),), formid='deform')

    def process_form(self, form):
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
            return dict(title=self.title, form = e.render())
        except Exception, e:
            logger.exception('could not harvest wps.')
            self.session.flash('Could not add Dataset %s. %s' % (appstruct.get('source'), e), queue="danger")
        return HTTPFound(location=self.request.route_path('settings_catalog'))

    @view_config(route_name="settings_add_dataset", renderer='phoenix:templates/settings/add_dataset.pt')
    def view(self):
        form = self.generate_form()
        if 'add_dataset' in self.request.POST:
            return self.process_form(form)
        return dict(title=self.title, form=form.render())

       
