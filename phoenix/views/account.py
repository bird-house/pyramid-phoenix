import datetime

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.renderers import render
from pyramid.security import remember, forget, authenticated_userid
from authomatic import Authomatic
from authomatic.adapters import WebObAdapter

from phoenix.views import MyView
from phoenix.security import Admin, Guest, admin_users

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
class Account(MyView):
    def __init__(self, request):
        super(Account, self).__init__(request, name="account", title='Account')

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

    def login_success(self, email, openid=None, name="Unknown"):
        from phoenix.models import add_user
        logger.debug('login success: email=%s', email)
        user = self.get_user(email)
        if user is None:
            logger.warn("openid login: new user %s", result.user.email)
            user = add_user(self.request, email=email, group=Guest)
        if email in admin_users(self.request):
            user['group'] = Admin
        user['last_login'] = datetime.datetime.now()
        if openid is not None:
            user['openid'] = openid
        user['name'] = name
        self.userdb.update({'email':email}, user)
        self.session.flash("Welcome %s (%s)." % (name, email), queue='info')

    @view_config(route_name='account_login', renderer='phoenix:templates/account/login.pt')
    def login(self):
        protocol = self.request.matchdict.get('protocol', 'esgf')
        lm = self.request.layout_manager
        if protocol == 'esgf':
            lm.layout.add_heading('logon_esgf')
        elif protocol == 'openid':
            lm.layout.add_heading('logon_openid')
        return dict(active=protocol)

    @view_config(route_name='logout', permission='edit')
    def logout(self):
        headers = forget(self.request)
        return HTTPFound(location = self.request.route_path('home'), headers = headers)

    @view_config(route_name='register', renderer='phoenix:templates/register.pt')
    def register(self):
        return dict(email=None)

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
                logger.info("openid login successful for user %s", result.user.email)
                logger.debug("user=%s, id=%s, email=%s, credentials=%s",
                          result.user.name, result.user.id, result.user.email, result.user.credentials)
                logger.debug("provider=%s", result.provider.name )
                logger.debug("response headers=%s", response.headers.keys())
                #logger.debug("response cookie=%s", response.headers['Set-Cookie'])
                self.login_success(email=result.user.email, openid=result.user.id, name=result.user.name)
                response.text = render('phoenix:templates/openid_success.pt', {'result': result}, request=self.request)
                # Add the headers required to remember the user to the response
                response.headers.extend(remember(self.request, result.user.email))

        #logger.debug('response: %s', response)

        return response

    

