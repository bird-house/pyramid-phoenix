from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from deform import Form, Button

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)

class WizardFavorite(object):
    session_name = "wizard_favorite"
    
    def __init__(self, session):
        self.session = session
        if not self.session_name in self.session:
            self.clear()
            
    def get(self, key, default=None):
        return self.session[self.session_name].get(key)

    def names(self):
        return self.session[self.session_name].keys()

    def set(self, key, value):
        self.session[self.session_name][key] = value
        self.session.changed()
        
    def clear(self):
        self.session[self.session_name] = {'No Favorite': WizardState(self.session).state(),}
        self.session.changed()

class WizardState(object):
    def __init__(self, session, initial_step='wizard', final_step='wizard_done'):
        self.session = session
        self.initial_step = initial_step
        self.final_step = final_step
        if not 'wizard' in self.session:
            self.clear()

    def load(self, state):
        self.clear()
        self.session['wizard'] = state
        self.session.changed()

    def state(self):
        return self.session['wizard']
            
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

@view_defaults(permission='edit', layout='default')
class Wizard(MyView):
    def __init__(self, request, name, title, description=None):
        super(Wizard, self).__init__(request, name, title, description)
        self.csw = self.request.csw
        self.wizard_state = WizardState(self.session)
        self.favorite = WizardFavorite(self.session)

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
    
    def next_success(self, appstruct):
        raise NotImplementedError

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
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            result = success_method(appstruct)
        except ValidationFailure as e:
            logger.exception('Validation of wizard view failed.')
            result = dict(form=e.render())
        return result
        
    def previous(self):
        self.wizard_state.previous()
        return HTTPFound(location=self.request.route_url(self.wizard_state.current_step()))

    def next(self, step):
        self.wizard_state.next(step)
        return HTTPFound(location=self.request.route_url(self.wizard_state.current_step()))

    def cancel(self):
        self.wizard_state.clear()
        return HTTPFound(location=self.request.route_url(self.wizard_state.current_step()))

    def custom_view(self):
        return {}

    def breadcrumbs(self):
        logger.debug('breadcrumbs %s', self)
        breadcrumbs = super(Wizard, self).breadcrumbs()
        breadcrumbs.append(dict(route_name='wizard', title='Wizard'))
        breadcrumbs.append(dict(route_name=self.name, title=self.title))
        return breadcrumbs

    def view(self):
        form = self.generate_form()
        
        if 'previous' in self.request.POST:
            return self.process_form(form, 'previous')
        elif 'next' in self.request.POST:
            return self.process_form(form, 'next')
        elif 'cancel' in self.request.POST:
            return self.cancel()
        
        custom = self.custom_view()    
        result = dict(form=form.render(self.appstruct()))

        # custom overwrites result
        return dict(result, **custom)
