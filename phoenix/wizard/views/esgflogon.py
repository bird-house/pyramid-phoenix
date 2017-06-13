from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
import colander
import deform

from phoenix.esgf.schema import ESGFLogonSchema
from phoenix.tasks.utils import task_result
from phoenix.tasks.esgflogon import esgf_logon
from phoenix.wizard.views import Wizard

import logging
LOGGER = logging.getLogger("PHOENIX")


class ESGFLogon(Wizard):
    def __init__(self, request):
        super(ESGFLogon, self).__init__(
            request,
            name='wizard_esgf_logon',
            title="ESGF Logon")

    def breadcrumbs(self):
        breadcrumbs = super(ESGFLogon, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return ESGFLogonSchema()

    def success(self, appstruct):
        super(ESGFLogon, self).success(appstruct)

        self.wizard_state.set('password', appstruct.get('password'))
        result = esgf_logon.delay(authenticated_userid(self.request),
                                  appstruct.get('provider'),
                                  appstruct.get('username'),
                                  appstruct.get('password'))
        self.session['task_id'] = result.id

    def next_success(self, appstruct):
        self.success(appstruct)
        return HTTPFound(location=self.request.route_path('wizard_loading'))

    def check_logon(self):
        status = 'running'
        result = task_result(self.session.get('task_id'))
        if result.ready():
            status = 'ready'
        return dict(status=status)

    def loading(self):
        result = task_result(self.session.get('task_id'))
        if result.ready():
            if result.get().get('status') == 'Success':
                self.session.flash('ESGF logon was successful.', queue='success')
                return self.next('wizard_done')
            else:
                self.session.flash('ESGF logon failed: {}.'.format(result.get().get('message')), queue='danger')
                return HTTPFound(location=self.request.route_path(self.name))
        return {}

    def view(self):
        return super(ESGFLogon, self).view()
