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

@view_defaults(permission='view', layout='default')
class Logon(MyView):
    def __init__(self, request):
        super(Logon, self).__init__(request, 'Logon')

    def is_valid_user(self, email):
        from phoenix.security import admin_users
        if email in admin_users(self.request):
            return True
        user = self.get_user(email=email)
        if user is None:
            return False
        return user.get('activated', False)

    def login_success(self, email, openid=None, activated=False):
        logger.debug('login success: email=%s', email)
        user = self.get_user(email)
        if user is None:
            user = models.add_user(self.request, email=email)
        user['last_login'] = datetime.datetime.now()
        if openid is not None:
            user['openid'] = openid
        user['activated'] = activated
        logger.debug('user=%s', user)
        self.userdb.update({'email':email}, user)

    @view_config(route_name='dummy', renderer='phoenix:templates/dummy.pt')
    @view_config(route_name='dummy_json', renderer='json')
    def dummy(self):
        email = self.request.matchdict['email']
        now = datetime.datetime.now()
        return dict(name="dummy", email=email, now=now)

    @view_config(route_name='signin', renderer='phoenix:templates/signin.pt')
    def signin(self):
        return dict()

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
        
        # TODO: need some work work on local accounts
        if (True):
            email = "admin@malleefowl.org"
            if self.is_valid_user(email):
                self.request.response.text = render('phoenix:templates/openid_success.pt',
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
        # Get the internal provider name URL variable.
        provider_name = self.request.matchdict.get('provider_name', 'openid')

        logger.debug('provider_name: %s', provider_name)

        # Start the login procedure.
        response = Response()
        #response = request.response
        result = authomatic.login(WebObAdapter(self.request, response), provider_name)

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
                        activated=True)
                    response.text = render('phoenix:templates/openid_success.pt',
                                           {'result': result},
                                           request=self.request)
                    # Add the headers required to remember the user to the response
                    response.headers.extend(remember(self.request, result.user.email))
                else:
                    logger.info("openid login: user %s is not registered", result.user.email)
                    self.login_success(
                        email=result.user.email,
                        openid=result.user.id,
                        activated=False)
                    response.text = render('phoenix:templates/register.pt',
                                           {'email': result.user.email}, request=self.request)
        #logger.debug('response: %s', response)

        return response

    

