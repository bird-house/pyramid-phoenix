from datetime import datetime
import uuid

from pyramid.view import view_config, view_defaults, forbidden_view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.security import remember, forget
from pyramid.compat import escape

from deform import Form, Button, ValidationFailure
from authomatic.adapters import WebObAdapter

from phoenix.security import Admin, Guest, authomatic
from phoenix.security import check_csrf_token
from phoenix.twitcherclient import generate_access_token


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

    def send_notification(self, email, subject, message):
        """Sends email notification to admins.

        Sends email with the pyramid_mailer module.
        For configuration look at documentation http://pythonhosted.org//pyramid_mailer/
        """
        from pyramid_mailer import get_mailer
        mailer = get_mailer(self.request)

        sender = "noreply@%s" % (self.request.server_name)

        recipients = set()
        for user in self.collection.find({'group': Admin}):
            email = user.get('email')
            if email:
                recipients.add(email)

        if len(recipients) > 0:
            from pyramid_mailer.message import Message
            message = Message(subject=subject,
                              sender=sender,
                              recipients=recipients,
                              body=message)
            try:
                mailer.send_immediately(message, fail_silently=True)
            except Exception:
                LOGGER.error("failed to send notification")
        else:
            LOGGER.warn("Can't send notification. No admin emails are available.")

    def add_user(self, login_id, email=None):
        user = dict(
            identifier=str(uuid.uuid1()),
            login_id=login_id,
            email=email or '',
            openid='',
            name='Guest',
            organisation='',
            notes='',
            group=Guest,
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

    def login_success(self, login_id, email=None, name=None, openid=None, local=False):
        self.session.invalidate()  # clear session
        user = self.collection.find_one(dict(login_id=login_id))
        if user is None:
            LOGGER.warn("new user: %s", login_id)
            user = self.add_user(login_id=login_id, email=email)
            subject = 'Phoenix: New user {} logged in on {}'.format(user['name'], self.request.server_name)
            message = 'Please check the activation of the user {} on the Phoenix host {}.'.format(
                user['name'], self.request.server_name)
            self.send_notification(email, subject, message)
        if local:
            user['group'] = Admin
        user['last_login'] = datetime.now()
        user['openid'] = openid or ''
        user['name'] = name or 'Guest'
        self.collection.update({'login_id': login_id}, user)
        self.session.flash("Hello <strong>{0}</strong>. Welcome to Phoenix.".format(escape(name)), queue='info')
        if user.get('group') == Guest:
            msg = """
            <strong>Warning:</strong> You are a member of the <strong>Guest</strong> group.
            You are only allowed to submit processes <strong>without access restrictions</strong>.
            """
            self.session.flash(msg, queue='warning')
        else:
            generate_access_token(self.request.registry, userid=user['identifier'])
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

        # LOGGER.debug('authomatic result: %s', result)
        # LOGGER.debug('authomatic response: %s', response)

        if result:
            if result.error:
                # Login procedure finished with an error.
                return self.login_failure(message=result.error.message)
            elif result.user:
                if not (result.user.name and result.user.id):
                    result.user.update()
                # Hooray, we have the user!
                LOGGER.info("login successful for user %s", result.user.name)
                if result.provider.name == 'github':
                    # TODO: fix email ... get more infos ... which login_id?
                    login_id = "{0.username}@github.com".format(result.user)
                    return self.login_success(login_id=login_id, name=result.user.name)
                if result.provider.name == 'ceda_oauth':
                    return self.login_success(login_id=result.user.name, name=result.user.name)
                else:
                    # TODO: change login_id ... more infos ...
                    return self.login_success(login_id=result.user.id,
                                              email=result.user.email or '',
                                              openid=result.user.id,
                                              name=result.user.name or 'Unknown')
        return response
