import colander
import deform

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from phoenix.account.base import Account


class ESGFSchema(deform.schema.CSRFSchema):
    choices = [('ceda', 'CEDA'), ('dkrz', 'DKRZ'), ('ipsl', 'IPSL'), ('smhi', 'SMHI'), ('pcmdi', 'PCMDI')]

    provider = colander.SchemaNode(
        colander.String(),
        default='dkrz',
        validator=colander.OneOf([x[0] for x in choices]),
        widget=deform.widget.RadioChoiceWidget(values=choices, inline=True),
        title='ESGF Provider',
        description='Select the Provider of your ESGF OpenID.')
    username = colander.SchemaNode(
        colander.String(),
        validator=colander.Length(min=2),
        title="Username",
        description="Your ESGF OpenID Username."
    )


class ESGFAccount(Account):
    def schema(self):
        return ESGFSchema().bind(request=self.request)

    def _handle_appstruct(self, appstruct):
        return HTTPFound(location=self.request.route_path('account_auth',
                         provider=appstruct.get('provider'),
                         _query=dict(username=appstruct.get('username'))))

    @view_config(route_name='esgf_login', renderer='phoenix:account/templates/account/login.pt')
    def esgf_login(self):
        return self.login()
