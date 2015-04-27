from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default') 
class MyAccount(MyView):
    def __init__(self, request):
        super(MyAccount, self).__init__(request, name='myaccount', title='My Account')
        self.description = "Update your profile details."

    def generate_form(self, formid="deform"):
        from phoenix.schema import MyAccountSchema
        schema = MyAccountSchema().bind()
        return Form(
            schema=schema,
            buttons=('submit',),
            formid=formid)

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            user = self.get_user()
            for key in ['name', 'openid', 'organisation', 'notes']:
                user[key] = appstruct.get(key)
            self.userdb.update({'email':self.user_email()}, user)
        except ValidationFailure, e:
            logger.exception('validation of form failed.')
            return dict(form=e.render())
        except Exception, e:
            logger.exception('update user failed.')
            self.session.flash('Update of your accound failed. %s' % (e), queue='error')
        else:
            self.session.flash("Your account was updated.", queue='success')
        return HTTPFound(location=self.request.route_url('myaccount'))
        
    def generate_creds_form(self, formid="deform"):
        from phoenix.schema import CredentialsSchema
        schema = CredentialsSchema().bind()
        return Form(
            schema,
            buttons=('update',),
            formid=formid)

    def process_creds_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)

            user = self.get_user()
            from phoenix.models import esgf
            result = esgf.myproxy_logon(
                self.request,
                openid = user.get('openid'),
                password = appstruct.get('password'))
            
            user['credentials'] = result['credentials']
            user['cert_expires'] = result['cert_expires'] 
            self.userdb.update({'email':self.user_email()}, user)
        except ValidationFailure, e:
            logger.exception('Validation of credentials form failed.')
            return dict(form=e.render())
        except Exception, e:
            logger.exception("update credentials failed.")
            self.request.session.flash(
                "Could not update your credentials. %s" % (e), queue='error')
        else:
            self.request.session.flash(
                'Credentials updated.',
                queue='success')
        return HTTPFound(location=self.request.route_url('myaccount'))

    def generate_swift_form(self, formid="deform"):
        from phoenix.schema import SwiftLoginSchema
        schema = SwiftLoginSchema().bind()
        return Form(
            schema,
            buttons=('update_token',),
            formid=formid)

    def process_swift_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)

            user = self.get_user()
            from phoenix.models import swift
            result = swift.swift_login(
                self.request,
                username = appstruct.get('username'),
                password = appstruct.get('password'))

            user['swift_username'] = appstruct.get('username')
            user['swift_storage_url'] = result['storage_url']
            user['swift_auth_token'] = result['auth_token'] 
            self.userdb.update({'email':self.user_email()}, user)
        except ValidationFailure, e:
            logger.exception('Validation of swift form failed.')
            return dict(form=e.render())
        except Exception, e:
            logger.exception("update swift token failed.")
            self.request.session.flash(
                "Could not update your swift token. %s" % (e), queue='error')
        else:
            self.request.session.flash(
                'Swift token updated.',
                queue='success')
        return HTTPFound(location=self.request.route_url('myaccount'))

    def appstruct(self):
        appstruct = self.get_user()
        if appstruct is None:
            appstruct = {}
        return appstruct
        
    @view_config(route_name='myaccount', renderer='phoenix:templates/myaccount.pt')
    def view(self):
        form = self.generate_form()
        creds_form = self.generate_creds_form()
        swift_form = self.generate_swift_form()

        if 'update' in self.request.POST:
            return self.process_creds_form(creds_form)
        if 'update_token' in self.request.POST:
            return self.process_swift_form(swift_form)
        if 'submit' in self.request.POST:
            return self.process_form(form)
        return dict(
            form=form.render(self.appstruct()),
            form_credentials=creds_form.render(self.appstruct()),
            form_swift=swift_form.render(self.appstruct()))
