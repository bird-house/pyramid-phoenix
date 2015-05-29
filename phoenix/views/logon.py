import datetime

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.renderers import render
from pyramid.security import remember, forget, authenticated_userid
from authomatic import Authomatic
from authomatic.adapters import WebObAdapter

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)

from phoenix import config_public as config
authomatic = Authomatic(config=config.config,
                        secret=config.SECRET,
                        report_errors=True,
                        logging_level=logging.DEBUG)

# TODO: make this configurable
PROVIDER_URLS = dict(
    badc='https://ceda.ac.uk/openid/%s',
    bnu='https://esg.bnu.edu.cn/esgf-idp/openid/%s',
    dkrz='https://esgf-data.dkrz.de/esgf-idp/openid/%s',
    ipsl='https://esgf-node.ipsl.fr/esgf-idp/openid/%s',
    nci='https://esg2.nci.org.au/esgf-idp/openid/%s',
    pcmdi='https://pcmdi9.llnl.gov/esgf-idp/openid/%s',
    smhi='https://esg-dn1.nsc.liu.se/esgf-idp/openid/%s',
)

@view_defaults(permission='view', layout='default')
class Logon(MyView):
    def __init__(self, request):
        super(Logon, self).__init__(request, name="login_openid", title='Logon')

    # FK: What is this function for?
    def is_valid_user(self, email):
        from phoenix.security import admin_users
        if email in admin_users(self.request):
            return True
        user = self.get_user(email=email)
        if user is None:
            return False
        return user.get('activated', False)

    def notify_login_failure(self, user_email):
        """Notifies about user login failure via email.
        
        Sends email with the pyramid_mailer module.
        For configuration look at documentation http://pythonhosted.org//pyramid_mailer/
        """
        logger.debug("notify login failure for %s", user_email)
        
        from pyramid_mailer import get_mailer
        mailer = get_mailer(self.request)

        sender = "noreply@%s" % (self.request.server_name)
        subject = "User %s failed to login on %s" % (user_email, self.request.server_name)
        body = """User %s is not registered at Phoenix server on %s:%s.
        """ % (user_email, self.request.server_name, self.request.server_port)

        from phoenix.security import admin_users
        recipients = admin_users(self.request)
        
        from pyramid_mailer.message import Message
        message = Message(subject=subject,
                          sender=sender,
                          recipients=recipients,
                          body=body)
        #mailer.send(message)
        mailer.send_immediately(message, fail_silently=True)

    def login_success(self, email, openid=None, name="Unknown", activated=False):
        from phoenix.models import add_user
        logger.debug('login success: email=%s', email)
        user = self.get_user(email)
        if user is None:
            user = add_user(self.request, email=email)
        user['last_login'] = datetime.datetime.now()
        if openid is not None:
            user['openid'] = openid
        user['activated'] = activated
        user['name'] = name
        logger.debug('user=%s', user)
        self.userdb.update({'email':email}, user)
        self.session.flash("Welcome %s (%s)." % (name, email), queue='info')

    @view_config(route_name='dummy', renderer='phoenix:templates/dummy.pt')
    @view_config(route_name='dummy_json', renderer='json')
    def dummy(self):
        email = self.request.matchdict['email']
        now = datetime.datetime.now()
        return dict(name="dummy", email=email, now=now)

    @view_config(route_name='signin', renderer='phoenix:templates/signin.pt')
    def signin(self):
        tab = self.request.matchdict.get('tab', 'esgf')
        lm = self.request.layout_manager
        if tab == 'esgf':
            lm.layout.add_heading('logon_esgf')
        elif tab == 'openid':
            lm.layout.add_heading('logon_openid')
        elif tab == 'ldap':
            lm.layout.add_heading('logon_ldap')
        return dict(active=tab)

    @view_config(route_name='logout', permission='edit')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(location = self.request.route_url('home'), headers = headers)

    @view_config(route_name='register', renderer='phoenix:templates/register.pt')
    def register(self):
        return dict(email=None)

    @view_config(route_name='login_local')
    def login_local(self):
        """local login for admin and demo user"""
        
        # TODO: need some work on local accounts
        if (True):
            email = "admin@malleefowl.org"
            if self.is_valid_user(email):
                self.request.response.text = render('phoenix:templates/login_success.pt',
                                               {'result': email},
                                               request=self.request)
                # Add the headers required to remember the user to the response
                self.request.response.headers.extend(remember(self.request, email))
                self.login_success(email=email)
            else:
                self.request.response.text = render('phoenix:templates/register.pt',
                                               {'email': email}, request=self.request)
        else:
            self.request.response.text = render('phoenix:templates/forbidden.pt',
                                           {'message': 'Wrong Password'},
                                           request=self.request)

        return self.request.response

    @view_config(route_name='login_openid')
    def login_openid(self):
        """authomatic openid login"""
        username = self.request.params.get('username')
        # esgf openid login with username and provider
        if username is not None:
            provider = self.request.params.get('provider')
            logger.debug('username=%s, provider=%s', username, provider)
            openid = PROVIDER_URLS.get(provider) % username
            self.request.GET['id'] = openid
            del self.request.GET['username']
            del self.request.GET['provider']
            
        # Start the login procedure.
        response = Response()
        #response = request.response
        result = authomatic.login(WebObAdapter(self.request, response), "openid")

        logger.debug('authomatic login result: %s', result)

        if result:
            if result.error:
                # Login procedure finished with an error.
                #request.session.flash('Sorry, login failed: %s' % (result.error.message))
                logger.error('openid login failed: %s', result.error.message)
                #response.write(u'<h2>Login failed: {}</h2>'.format(result.error.message))
                response.text = render('phoenix:templates/forbidden.pt',
                                       {'message': result.error.message}, request=self.request)
            elif result.user:
                # Hooray, we have the user!
                logger.debug("user=%s, id=%s, email=%s, credentials=%s",
                          result.user.name, result.user.id, result.user.email, result.user.credentials)
                logger.debug("provider=%s", result.provider.name )
                logger.debug("response headers=%s", response.headers.keys())
                #logger.debug("response cookie=%s", response.headers['Set-Cookie'])

                if self.is_valid_user(result.user.email):
                    logger.info("openid login successful for user %s", result.user.email)
                    self.login_success(
                        email=result.user.email,
                        openid=result.user.id,
                        name=result.user.name,
                        activated=True)
                    response.text = render('phoenix:templates/login_success.pt',
                                           {'result': result},
                                           request=self.request)
                    # Add the headers required to remember the user to the response
                    response.headers.extend(remember(self.request, result.user.email))
                else:
                    logger.info("openid login: user %s is not registered", result.user.email)
                    self.notify_login_failure(result.user.email)
                    self.login_success(
                        email=result.user.email,
                        openid=result.user.id,
                        name=result.user.name,
                        activated=False)
                    response.text = render('phoenix:templates/register.pt',
                                           {'email': result.user.email}, request=self.request)

        #logger.debug('response: %s', response)

        return response

    @view_config(route_name='login_ldap')
    def login_ldap(self):
        """ldap login"""
        # FK: Why not use 'deform' and it's features to check the fields?
        username = self.request.params.get('username')
        password = self.request.params.get('password')

        # FK: Why is everything logged twice?
        logger.debug('ldap login, username: %s, password: %s', username, '*' * len(password))

        # Performing ldap login
        from pyramid_ldap import get_ldap_connector
        connector = get_ldap_connector(self.request)
        auth = connector.authenticate(username, password)
        logger.debug('ldap auth, %s', auth)

        response = Response()
        if auth is not None:
            # Authentication successful
            userdn = auth[0]
            response.text = render('phoenix:templates/login_success.pt',
                    # FK: What is 'result' for? Just an old debug argument?
                    {'result': username}, request = self.request)
            response.headers.extend(remember(self.request, userdn))
        else:
            # Authentification failed
            response.text = render('phoenix:templates/forbidden.pt',
                    {'message': 'Invalid credentials'}, request = self.request)

        return response
