from pyramid_layout.panel import panel_config

from deform import Form, ValidationFailure

import logging
logger = logging.getLogger(__name__)


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
        from .schema import AccountSchema
        form = Form(schema=AccountSchema(), buttons=('update',), formid='deform')
        if 'update' in self.request.POST:
            self.process_form(form)
        return dict(title="Account settings", form=form.render(self.appstruct()))


class TwitcherPanel(ProfilePanel):
    @panel_config(name='profile_twitcher', renderer='templates/people/panels/profile_twitcher.pt')
    def panel(self):
        from .schema import TwitcherSchema
        form = Form(schema=TwitcherSchema(), formid='deform')
        return dict(title="Twitcher access token", form=form.render(self.appstruct()))


class ESGFPanel(ProfilePanel):
    @panel_config(name='profile_esgf', renderer='templates/people/panels/profile_esgf.pt')
    def panel(self):
        from .schema import ESGFCredentialsSchema
        form = Form(schema=ESGFCredentialsSchema(), formid='deform')
        return dict(title="ESGF access token", form=form.render(self.appstruct()))

