from deform import Form
from deform import Button
from deform import ValidationFailure
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.compat import escape

from phoenix.tasks.esgflogon import esgf_logon
from phoenix.tasks.utils import task_result
from phoenix.esgf.schema import ESGFLogonSchema
from phoenix.security import check_csrf_token


import logging
LOGGER = logging.getLogger("PHOENIX")


@view_defaults(permission='edit', layout='default')
class ESGFLogon(object):
    def __init__(self, request):
        self.request = request
        self.session = self.request.session
        if 'callback' in self.request.params:
            self.session['esgflogon_callback'] = self.request.params.get('callback')

    def appstruct(self):
        return {}

    def generate_form(self):
        submit_button = Button(name='submit', title='Submit', css_class='btn btn-success')
        return Form(
            schema=ESGFLogonSchema().bind(request=self.request),
            buttons=(submit_button,), formid="esgflogon")

    def process_form(self, form):
        try:
            controls = list(self.request.POST.items())
            appstruct = form.validate(controls)
            result = esgf_logon.delay(authenticated_userid(self.request),
                                      appstruct.get('provider'),
                                      appstruct.get('username'),
                                      appstruct.get('password'))
            self.session['task_id'] = result.id
        except ValidationFailure as e:
            self.session.flash("Form validation failed.", queue='danger')
            return dict(form=e.render())
        except Exception as e:
            msg = '<strong>Error:</strong> ESGF logon failed: {0}.'.format(escape(e.message))
            self.session.flash(msg, queue='danger')
            return HTTPFound(location=self.request.route_path('esgflogon'))
        else:
            return HTTPFound(location=self.request.route_path('esgflogon_loading'))

    def check_logon(self):
        status = 'running'
        result = task_result(self.session.get('task_id'))
        if result.ready():
            status = 'ready'
        return dict(status=status)

    def loading(self):
        result = task_result(self.session.get('task_id'))
        if result.ready():
            if result.get().get('status') == 'Success':
                self.session.flash('ESGF logon was successful.', queue='success')
                return self.callback()
            else:
                msg = '<strong>Error:</strong> ESGF logon failed: {0}.'.format(
                    escape(result.get().get('message')))
                self.session.flash(msg, queue='danger')
                return HTTPFound(location=self.request.route_path('esgflogon'))
        return {}

    def callback(self):
        callback = self.session.get('esgflogon_callback')
        callback = callback or self.request.route_path('esgflogon')
        if 'esgflogon_callback' in self.session:
            del self.session['esgflogon_callback']
        return HTTPFound(location=callback)

    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            check_csrf_token(self.request)
            return self.process_form(form)
        return dict(
            form=form.render(self.appstruct()))
