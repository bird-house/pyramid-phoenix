from datetime import datetime
import uuid

from pyramid.view import view_config, view_defaults, forbidden_view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import remember, forget
from pyramid.compat import escape

from deform import Form, Button, ValidationFailure
from authomatic.adapters import WebObAdapter

from phoenix.security import Admin, User, authomatic
from phoenix.security import check_csrf_token
from phoenix.oauth2 import KeycloakClient


import logging
LOGGER = logging.getLogger("PHOENIX")


@forbidden_view_config(renderer='phoenix:account/templates/account/forbidden.pt')
def forbidden(request):
    request.response.status = 403
    return dict()


@view_defaults(permission='view', layout='default')
class Account(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.collection = request.db.users

    def schema(self):
        raise NotImplementedError("Needs to be implemented in subclass")

    def generate_form(self):
        btn = Button(name='submit', title='Sign In',
                     css_class="btn btn-success btn-lg btn-block")
        form = Form(schema=self.schema(), buttons=(btn,), formid='deform')
        return form

    def process_form(self, form):
        try:
            controls = list(self.request.POST.items())
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            self.session.flash("<strong>Error:</strong> Login failed.", queue='danger')
            return dict(form=e.render())
        else:
            return self._handle_appstruct(appstruct)

    def _handle_appstruct(self, appstruct):
        raise NotImplementedError("Needs to be implemented in subclass")

    def add_user(self, login_id):
        user = dict(
            identifier=str(uuid.uuid1()),
            login_id=login_id,
            email='',
            name=login_id,
            organisation='',
            notes='',
            group=User,
            creation_time=datetime.now(),
            last_login=datetime.now())
        self.collection.save(user)
        return self.collection.find_one({'identifier': user['identifier']})

    def login(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            check_csrf_token(self.request)
            return self.process_form(form)
        return dict(form=form.render())

    def login_success(self, login_id, provider=None, token=None):
        self.session.invalidate()  # clear session
        user = self.collection.find_one(dict(login_id=login_id))
        if user is None:
            LOGGER.warn("new user: {}".format(login_id))
            user = self.add_user(login_id=login_id)
        if provider == 'local':
            user['group'] = Admin
        if provider == 'keycloak':
            user['token'] = token
        user['provider'] = provider
        user['last_login'] = datetime.now()
        self.collection.update({'login_id': login_id}, user)
        self.session.flash("Hello <strong>{0}</strong>. Welcome to CEDA WPS.".format(escape(login_id)), queue='info')
        if provider != 'keycloak':
            # generate_access_token(self.request.registry, userid=user['identifier'])
            pass
        headers = remember(self.request, user['identifier'])
        return HTTPFound(location=self.request.route_path('home'), headers=headers)

    def login_failure(self, message=None):
        if message:
            msg = '<strong>Error:</strong> Sorry, login failed: {0}'.format(escape(message))
        else:
            msg = '<strong>Error:</strong> Sorry, login failed.'
        self.session.flash(msg, queue='danger')
        return HTTPFound(location=self.request.route_path('sign_in'))

    @view_config(route_name='account_logout', permission='edit')
    def logout(self):
        headers = forget(self.request)
        self.session.invalidate()  # deleting the session
        return HTTPFound(location=self.request.route_path('home'), headers=headers)

    @view_config(route_name='account_register', renderer='phoenix:account/templates/account/register.pt')
    def register(self):
        return dict()

    @view_config(route_name='account_auth')
    def authomatic_login(self):
        # LOGGER.debug('authomatic_login')
        _authomatic = authomatic(self.request)
        provider = self.request.matchdict.get('provider')

        # Start the login procedure.
        response = Response()
        result = _authomatic.login(WebObAdapter(self.request, response), provider)

        LOGGER.debug('authomatic result: {}'.format(result))
        # LOGGER.debug('authomatic response: %s', response)

        if result:
            if result.error:
                # Login procedure finished with an error.
                return self.login_failure(message=result.error.message)
            elif result.user:
                if not (result.user.name and result.user.id):
                    result.user.update()
                # Hooray, we have the user!
                LOGGER.debug("login successful for user {}".format(result.user.name))
                if result.provider.name == 'github':
                    return self.login_success(login_id=result.user.username, provider=result.provider.name,)
                elif result.provider.name == 'ceda_oauth':
                    return self.login_success(login_id=result.user.name, provider=result.provider.name,)
                elif result.provider.name == 'keycloak':
                    LOGGER.debug('credentials: {}'.format(result.provider.credentials))
                    client = KeycloakClient(self.request.registry)
                    user_info = client.introspect_access_token(result.provider.credentials.token)
                    return self.login_success(
                        login_id=user_info['preferred_username'],
                        provider=result.provider.name,
                        token={
                            'access_token': result.provider.credentials.token,
                            'refresh_token': result.provider.credentials.refresh_token,
                            'expires_in': result.provider.credentials.expire_in,
                            'expires_at': result.provider.credentials.expiration_time,
                            'token_type': result.provider.credentials.token_type,
                        })
                else:
                    raise Exception('Unknown provider')
        return response
