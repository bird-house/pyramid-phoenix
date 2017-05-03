import colander
import deform

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from phoenix.security import passwd_check
from phoenix.account.base import Account


class LocalSchema(colander.MappingSchema):
    password = colander.SchemaNode(
        colander.String(),
        title='Password',
        description='If you have not configured your password yet then it is likely to be "qwerty"',
        validator=colander.Length(min=6),
        widget=deform.widget.PasswordWidget())


class LocalAccount(Account):

    def schema(self):
        return LocalSchema()

    def _handle_appstruct(self, appstruct):
        password = appstruct.get('password')
        if passwd_check(self.request, password):
            return self.login_success(login_id="phoenix@localhost", name="Phoenix", local=True)
        return self.login_failure()

    @view_config(route_name='sign_in', renderer='templates/account/sign_in.pt')
    def sign_in(self):
        return self.login()
