import datetime

from pyramid.view import view_config, view_defaults, forbidden_view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.renderers import render, render_to_response
from pyramid.security import remember, forget, authenticated_userid
from deform import Form, ValidationFailure
from authomatic import Authomatic
from authomatic.adapters import WebObAdapter

from phoenix.views import MyView
from phoenix.security import Admin, Guest, admin_users, ESGF_Provider

import logging
logger = logging.getLogger(__name__)

from phoenix import config_public as config
authomatic = Authomatic(config=config.config,
                        secret=config.SECRET,
                        report_errors=True,
                        logging_level=logging.DEBUG)

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

    def appstruct(self):
        return dict(provider='DKRZ')

    def generate_form(self, protocol):
        from phoenix.schema import OpenIDSchema, ESGFOpenIDSchema, LdapSchema
        schema = None
        if protocol == 'esgf':
            schema = ESGFOpenIDSchema()
        elif protocol == 'openid':
            schema = OpenIDSchema()
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
            if protocol == 'ldap':
                return self.ldap() # No redirect, just call the ldap login handler
            else:
                logger.debug('openid route = %s', self.request.route_path('account_openid', _query=appstruct.items()))
                return HTTPFound(location=self.request.route_path('account_openid', _query=appstruct.items()))

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
        mailer.send_immediately(message, fail_silently=True)

    def login_success(self, email, openid=None, name="Unknown"):
        from phoenix.models import add_user
        logger.debug('login success: email=%s', email)
        user = self.get_user(email)
        if user is None:
            logger.warn("openid login: new user %s", email)
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

    @view_config(route_name='account_login', renderer='phoenix:templates/account/login.pt')
    def login(self):
        protocol = self.request.matchdict.get('protocol', 'esgf') # FK: What is the second arg for?
        if protocol == 'ldap':
            ldap_settings = self.db.ldap.find_one()
            if ldap_settings is None:
                # Warn if LDAP is about to be used but not set up.
                self.session.flash('LDAP does not seem to be set up correctly!', queue = 'danger')
            elif getattr(self.request, 'ldap_connector', None) is None:
                # Load LDAP settings
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

        form = self.generate_form(protocol)
        if 'submit' in self.request.POST:
            return self.process_form(form, protocol)
        # TODO: Add ldap to title?
        return dict(active=protocol, title="ESGF OpenID", form=form.render( self.appstruct() ))

    @view_config(route_name='account_logout', permission='edit')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(location = self.request.route_path('home'), headers = headers)

    @view_config(route_name='account_openid')
    def openid(self):
        """authomatic openid login"""
        username = self.request.params.get('username')
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
        #response = request.response
        result = authomatic.login(WebObAdapter(self.request, response), "openid")

        #logger.debug('authomatic login result: %s', result)

        # TODO: refactor handling of result and response
        if result:
            if result.error:
                # Login procedure finished with an error.
                self.session.flash('Sorry, login failed: %s' % (result.error.message), queue='danger')
                logger.warn('openid login failed: %s', result.error.message)
                response.text = render('phoenix:templates/account/forbidden.pt', dict(), self.request)
            elif result.user:
                # Hooray, we have the user!
                logger.info("openid login successful for user %s", result.user.email)
                #logger.debug("user=%s, id=%s, email=%s, credentials=%s",
                #          result.user.name, result.user.id, result.user.email, result.user.credentials)
                #logger.debug("provider=%s", result.provider.name )
                #logger.debug("response headers=%s", response.headers.keys())
                #logger.debug("response cookie=%s", response.headers['Set-Cookie'])
                self.login_success(email=result.user.email, openid=result.user.id, name=result.user.name)
                response.text = render('phoenix:templates/account/openid_success.pt', {'result': result}, request=self.request)
                # Add the headers required to remember the user to the response
                response.headers.extend(remember(self.request, result.user.email))

        #logger.debug('response: %s', response)

        return response

    def ldap(self):
        """ldap login"""
        username = self.request.params.get('username')
        password = self.request.params.get('password')

        # Performing ldap login
        from pyramid_ldap import get_ldap_connector
        connector = get_ldap_connector(self.request)
        auth = connector.authenticate(username, password)

        if auth is not None:
            # FK: At the moment, all user identification is build around the
            #     email address as one primary, unique key. While this is fine
            #     with OpenID, it is no longer true when LDAP comes into play.
            #     Maybe we should move away from the email address being a key
            #     identifier, but for now (and for testing) we just assume
            #     there is always an LDAP attribute 'mail' which gives as an
            #     unique identification.
            ldap_settings = self.db.ldap.find_one()
            email = auth[1].get(ldap_settings['email'])[0]

            # Authentication successful
            self.login_success(email = email)

            # TODO: Rename template?
            response = render_to_response('phoenix:templates/account/openid_success.pt',
                    # FK: What is 'result' for? Just an old debug argument?
                    {'result': email}, request = self.request)
            response.headers.extend(remember(self.request, email))
            return response
        else:
            # Authentification failed
            self.session.flash('Sorry, login failed!', queue='danger')
            return HTTPFound(location = self.request.current_route_url())
