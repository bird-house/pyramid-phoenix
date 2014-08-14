from pyramid_layout.layout import layout_config


@layout_config(name='default',
               template='templates/layouts/bootstrap2.pt'
              )
class AppLayout(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.home_url = request.application_url
        self.headings = []

    @property
    def project_title(self):
        return 'Phoenix - A Pyramid WPS Application for Climate Data'

    def add_heading(self, name, *args, **kw):
        self.headings.append((name, args, kw))

