from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views.views import MyView

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='admin', layout='default')    
class SettingsView(MyView):
    def __init__(self, request, title="Settings", description=None):
        super(SettingsView, self).__init__(request, title, description)
        self.settings = self.request.registry.settings
        self.top_title = "Settings"
        self.top_route_name = "all_settings"

class AllSettings(SettingsView):
    def __init__(self, request):
        super(AllSettings, self).__init__(request, 'All Settings')
        self.settings = self.request.registry.settings

    @view_config(route_name='all_settings', renderer='phoenix:templates/settings/all.pt')
    def view(self):
        buttongroups = []
        buttons = []

        buttons.append(dict(url=self.settings.get('supervisor.url'),
                            icon="monitor_edit.png", title="Supervisor", id="external-url"))
        buttons.append(dict(url="/settings/catalog", icon="catalog_pages.png", title="Catalog"))
        buttons.append(dict(url="/settings/users", icon="user_catwomen.png", title="Users"))
        buttons.append(dict(url=self.settings.get('thredds.url'),
                            icon="unidataLogo.png", title="Thredds", id="external-url"))
        buttongroups.append(dict(title='Settings', buttons=buttons))

        return dict(buttongroups=buttongroups)

class CatalogSettings(SettingsView):
    def __init__(self, request):
        super(CatalogSettings, self).__init__(request, 'CSW Catalog Service')
        self.csw = self.request.csw
        self.description = "%s (%s)" % (self.csw.identification.title, self.csw.url)
        
    def generate_service_form(self, formid="deform"):
        from phoenix.schema import CatalogAddServiceSchema
        schema = CatalogAddServiceSchema()
        return Form(
            schema,
            buttons=(Button(name='add_service', title='Add Service'),),
            formid=formid)

    def process_service_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            url = appstruct.get('url')
            self.request.csw.harvest(
                source=url,
                resourcetype=appstruct.get('resource_type'))
            self.session.flash('Added WPS %s' % (url), queue="success")
        except ValidationFailure, e:
            logger.exception('validation of catalog form failed')
            return dict(form = e.render())
        except Exception, e:
            logger.exception('could not harvest wps.')
            self.session.flash('Could not add WPS %s. %s' % (url, e), queue="error")
        return HTTPFound(location=self.request.route_url('catalog_settings'))

    def generate_dataset_form(self, formid="deform"):
        from phoenix.schema import PublishSchema
        schema = PublishSchema().bind(email=self.user_email())
        return Form(
            schema,
            buttons=(Button(name='add_dataset', title='Add Dataset'),),
            formid=formid)

    def process_dataset_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)

            from mako.template import Template
            templ_dc = Template(filename=os.path.join(os.path.dirname(__file__), "templates", "dc.xml"))
            record = templ_dc.render(**appstruct)
            logger.debug('record=%s', record)
            self.request.csw.transaction(ttype="insert", typename='csw:Record', record=str(record))
            self.session.flash('Added Dataset %s' % (appstruct.get('title')), queue="success")
        except ValidationFailure, e:
            logger.exception('validation of catalog form failed')
            return dict(form = e.render())
        except Exception, e:
            logger.exception('could not harvest wps.')
            self.session.flash('Could not add Dataset %s. %s' % (appstruct.get('source'), e), queue="error")
        return HTTPFound(location=self.request.route_url('catalog_settings'))

    @view_config(renderer='json', name='catalog.edit')
    def delete(self):
        identfier = self.request.params.get('identifier', None)
        self.session.flash('Edit catalog entry not implemented yet.', queue="error")
        return {}
    
    @view_config(renderer='json', name='catalog.delete')
    def delete(self):
        identfier = self.request.params.get('identifier', None)
        self.session.flash('Delete catalog entry not implemented yet.', queue="error")
        return {}

    def get_csw_items(self):
        results = []
        try:
            self.csw.getrecords(esn="full")
            logger.debug('csw results %s', self.csw.results)
            for rec in self.csw.records:
                myrec = self.csw.records[rec]
                results.append(dict(
                    source = myrec.source,
                    identifier = myrec.identifier,
                    title = myrec.title,
                    abstract = myrec.abstract,
                    subjects = myrec.subjects,
                    format = myrec.format,
                    creator = myrec.creator,
                    modified = myrec.modified,
                    bbox = myrec.bbox,
                    references = myrec.references,
                    ))
        except:
            logger.exception('could not get items for csw.')
        return results
 
    @view_config(route_name="catalog_settings", renderer='phoenix:templates/settings/catalog.pt')
    def view(self):
        service_form = self.generate_service_form()
        dataset_form = self.generate_dataset_form()
        if 'add_service' in self.request.POST:
            return self.process_service_form(service_form)
        elif 'add_dataset' in self.request.POST:
            return self.process_dataset_form(dataset_form)
        from phoenix.grid import CatalogSettingsGrid
        items = self.get_csw_items()
            
        grid = CatalogSettingsGrid(
                self.request,
                items,
                ['title', 'creator', 'modified', 'format', ''],
            )
        return dict(
            grid=grid,
            items=items,
            service_form=service_form.render(),
            dataset_form=dataset_form.render())

