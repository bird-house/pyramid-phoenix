import datetime

from pyramid.view import view_config, view_defaults, forbidden_view_config
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.response import Response
from pyramid.renderers import render, render_to_response
from pyramid.security import remember, forget, authenticated_userid
from deform import Form, ValidationFailure

from phoenix.views import MyView
from phoenix.security import Admin, Guest, admin_users, ESGF_Provider, authomatic

import logging
logger = logging.getLogger(__name__)


@forbidden_view_config(renderer='phoenix:templates/account/forbidden.pt', layout="frontpage")
def forbidden(request):
    request.response.status = 403
    return dict()

@view_config(route_name='account_register', renderer='phoenix:templates/account/register.pt',
             permission='view', layout="frontpage")
def register(request):
    return dict()

@view_defaults(permission='view', layout='default')
class Account(MyView):
    def __init__(self, request):
        super(Account, self).__init__(request, name="account", title='Account')

    def appstruct(self, protocol):
        if protocol == 'oauth2':
            return dict(provider='github')
        elif protocol == 'esgf':
            return dict(provider='DKRZ')
        else:
            return dict()

    def generate_form(self, protocol):
        from phoenix.schema import PhoenixSchema, OAuthSchema, OpenIDSchema, ESGFOpenIDSchema, LdapSchema
        schema = None
        if protocol == 'phoenix':
            schema = PhoenixSchema()
        elif protocol == 'esgf':
            schema = ESGFOpenIDSchema()
        elif protocol == 'openid':
            schema = OpenIDSchema()
        elif protocol == 'oauth2':
            schema = OAuthSchema()
        else:
            schema = LdapSchema()
        form = Form(schema=schema, buttons=('submit',), formid='deform')
        return form

    def process_form(self, form, protocol):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
        except ValidationFailure, e:
            logger.exception('validation of form failed.')
            return dict(active=protocol, form=e.render())
        else:
            if protocol == 'phoenix':
                return self.phoenix_login(appstruct)
            elif protocol == 'ldap':
                return self.ldap_login()
            elif protocol == 'oauth2':
                return HTTPFound(location=self.request.route_path('account_auth', provider_name=appstruct.get('provider')))
            else:
                return HTTPFound(location=self.request.route_path('account_auth', provider_name=protocol, _query=appstruct.items()))

    def send_notification(self, email, subject, message):
        """Sends email notification to admins.
        
        Sends email with the pyramid_mailer module.
        For configuration look at documentation http://pythonhosted.org//pyramid_mailer/
        """
        from pyramid_mailer import get_mailer
        mailer = get_mailer(self.request)

        sender = "noreply@%s" % (self.request.server_name)

        from phoenix.security import admin_users
        recipients = admin_users(self.request)
        
        from pyramid_mailer.message import Message
        message = Message(subject=subject,
                          sender=sender,
                          recipients=recipients,
                          body=message)
        try:
            mailer.send_immediately(message, fail_silently=True)
        except:
            logger.exception("failed to send notification")

    def login_success(self, email, openid=None, name="Unknown"):
        from phoenix.models import add_user
        logger.debug('login success: email=%s', email)
        user = self.get_user(email)
        if user is None:
            logger.warn("new user: %s", email)
            user = add_user(self.request, email=email, group=Guest)
            subject = 'New user %s logged in on %s' % (email, self.request.server_name)
            message = 'Please check the activation of the user %s on the Phoenix host %s' % (email, self.request.server_name)
            self.send_notification(email, subject, message)
        if email in admin_users(self.request):
            user['group'] = Admin
        user['last_login'] = datetime.datetime.now()
        if openid is not None:
            user['openid'] = openid
        user['name'] = name
        self.userdb.update({'email':email}, user)
        self.session.flash("Welcome %s (%s)." % (name, email), queue='success')
        if user.get('group') == Guest:
            self.session.flash("You are logged in as guest. You are not allowed to submit any process.", queue='danger')
        headers = remember(self.request, email)
        return HTTPFound(location = self.request.route_path('home'), headers = headers)

    @view_config(route_name='account_login', renderer='phoenix:templates/account/login.pt')
    def login(self):
        protocol = self.request.matchdict.get('protocol', 'esgf')

        if protocol == 'ldap':
            # Ensure that the ldap connector is created
            self.ldap_prepare()

        form = self.generate_form(protocol)
        if 'submit' in self.request.POST:
            return self.process_form(form, protocol)
        # TODO: Add ldap to title?
        return dict(active=protocol, title="Login", form=form.render( self.appstruct(protocol) ))

    @view_config(route_name='account_logout', permission='edit')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(location = self.request.route_path('home'), headers = headers)

    def phoenix_login(self, appstruct):
        return self.login_success(appstruct.get('user'), name="Phoenix")
       

    @view_config(route_name='account_auth')
    def authomatic_login(self):
        from authomatic.adapters import WebObAdapter
        _authomatic = authomatic(self.request)
        
        provider_name = self.request.matchdict.get('provider_name')

        if provider_name == 'esgf':
            username = self.request.params.get('username')
            provider_name = 'openid'
            # esgf openid login with username and provider
            if username is not None:
                provider = self.request.params.get('provider')
                logger.debug('username=%s, provider=%s', username, provider)
                openid = ESGF_Provider.get(provider) % username
                self.request.GET['id'] = openid
                del self.request.GET['username']
                del self.request.GET['provider']
            
        # Start the login procedure.
        response = Response()
        result = _authomatic.login(WebObAdapter(self.request, response), provider_name)

        if result:
            if result.error:
                # Login procedure finished with an error.
                self.session.flash('Sorry, login failed: {0}'.format(result.error.message), queue='danger')
                logger.warn('login failed: %s', result.error.message)
                return HTTPForbidden()
            elif result.user:
                if not (result.user.name and result.user.id):
                    result.user.update()
                # Hooray, we have the user!
                logger.info("login successful for user %s", result.user.name)
                if result.provider.name == 'openid':
                    return self.login_success(email=result.user.email, openid=result.user.id, name=result.user.name)
                elif result.provider.name == 'github':
                    logger.debug('logged in with github')
                    # TODO: dont use email as user id
                    email = "{0.username}@github.com".format(result.user)
                    # get extra info
                    if result.user.credentials:
                        pass
                    return self.login_success(email=email, name=result.user.name)
        return response

    def ldap_prepare(self):
        """Lazy LDAP connector construction"""
        ldap_settings = self.db.ldap.find_one()

        if ldap_settings is None:
            # Warn if LDAP is about to be used but not set up.
            self.session.flash('LDAP does not seem to be set up correctly!', queue = 'danger')
        elif getattr(self.request, 'ldap_connector', None) is None:
            logger.debug('Set up LDAP connector...')

            # Set LDAP settings
            import ldap
            if ldap_settings['scope'] == 'ONELEVEL':
                ldap_scope = ldap.SCOPE_ONELEVEL
            else:
                ldap_scope = ldap.SCOPE_SUBTREE

            # FK: Do we have to think about race conditions here?
            from pyramid.config import Configurator
            config = Configurator(registry = self.request.registry)
            config.ldap_setup(ldap_settings['server'],
                    bind = ldap_settings['bind'],
                    passwd = ldap_settings['passwd'])
            config.ldap_set_login_query(
                    base_dn = ldap_settings['base_dn'],
                    filter_tmpl = ldap_settings['filter_tmpl'],
                    scope = ldap_scope)
            config.commit()

    def ldap_login(self):
        """LDAP login"""
        username = self.request.params.get('username')
        password = self.request.params.get('password')

        # Performing ldap login
        from pyramid_ldap import get_ldap_connector
        connector = get_ldap_connector(self.request)
        auth = connector.authenticate(username, password)

        if auth is not None:
            ldap_settings = self.db.ldap.find_one()
            email = auth[1].get(ldap_settings['email'])[0]

            # Authentication successful
            return self.login_success(email = email)
        else:
            # Authentification failed
            self.session.flash('Sorry, login failed!', queue='danger')
            return HTTPFound(location = self.request.current_route_url())
