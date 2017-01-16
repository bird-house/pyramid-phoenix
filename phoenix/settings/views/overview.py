from pyramid.view import view_config, view_defaults

from phoenix.views import MyView

import logging
logger = logging.getLogger(__name__)


@view_defaults(permission='admin', layout='default')
class Overview(MyView):
    def __init__(self, request):
        super(Overview, self).__init__(request, name='settings', title='Overview')

    @view_config(route_name='settings', renderer='../templates/settings/overview.pt')
    def view(self):
        buttongroups = list()
        buttons = list()

        buttons.append(dict(url=self.request.route_path('services'), icon_class="fa fa-server fa-2x", title="Services"))
        if self.request.solr_activated:
            buttons.append(dict(url=self.request.route_path('settings_solr', tab='index'),
                                icon_class="fa fa-search fa-2x", title="Solr"))
        buttons.append(dict(url=self.request.route_path('settings_auth'),
                            icon_class="fa fa-lock fa-2x", title="Auth"))
        buttons.append(dict(url=self.request.route_path('settings_ldap'),
                            icon_class="fa fa-sitemap fa-2x", title="LDAP"))
        buttons.append(dict(url=self.request.route_path('settings_github'),
                            icon_class="fa fa-github fa-2x", title="GitHub"))
        buttons.append(dict(url=self.request.route_path('settings_esgf'),
                            icon_class="fa fa-globe fa-2x", title="ESGF"))
        buttongroups.append(dict(title='Settings', buttons=buttons))

        return dict(buttongroups=buttongroups)