class UserSettings(SettingsView):
    def __init__(self, request):
        super(UserSettings, self).__init__(request, 'Users')

    def sort_order(self):
        """Determine what the current sort parameters are.
        """
        order = self.request.GET.get('order_col', 'activated')
        order_dir = self.request.GET.get('order_dir', 'asc')
        ## if order == 'due_date':
        ##     # handle sorting of NULL values so they are always at the end
        ##     order = 'CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date'
        ## if order == 'task':
        ##     # Sort ignoring case
        ##     order += ' COLLATE NOCASE'
        order_dir = 1 if order_dir == 'asc' else -1
        return dict(order=order, order_dir=order_dir)   
        
    def generate_form(self, formid="deform"):
        from phoenix.schema import UserSchema
        schema = UserSchema().bind()
        return Form(
            schema,
            buttons=('submit',),
            formid=formid)

    def process_form(self, form):
        try:
            controls = self.request.POST.items()
            appstruct = form.validate(controls)
            # TODO: fix update user ... email is readonly
            user = self.get_user(appstruct.get('email'))
            for key in ['name', 'openid', 'organisation', 'notes']:
                user[key] = appstruct.get(key)
            self.userdb.update({'email':self.user_email()}, user)
        except ValidationFailure, e:
            logger.exception('validation of user form failed')
            return dict(form = e.render())
        except Exception, e:
            logger.exception('edit user failed')
            self.session.flash('Edit user failed. %s' % (e), queue="error")
        return HTTPFound(location=self.request.route_url('user_settings'))

    @view_config(route_name='delete_user', renderer='json')
    def delete(self):
        email = self.request.matchdict.get('email')
        if email is not None:
            self.userdb.remove(dict(email=email))
        return {}

    @view_config(route_name='activate_user', renderer='json')
    def activate(self):
        email = self.request.matchdict.get('email')
        if email is not None:
            user = self.userdb.find_one({'email':email})
            user['activated'] = not user.get('activated', True)
            self.userdb.update({'email':email}, user)
        return {}

    @view_config(route_name='edit_user', renderer='json')
    def edit(self):
        email = self.request.matchdict.get('email')
        user = None
        if email is not None:
            user = self.userdb.find_one({'email':email})
        if user is None:
            user = dict(email=email)
        return user

    @view_config(route_name='user_settings', renderer='phoenix:templates/settings/users.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)

        from phoenix.grid import UsersGrid
        order = self.sort_order()
        user_items = list(self.userdb.find().sort(order.get('order'), order.get('order_dir')))
        logger.debug('user_items: %s', user_items)
        grid = UsersGrid(
                self.request,
                user_items,
                ['name', 'email', 'openid', 'organisation', 'notes', 'activated', ''],
            )
        return dict(
            grid=grid,
            items=user_items,
            form=form.render())

