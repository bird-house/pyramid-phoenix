import colander
import deform


class PhoenixSchema(colander.MappingSchema):
    password = colander.SchemaNode(
        colander.String(),
        title='Password',
        description='If you have not configured your password yet then it is likely to be "qwerty"',
        validator=colander.Length(min=6),
        widget=deform.widget.PasswordWidget())


class OAuthSchema(colander.MappingSchema):
    choices = [('github', 'GitHub'), ('ceda', 'Ceda')]

    provider = colander.SchemaNode(
        colander.String(),
        validator=colander.OneOf([x[0] for x in choices]),
        widget=deform.widget.RadioChoiceWidget(values=choices, inline=True),
        title='OAuth 2.0 Provider',
        description='Select your OAuth Provider.')


class OpenIDSchema(colander.MappingSchema):
    openid = colander.SchemaNode(
        colander.String(),
        validator=colander.url,
        title="OpenID",
        description="Example: https://esgf-data.dkrz.de/esgf-idp/openid/myname or https://openid.stackexchange.com/",
        default='https://openid.stackexchange.com/')


class ESGFOpenIDSchema(colander.MappingSchema):
    choices = [('badc', 'BADC'), ('dkrz', 'DKRZ'), ('ipsl', 'IPSL'), ('smhi', 'SMHI'), ('pcmdi', 'PCMDI')]

    provider = colander.SchemaNode(
        colander.String(),
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


class LdapSchema(colander.MappingSchema):
    username = colander.SchemaNode(
        colander.String(),
        title="Username",
    )
    password = colander.SchemaNode(
        colander.String(),
        title='Password',
        widget=deform.widget.PasswordWidget())