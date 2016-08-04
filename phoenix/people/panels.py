from pyramid_layout.panel import panel_config

from deform import Form, ValidationFailure
import colander
import deform

import logging
logger = logging.getLogger(__name__)


class AccountSchema(colander.MappingSchema):
    name = colander.SchemaNode(
        colander.String(),
        title="Your Name",
        missing='',
        default='',
        )
    email = colander.SchemaNode(
        colander.String(),
        title="EMail",
        validator=colander.Email(),
        missing=colander.drop,
        widget=deform.widget.TextInputWidget(),
        )
    organisation = colander.SchemaNode(
        colander.String(),
        title="Organisation",
        missing='',
        default='',
        )
    notes = colander.SchemaNode(
        colander.String(),
        title="Notes",
        missing='',
        default='',
        )


# class EditUserSchema(UserProfileSchema):
#     choices = ((Admin, 'Admin'), (User, 'User'), (Guest, 'Guest'))
#
#     group = colander.SchemaNode(
#         colander.String(),
#         validator=colander.OneOf([x[0] for x in choices]),
#         widget=deform.widget.RadioChoiceWidget(values=choices, inline=True),
#         title='Group',
#         description='Select Group')


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


class ProfilePanel(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.userid = request.matchdict.get('userid')
        self.collection = self.request.db.users

    def appstruct(self):
        appstruct = self.collection.find_one({'identifier': self.userid})
        if appstruct is None:
            appstruct = dict()
        return appstruct


class AccountPanel(ProfilePanel):
    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            user = self.collection.find_one({'identifier': self.userid})
            for key in ['name', 'email', 'organisation', 'notes']:
                user[key] = appstruct.get(key)
            self.collection.update({'identifier': self.userid}, user)
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
        form = Form(schema=AccountSchema(), buttons=('update',), formid='deform')
        if 'update' in self.request.POST:
            self.process_form(form)
        return dict(title="Account settings", form=form.render(self.appstruct()))


class TwitcherPanel(ProfilePanel):
    @panel_config(name='profile_twitcher', renderer='templates/people/panels/profile_twitcher.pt')
    def panel(self):
        form = Form(schema=TwitcherSchema(), formid='deform')
        return dict(title="Twitcher access token", form=form.render(self.appstruct()))


class ESGFPanel(ProfilePanel):
    @panel_config(name='profile_esgf', renderer='templates/people/panels/profile_esgf.pt')
    def panel(self):
        form = Form(schema=ESGFCredentialsSchema(), formid='deform')
        return dict(title="ESGF access token", form=form.render(self.appstruct()))

