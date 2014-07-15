from webhelpers.html.builder import HTML
from webhelpers.html.grid import ObjectGrid

class UsersGrid(ObjectGrid):
    """A generated table for the todo list that supports ordering of
    the task name and due date columns. We also customize the init so
    that we accept the selected_tag and user_tz.
    """

    def __init__(self, request, *args, **kwargs):
        self.request = request
        if 'url' not in kwargs:
            kwargs['url'] = request.current_route_url
        super(UsersGrid, self).__init__(*args, **kwargs)
        self.exclude_ordering = ['_numbered', 'tags']


    def __html__(self):
        """Override of the ObjectGrid to use a <thead> so that bootstrap
        renders the styles correctly
        """
        records = []
        # first render headers record
        headers = self.make_headers()
        r = self.default_header_record_format(headers)
        # Wrap the headers in a thead
        records.append(HTML.tag('thead', r))
        # now lets render the actual item grid
        for i, record in enumerate(self.itemlist):
            columns = self.make_columns(i, record)
            if hasattr(self, 'custom_record_format'):
                r = self.custom_record_format(i + 1, record, columns)
            else:
                r = self.default_record_format(i + 1, record, columns)
            records.append(r)
        return HTML(*records)
