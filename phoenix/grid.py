import logging
logger = logging.getLogger(__name__)

from webhelpers.html.builder import HTML
from webhelpers.html.grid import Grid

from .utils import localize_datetime

class MyGrid(Grid):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        if 'url' not in kwargs:
            kwargs['url'] = request.current_route_url
        super(MyGrid, self).__init__(*args, **kwargs)
        self.exclude_ordering = ['_numbered']

    def generate_header_link(self, column_number, column, label_text):
        """Override of the ObjectGrid to customize the headers. This is
        mostly taken from the example code in ObjectGrid itself.
        """
        GET = dict(self.request.copy().GET)
        self.order_column = GET.pop("order_col", None)
        self.order_dir = GET.pop("order_dir", None)
        # determine new order
        if column == self.order_column and self.order_dir == "desc":
            new_order_dir = "asc"
        else:
            new_order_dir = "desc"
        self.additional_kw['order_col'] = column
        self.additional_kw['order_dir'] = new_order_dir
        new_url = self.url_generator(_query=self.additional_kw)
        # set label for header with link
        label_text = HTML.tag("a", href=new_url, c=label_text)
        return super(MyGrid, self).generate_header_link(column_number,
                                                        column,
                                                        label_text)
    
    def default_header_column_format(self, column_number, column_name,
        header_label):
        """Override of the ObjectGrid to use <th> for header columns
        """
        if column_name == "_numbered":
            column_name = "numbered"
        if column_name in self.exclude_ordering:
            class_name = "c%s %s" % (column_number, column_name)
            return HTML.tag("th", header_label, class_=class_name)
        else:
            header_label = HTML(
                header_label, HTML.tag("span", class_="marker"))
            class_name = "c%s ordering %s" % (column_number, column_name)
            return HTML.tag("th", header_label, class_=class_name)

    def default_header_ordered_column_format(self, column_number, column_name,
                                             header_label):
        """Override of the ObjectGrid to use <th> and to add an icon
        that represents the sort order for the column.
        """
        icon_direction = self.order_dir == 'asc' and 'up' or 'down'
        icon_class = 'icon-chevron-%s' % icon_direction
        icon_tag = HTML.tag("i", class_=icon_class)
        header_label = HTML(header_label, " ", icon_tag)
        if column_name == "_numbered":
            column_name = "numbered"
        class_name = "c%s ordering %s %s" % (
            column_number, self.order_dir, column_name)
        return HTML.tag("th", header_label, class_=class_name)
        

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
            logger.debug('item %s %s', i, record)
            columns = self.make_columns(i, record)
            if hasattr(self, 'custom_record_format'):
                r = self.custom_record_format(i + 1, record, columns)
            else:
                r = self.default_record_format(i + 1, record, columns)
            records.append(r)
        return HTML(*records)

class ProcessesGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(ProcessesGrid, self).__init__(request, *args, **kwargs)
        self.column_formats[''] = self.action_td

    def action_td(self, col_num, i, item):
        """Generate the column that has the actions in it.
        """
        return HTML.td(HTML.literal("""\
        <div class="btn-group">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
          Action
          <span class="caret"></span>
          </a>
          <ul class="dropdown-menu" id="%s">
            <li><a class="process-execute" href="#">Execute</a></li>
            <li><a class="process-execute" href="#">Info</a></li>
          </ul>
        </div>
        """ % item.get('identifier') ))

class OutputDetailsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(OutputDetailsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats[''] = self.action_td

    def action_td(self, col_num, i, item):
        """Generate the column that has the actions in it.
        """
        return HTML.td(HTML.literal("""\
        <div class="btn-group">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
          Action
          <span class="caret"></span>
          </a>
          <ul class="dropdown-menu" id="%s">
            <li><a class="output-publish" href="#">Publish</a></li>
            <li><a class="output-show" href="#">Show in Viewer</a></li>
            <li><a class="output-map" href="#">Show on Map</a></li>
          </ul>
        </div>
        """ % item.get('identifier')))

class JobsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(JobsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['start_time'] = self.start_time_td
        self.column_formats[''] = self.action_td
        #self.user_tz = u'US/Eastern'
        self.user_tz = u'UTC'

    def start_time_td(self, col_num, i, item):
        """Generate the column for the start time.
        """
        if item.get('start_time') is None:
            return HTML.td('')
        span_class = 'due-date badge'
        #if item.start_time:
        #    span_class += ' badge-important'
        start_time = localize_datetime(item.get('start_time'), self.user_tz)
        span = HTML.tag(
            "span",
            c=HTML.literal(start_time.strftime('%Y-%m-%d %H:%M:%S')),
            class_=span_class,
        )
        return HTML.td(span)

    def action_td(self, col_num, i, item):
        """Generate the column that has the actions in it.
        """
        return HTML.td(HTML.literal("""\
        <div class="btn-group">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
          Action
          <span class="caret"></span>
          </a>
          <ul class="dropdown-menu" id="%s">
            <li><a class="job-show" href="#">Show Output Details</a></li>
            <li><a class="job-delete" href="#">Delete</a></li>
          </ul>
        </div>
        """ % item.get('uuid')))
        
class UsersGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(UsersGrid, self).__init__(request, *args, **kwargs)
        self.column_formats[''] = self.action_td

    def action_td(self, col_num, i, item):
        """Generate the column that has the actions in it.
        """
        return HTML.td(HTML.literal("""\
        <div class="btn-group">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
          Action
          <span class="caret"></span>
          </a>
          <ul class="dropdown-menu" id="%s">
            <li><a class="user-edit" href="#">Edit</a></li>
            <li><a class="user-delete" href="#">Delete</a></li>
            <li><a class="user-activate" href="#">Activate/Deactivate</a></li>
          </ul>
        </div>
        """ % item.get('user_id')))

class CatalogGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(CatalogGrid, self).__init__(request, *args, **kwargs)
        self.column_formats[''] = self.action_td

    def action_td(self, col_num, i, item):
        """Generate the column that has the actions in it.
        """
        return HTML.td(HTML.literal("""\
        <div class="btn-group">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
          Action
          <span class="caret"></span>
          </a>
          <ul class="dropdown-menu" id="%s">
            <li><a class="catalog-edit" href="#">Edit</a></li>
            <li><a class="catalog-delete" href="#">Delete</a></li>
          </ul>
        </div>
        """ % item.get('url')))

