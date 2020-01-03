from pyramid_layout.panel import panel_config

from phoenix.utils import root_path

import logging
logger = logging.getLogger(__name__)


@panel_config(name='navbar', renderer='phoenix:templates/panels/navbar.pt')
def navbar(context, request):
    def nav_item(name, url, icon=None):
        active = root_path(request.current_route_path()) == root_path(url)
        return dict(name=name, url=url, active=active, icon=icon)

    def dropdown(name, items=None, icon=None):
        items = items or []
        return dict(name=name, icon=icon, items=items)

    items = list()
    items.append(nav_item('Processes', request.route_path('processes')))
    if request.has_permission('edit'):
        items.append(nav_item('Monitor', request.route_path('monitor')))

    subitems = list()
    subitems.append(nav_item('Dashboard', request.route_path('dashboard', tab='overview'), icon='fa fa-dashboard'))

    return dict(items=items, subitems=subitems)


@panel_config(name='messages', renderer='phoenix:templates/panels/messages.pt')
def messages(context, request):
    return dict()


@panel_config(name='breadcrumbs', renderer='phoenix:templates/panels/breadcrumbs.pt')
def breadcrumbs(context, request):
    lm = request.layout_manager
    return dict(breadcrumbs=lm.layout.breadcrumbs)


@panel_config(name='footer', renderer='phoenix:templates/panels/footer.pt')
def footer(context, request):
    from phoenix import __version__ as version
    return dict(version=version)


@panel_config(name='headings')
def headings(context, request):
    lm = request.layout_manager
    layout = lm.layout
    if layout.headings:
        return '\n'.join([lm.render_panel(name, *args, **kw) for name, args, kw in layout.headings])
    return ''
