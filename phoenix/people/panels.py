from pyramid_layout.panel import panel_config
from pyramid.security import authenticated_userid

from deform import Form, ValidationFailure
import colander
import deform

from phoenix.utils import get_user

import logging
logger = logging.getLogger(__name__)


class TwitcherSchema(colander.MappingSchema):
    twitcher_token = colander.SchemaNode(
        colander.String(),
        title="Twitcher access token",
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    twitcher_token_expires = colander.SchemaNode(
        colander.String(),
        title="Expires",
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )


class ESGFCredentialsSchema(colander.MappingSchema):
    openid = colander.SchemaNode(
        colander.String(),
        title="OpenID",
        description="OpenID to access ESGF data",
        validator=colander.url,
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    credentials = colander.SchemaNode(
        colander.String(),
        title="Credentials",
        description="URL to ESGF Proxy Certificate",
        validator=colander.url,
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    cert_expires = colander.SchemaNode(
        colander.String(),
        title="Expires",
        description="When your Proxy Certificate expires",
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )


class SwiftSchema(colander.MappingSchema):
    swift_username = colander.SchemaNode(
        colander.String(),
        title="Swift Username",
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    swift_storage_url = colander.SchemaNode(
        colander.String(),
        title="Swift Storage URL",
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )
    swift_auth_token = colander.SchemaNode(
        colander.String(),
        title="Swift Auth Token",
        missing='',
        widget=deform.widget.TextInputWidget(template='readonly/textinput'),
        )


class ProfilePanel(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def appstruct(self):
        appstruct = get_user(self.request)
        if appstruct is None:
            appstruct = dict()
        return appstruct


class AccountPanel(ProfilePanel):
    def generate_form(self):
        from phoenix.schema import UserProfileSchema
        form = Form(schema=UserProfileSchema(), buttons=('update',), formid='deform')
        return form
    
    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            user = get_user(self.request)
            for key in ['name', 'email', 'organisation', 'notes']:
                user[key] = appstruct.get(key)
            self.request.db.users.update({'identifier':authenticated_userid(self.request)}, user)
        except ValidationFailure, e:
            logger.exception('validation of form failed.')
            return dict(form=e.render())
        except Exception, e:
            logger.exception('update user failed.')
            self.request.session.flash('Update of your account failed. %s' % (e), queue='danger')
        else:
            self.request.session.flash("Your account was updated.", queue='success')

    @panel_config(name='profile_account', renderer='phoenix:templates/panels/form.pt')
    def panel(self):
        form = self.generate_form()
        if 'update' in self.request.POST:
            self.process_form(form)
        return dict(title="Account settings", form=form.render( self.appstruct() ))


class TwitcherPanel(ProfilePanel):
    def generate_form(self):
        form = Form(schema=TwitcherSchema(), formid='deform')
        return form

    @panel_config(name='profile_twitcher', renderer='templates/panels/profile_twitcher.pt')
    def panel(self):
        form = self.generate_form()
        return dict(title="Twitcher access token", form=form.render( self.appstruct() ))


class ESGFPanel(ProfilePanel):
    def generate_form(self):
        form = Form(schema=ESGFCredentialsSchema(), formid='deform')
        return form

    @panel_config(name='profile_esgf', renderer='templates/panels/profile_esgf.pt')
    def panel(self):
        form = self.generate_form()
        return dict(title="ESGF access token", form=form.render( self.appstruct() ))


class SwiftPanel(ProfilePanel):
    def generate_form(self):
        form = Form(schema=SwiftSchema(), formid='deform')
        return form

    @panel_config(name='profile_swift', renderer='phoenix:templates/panels/form.pt')
    def panel(self):
        form = self.generate_form()
        return dict(title="Swift access token", form=form.render( self.appstruct() ))
