from pyramid.view import view_config, view_defaults
from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound

from deform import Form, Button

from phoenix.views import MyView

import yaml

import logging
logger = logging.getLogger(__name__)

wizard_favorite = "wizard_favorite"
no_favorite = "No Favorite"

class WizardFavorite(object):
    def __init__(self, request, session, email):
        self.request = request
        self.session = session
        self.email = email
        self.favdb = self.request.db.favorites
        if not wizard_favorite in self.session:
            self.load()

    def names(self):
        return self.session[wizard_favorite].keys()
            
    def get(self, name, default=None):
        return self.session[wizard_favorite].get(name)

    def set(self, name, state):
        if name != no_favorite:
            self.session[wizard_favorite][name] = state
            self.session.changed()
        
    def clear(self):
        self.session[wizard_favorite] = {}
        self.session[wizard_favorite][no_favorite] = {}
        self.session.changed()

    def save(self):
        try:
            fav = dict(email=self.email, favorite=yaml.dump(self.session.get(wizard_favorite, {})))
            self.favdb.update({'email':self.email}, fav)
            logger.debug('saved favorite for %s', self.email)
        except:
            logger.exception('saving favorite for %s failed.', self.email)

    def load(self):
        try:
            fav = self.favdb.find_one({'email': self.email})
            if fav is None:
                fav = dict(email=self.email)
                self.favdb.save(fav)
            self.session[wizard_favorite] = yaml.load(fav.get('favorite', '{}'))
            self.session[wizard_favorite][no_favorite] = {}
            self.session.changed()
            logger.debug('loaded favorite for %s', self.email)
        except:
            self.clear()
            logger.exception('loading favorite for %s failed.', self.email)

class WizardState(object):
    def __init__(self, session, initial_step='wizard', final_step='wizard_done'):
        self.session = session
        self.initial_step = initial_step
        self.final_step = final_step
        if not 'wizard' in self.session:
            self.clear()

    def load(self, state):
        import copy
        self.clear()
        self.session['wizard']['state'] = copy.deepcopy(state)
        self.session.changed()

    def dump(self):
        return self.session['wizard']['state']
            
    def current_step(self):
        step = self.initial_step
        if len(self.session['wizard']['chain']) > 0:
            step = self.session['wizard']['chain'][-1]
        return step

    def is_first(self):
        return self.current_step() == self.initial_step

    def is_last(self):
        return self.current_step() == self.final_step

    def next(self, step):
        self.session['wizard']['chain'].append(step)
        self.session.changed()

    def previous(self):
        if len(self.session['wizard']['chain']) > 1:
            self.session['wizard']['chain'].pop()
            self.session.changed()

    def get(self, key, default=None):
        if self.session['wizard']['state'].get(key) is None:
            self.session['wizard']['state'][key] = default
            self.session.changed()
        return self.session['wizard']['state'].get(key)

    def set(self, key, value):
        self.session['wizard']['state'][key] = value
        self.session.changed()

    def clear(self):
        self.session['wizard'] = dict(state={}, chain=[self.initial_step])
        self.session.changed()

@view_defaults(permission='submit', layout='default')
class Wizard(MyView):
    def __init__(self, request, name, title, description=None):
        super(Wizard, self).__init__(request, name, title, description)
        self.csw = self.request.csw
        self.wizard_state = WizardState(self.session)
        self.favorite = WizardFavorite(self.request, self.session, email=authenticated_userid(self.request))

    def buttons(self):
        prev_disabled = not self.prev_ok()
        next_disabled = not self.next_ok()

        prev_button = Button(name='previous', title='Previous',
                             disabled=prev_disabled)   #type=submit|reset|button,value=name,css_type="btn-..."
        next_button = Button(name='next', title='Next',
                             disabled=next_disabled)
        done_button = Button(name='next', title='Done',
                             disabled=next_disabled)
        cancel_button = Button(name='cancel', title='Cancel',
                               css_class='btn btn-danger',
                               disabled=False)
        buttons = []
        # TODO: fix focus button
        if not self.wizard_state.is_first():
            buttons.append(prev_button)
        if self.wizard_state.is_last():
            buttons.append(done_button)
        else:
            buttons.append(next_button)
        buttons.append(cancel_button)
        return buttons

    def prev_ok(self):
        return True

    def next_ok(self):
        return True
    
    def use_ajax(self):
        return False

    def ajax_options(self):
        options = """
        {success:
           function (rText, sText, xhr, form) {
             deform.processCallbacks();
             deform.focusFirstInput();
             var loc = xhr.getResponseHeader('X-Relocate');
                if (loc) {
                  document.location = loc;
                };
             }
        }
        """
        return options

    def success(self, appstruct):
        self.wizard_state.set(self.name, appstruct)

    def appstruct(self):
        return self.wizard_state.get(self.name, {})
    
    def schema(self):
        raise NotImplementedError

    def previous_success(self, appstruct):
        self.success(appstruct)
        return self.previous()

    def previous_failure(self, validation_failure):
        # dont stop previous in case of validation failure
        return self.previous()
    
    def next_success(self, appstruct):
        raise NotImplementedError

    def next_failure(self, validation_failure):
        return dict(title=self.title, form=validation_failure.render())

    def generate_form(self, formid='deform'):
        return Form(
            schema = self.schema(),
            buttons=self.buttons(),
            formid=formid,
            use_ajax=self.use_ajax(),
            ajax_options=self.ajax_options(),
            )

    def process_form(self, form, action):
        from deform import ValidationFailure
        
        success_method = getattr(self, '%s_success' % action)
        failure_method = getattr(self, '%s_failure' % action)
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            result = success_method(appstruct)
        except ValidationFailure as e:
            logger.exception('Validation of wizard view failed.')
            result = failure_method(e)
        return result
        
    def previous(self):
        self.wizard_state.previous()
        return HTTPFound(location=self.request.route_path(self.wizard_state.current_step()))

    def next(self, step):
        self.wizard_state.next(step)
        return HTTPFound(location=self.request.route_path(self.wizard_state.current_step()))

    def cancel(self):
        self.wizard_state.clear()
        return HTTPFound(location=self.request.route_path(self.wizard_state.current_step()))

    def custom_view(self):
        return {}

    def breadcrumbs(self):
        breadcrumbs = super(Wizard, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path('wizard'), title='Wizard'))
        return breadcrumbs

    def resources(self):
        resources = []
        resource = self.wizard_state.get('wizard_source')['source']
        # TODO: refactore this ... there is a common way
        if resource == 'wizard_csw':
            selection = self.wizard_state.get(resource).get('selection', [])
            logger.debug("catalog selection: %s", selection)
            self.csw.getrecordbyid(id=selection)
            resources = [str(rec.source) for rec in self.csw.records.values()]
        return resources

    def view(self):
        form = self.generate_form()

        if 'previous' in self.request.POST:
            return self.process_form(form, 'previous')
        elif 'next' in self.request.POST:
            return self.process_form(form, 'next')
        elif 'cancel' in self.request.POST:
            return self.cancel()
    
        result = dict(title=self.title, form=form.render(self.appstruct()))
        custom = self.custom_view()    
        return dict(result, **custom)
