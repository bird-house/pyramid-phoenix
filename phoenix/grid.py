import logging
logger = logging.getLogger(__name__)

from webhelpers.html.builder import HTML
from webhelpers.html.grid import Grid

from string import Template

from .utils import localize_datetime

class MyGrid(Grid):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        if 'url' not in kwargs:
            kwargs['url'] = request.current_route_url
        super(MyGrid, self).__init__(*args, **kwargs)
        self.exclude_ordering = ['action', '_numbered']

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
        self.column_formats['action'] = self.action_td

    def action_td(self, col_num, i, item):
        """Generate the column that has the actions in it.
        """
        div = Template("""\
        <div class="btn-group">
            <button class="btn btn-mini btn-success execute" data-value="${identifier}">Execute</button>
            <button class="btn btn-mini btn-primary info" data-value="${identifier}">Info</button>
        </div>
        """)
        return HTML.td(HTML.literal(div.substitute({'identifier': item.get('identifier')} )))
        

class OutputDetailsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(OutputDetailsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['reference'] = self.reference_td
        self.column_formats['action'] = self.action_td
        self.exclude_ordering = ['data', 'reference', 'action']

    def reference_td(self, col_num, i, item):
        """Generates the column with a download reference.
        """
        anchor = Template("""\
        <a class="reference" href="${reference}"><i class="icon-download"></i></a>
        """)
        return HTML.td(HTML.literal(anchor.substitute( {'reference': item.get('reference')} )))

    def action_td(self, col_num, i, item):
        """Generate the column that has the actions in it.
        """
        div = Template("""\
        <div class="btn-group">
            <button class="btn btn-mini btn-primary publish" data-value="${identifier}">Publish</button>
            <button class="btn btn-mini btn-primary view" data-value="${identifier}">View</button>
            <button class="btn btn-mini btn-primary mapit" data-value="${identifier}">MapIt</button>
        </div>
        """)
        return HTML.td(HTML.literal(div.substitute({'identifier': item.get('identifier')} )))

class JobsGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(JobsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['start_time'] = self.start_time_td
        self.column_formats['status'] = self.status_td
        self.column_formats['message'] = self.message_td
        self.column_formats['status_location'] = self.status_location_td
        self.column_formats['progress'] = self.progress_td
        self.column_formats['action'] = self.action_td
        #self.user_tz = u'US/Eastern'
        self.user_tz = u'UTC'
        self.exclude_ordering = ['message', 'action']

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

    def status_td(self, col_num, i, item):
        """Generate the column for the job status.
        """
        status = item.get('status')
        if status is None:
            return HTML.td('')
        span_class = 'label'
        if status == 'ProcessSucceeded':
            span_class += ' label-success'
        elif status == 'ProcessFailed':
            span_class += ' label-warning'
        elif status == 'Exception':
            span_class += ' label-important'
        else:
            span_class += ' label-info'
            
        span = HTML.tag(
            "span",
            c=HTML.literal(status),
            class_=span_class,
            id_="status-%s" % item.get('uuid'))
        return HTML.td(span)

    def message_td(self, col_num, i, item):
        """Generates the column with job message.
        """
        message = item.get('message')
        for error in item.get('errors'):
            message += ', Exception: %s' % error
        span = HTML.tag(
            "span",
            c=HTML.literal(message),
            class_="",
            id_="message-%s" % item.get('uuid'))
        return HTML.td(span)

    def status_location_td(self, col_num, i, item):
        anchor = Template("""\
        <a class="reference" href="${url}"><i class="icon-download"></i></a>
        """)
        return HTML.td(HTML.literal(anchor.substitute( {'url': item.get('status_location')} )))

    def progress_td(self, col_num, i, item):
        """Generate the column for the job progress.
        """
        progress = item.get('progress', 100)
        if progress is None:
            return HTML.td('')
        span_class = 'progress progress-info bar'

        div_bar = HTML.tag(
            "div",
            c=HTML.literal(progress),
            class_="bar",
            style_="width: %d%s" % (progress, '%'),
            id_="progress-%s" % item.get('uuid'))
        div_progress = HTML.tag(
            "div",
            c=div_bar,
            class_="progress progress-info")
       
        return HTML.td(div_progress)

    def action_td(self, col_num, i, item):
        """Generate the column that has the actions in it.
        """
        div = Template("""\
        <div class="btn-group">
            <button class="btn btn-mini btn-primary show" data-value="${jobid}">Details</button>
            <button class="btn btn-mini btn-danger delete" data-value="${jobid}">Delete</button>
        </div>
        """)
        return HTML.td(HTML.literal(div.substitute({'jobid': item.get('uuid')} )))

class CatalogSearchGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(CatalogSearchGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['selected'] = self.selected_td
        #self.exclude_ordering = ['action']

    def selected_td(self, col_num, i, item):
        """Generate the column for selecting items.
        """
        icon_class = "icon-thumbs-down"
        if item['selected'] == True:
            icon_class = "icon-thumbs-up"
        div = Template("""\
        <button class="btn btn-mini select" data-value="${identifier}"><i class="${icon_class}"></i></button>
        """)
        return HTML.td(HTML.literal(div.substitute({'identifier': item['identifier'], 'icon_class': icon_class} )))
       
        
class UsersGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(UsersGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['action'] = self.action_td

    def action_td(self, col_num, i, item):
        """Generate the column that has the actions in it.
        """
        div = Template("""\
        <div class="btn-group">
            <button class="btn btn-mini btn-primary edit" data-value="${user_id}">Edit</button>
            <button class="btn btn-mini btn-danger delete" data-value="${user_id}">Delete</button>
            <button class="btn btn-mini btn-primary activate" data-value="${user_id}">Activate</button>
        </div>
        """)
        return HTML.td(HTML.literal(div.substitute({'user_id': item.get('user_id')} )))

class CatalogGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(CatalogGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['action'] = self.action_td

    def action_td(self, col_num, i, item):
        """Generate the column that has the actions in it.
        """
        div = Template("""\
        <div class="btn-group">
            <button class="btn btn-mini btn-danger delete" data-value="${identifier}">Delete</button>
        </div>
        """)
        return HTML.td(HTML.literal(div.substitute({'identifier': item.get('identifier')} )))
       

