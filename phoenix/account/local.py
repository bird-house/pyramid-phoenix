import colander
import deform

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from phoenix.security import passwd_check
from phoenix.account.base import Account


class LocalSchema(deform.schema.CSRFSchema):
    password = colander.SchemaNode(
        colander.String(),
        title='password',
        validator=colander.Length(min=6),
        widget=deform.widget.PasswordWidget())


class LocalAccount(Account):
    def schema(self):
        return deform.schema.CSRFSchema()

    @view_config(route_name='sign_in', renderer='phoenix:account/templates/account/sign_in.pt')
    def sign_in(self):
        return self.login()


class AdminAccount(Account):

    def schema(self):
        return LocalSchema().bind(request=self.request)

    def _handle_appstruct(self, appstruct):
        password = appstruct.get('password')
        if passwd_check(self.request, password):
            return self.login_success(login_id="admin", provider='local')
        return self.login_failure()

    @view_config(route_name='sign_in_admin', renderer='phoenix:account/templates/account/sign_in_admin.pt')
    def sign_in(self):
        return self.login()
