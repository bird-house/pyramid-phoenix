from pyramid_layout.layout import layout_config


@layout_config(name='default', template='phoenix:templates/layouts/bootstrap2.pt')
class Layouts(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.home_url = request.application_url
        self.headings = []
        self.breadcrumbs = []

    @property
    def project_title(self):
        return 'Phoenix - A Pyramid WPS Application for Climate Data'

    def add_breadcrumb(self, route_name, title):
        self.breadcrumbs.append(dict(route_name=route_name, title=title))

    def add_heading(self, name, *args, **kw):
        self.headings.append((name, args, kw))

