from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from deform import Form
from deform import ValidationFailure

from phoenix.settings.views import SettingsView

import logging
logger = logging.getLogger(__name__)

class GitHub(SettingsView):
    def __init__(self, request):
        super(GitHub, self).__init__(request, name='settings_github', title='GitHub')
        self.settings = self.db.settings.find_one()
        if self.settings is None:
            self.settings = {}

    def breadcrumbs(self):
        breadcrumbs = super(GitHub, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def generate_form(self):
        from phoenix.settings.schema import GitHubSchema
        return Form(schema=GitHubSchema(), buttons=('submit',), formid='deform')

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
        except ValidationFailure, e:
            logger.exception('validation of GitHub form failed')
            return dict(title=self.title, form = e.render())
        except Exception, e:
            msg = 'saving of GitHub settings failed'
            logger.exception(msg)
            self.session.flash(msg, queue="danger")
        else:
            self.settings['github'] = {}
            self.settings['github']['consumer_key'] = appstruct.get('consumer_key')
            self.settings['github']['consumer_secret'] = appstruct.get('consumer_secret')
            self.db.settings.save(self.settings)

            # TODO: use events, config, settings, ... to update auth
            self.session.flash('Successfully updated GitHub settings!', queue='success')
        return HTTPFound(location=self.request.route_path('settings_github'))

    def appstruct(self):
        return self.settings.get('github', {})

    @view_config(route_name='settings_github', renderer='../templates/settings/default.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)
        return dict(title=self.title, form=form.render(self.appstruct()))


