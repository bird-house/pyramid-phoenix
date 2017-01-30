from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
import colander
import deform

from phoenix.tasks.utils import task_result
from phoenix.tasks.esgflogon import esgf_logon
from phoenix.wizard.views import Wizard

import logging
logger = logging.getLogger(__name__)


class ESGFLoginSchema(colander.MappingSchema):
    openid = colander.SchemaNode(
        colander.String(),
        title="OpenID",
        description="Type your OpenID from your ESGF provider.\
         For example: https://esgf-data.dkrz.de/esgf-idp/openid/username",
        validator=colander.url
    )
    password = colander.SchemaNode(
        colander.String(),
        title='Password',
        description='Type your password for your ESGF OpenID',
        validator=colander.Length(min=6),
        widget=deform.widget.PasswordWidget())


class ESGFLogin(Wizard):
    def __init__(self, request):
        super(ESGFLogin, self).__init__(
            request,
            name='wizard_esgf_login',
            title="ESGF Login")

    def breadcrumbs(self):
        breadcrumbs = super(ESGFLogin, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs

    def schema(self):
        return ESGFLoginSchema()

    def appstruct(self):
        appstruct = super(ESGFLogin, self).appstruct()
        appstruct['openid'] = self.get_user().get('openid')
        return appstruct

    def success(self, appstruct):
        # appstruct['openid'] = self.get_user().get('openid')
        super(ESGFLogin, self).success(appstruct)

        self.wizard_state.set('password', appstruct.get('password'))
        result = esgf_logon.delay(authenticated_userid(self.request), self.request.wps.url,
                                  appstruct.get('openid'),
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
        return super(ESGFLogin, self).view()
