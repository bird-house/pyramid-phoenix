from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from phoenix.account.views import Account
from phoenix.account.schema import ESGFOpenIDSchema


class ESGFAccount(Account):
    def appstruct(self):
        return dict(provider='dkrz')

    def schema(self):
        return ESGFOpenIDSchema()

    def _handle_appstruct(self, appstruct):
        return HTTPFound(location=self.request.route_path('account_auth',
                         provider_name=appstruct.get('provider'),
                         _query=dict(username=appstruct.get('username'))))

    @view_config(route_name='esgf_login', renderer='templates/account/login.pt')
    def esgf_login(self):
        return self.login()
