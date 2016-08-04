from pyramid_layout.panel import panel_config

from deform import Form, ValidationFailure, Button

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
        btn = Button(name='update', title='Update Profile', css_class="btn btn-success btn-lg btn-block")
        form = Form(schema=AccountSchema(), buttons=(btn,), formid='deform')
        if 'update' in self.request.POST:
            self.process_form(form)
        return dict(title="Account settings", form=form.render(self.appstruct()))


class GroupPanel(ProfilePanel):
    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            user = self.collection.find_one({'identifier': self.userid})
            user['group'] = appstruct.get('group')
            self.collection.update({'identifier': self.userid}, user)
        except ValidationFailure, e:
            logger.debug('validation of form failed.')
            return dict(form=e.render())
        except Exception:
            msg = 'Update of group permission failed.'
            logger.exception(msg)
            self.request.session.flash(msg, queue='danger')
        else:
            self.request.session.flash("Group permission was updated.", queue='success')

    @panel_config(name='profile_group', renderer='phoenix:templates/panels/form.pt')
    def panel(self):
        from .schema import GroupSchema
        btn = Button(name='update_group', title='Update Group Permission', css_class="btn btn-success btn-lg btn-block",
                     disabled=not self.request.has_permission('admin'))
        form = Form(schema=GroupSchema(readonly=not self.request.has_permission('admin')), buttons=(btn,),
                    formid='deform')
        if 'update_group' in self.request.POST:
            self.process_form(form)
        return dict(title="Group permission", form=form.render(self.appstruct()))


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

