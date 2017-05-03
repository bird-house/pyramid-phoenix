from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from phoenix.security import passwd_check
from phoenix.account.views import Account
from phoenix.account.schema import PhoenixSchema


class LocalAccount(Account):

    def schema(self):
        return PhoenixSchema()

    def _handle_appstruct(self, appstruct):
        password = appstruct.get('password')
        if passwd_check(self.request, password):
            return self.login_success(login_id="phoenix@localhost", name="Phoenix", local=True)
        return self.login_failure()

    @view_config(route_name='sign_in', renderer='templates/account/sign_in.pt')
    def sign_in(self):
        return self.login()
