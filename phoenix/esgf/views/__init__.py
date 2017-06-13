from deform import Form
from deform import Button
from deform import ValidationFailure
from pyramid.view import view_defaults
from pyramid.httpexceptions import HTTPFound

from phoenix.esgf.schema import ESGFLogonSchema
from phoenix.esgf.schema import ESGFSearchSchema
from phoenix.esgf.search import ESGFSearch

import logging
LOGGER = logging.getLogger("PHOENIX")


@view_defaults(permission='submit', layout='default')
class ESGFLogon(object):
    def __init__(self, request):
        self.request = request
        self.session = self.request.session

    def appstruct(self):
        return {}

    def generate_form(self):
        submit_button = Button(name='submit', title='Submit', css_class='btn btn-success')
        return Form(schema=ESGFLogonSchema(), buttons=(submit_button,), formid="esgflogon")

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
        except ValidationFailure, e:
            self.session.flash("Form validation failed.", queue='danger')
            return dict(form=e.render())
        except Exception, e:
            self.session.flash("ESGF logon failed.", queue='danger')
        else:
            self.session.flash("ESGF logon succeded", queue='success')
        return HTTPFound(location=self.request.route_path('esgflogon'))

    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)
        return dict(
            form=form.render(self.appstruct()))


@view_defaults(permission='view', layout='default')
class ESGFSearchActions(object):
    def __init__(self, request):
        self.request = request
        self.esgfsearch = ESGFSearch(request)

    def search_datasets(self):
        result = dict()
        result.update(self.esgfsearch.query_params())
        result.update(self.esgfsearch.search_datasets())
        result['form'] = Form(ESGFSearchSchema())
        result['quickview'] = True
        return result

    def search_items(self):
        return self.esgfsearch.search_items()
