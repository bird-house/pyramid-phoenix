from os.path import join, dirname

from webhelpers2.html.builder import HTML
from webhelpers2_grid import Grid

import string # TODO replace by mako template
from mako.template import Template
from mako.lookup import TemplateLookup
mylookup = TemplateLookup([join(dirname(__file__), "templates", "grid")])

import logging
logger = logging.getLogger(__name__)

class MyGrid(Grid):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        if 'url' not in kwargs:
            kwargs['url'] = request.current_route_url
        super(MyGrid, self).__init__(*args, **kwargs)
        self.exclude_ordering = ['', 'preview', 'action', '_numbered']
        #self.user_tz = u'UTC'

    def render_td(self, renderer, **data):
        mytemplate = mylookup.get_template(renderer + ".mako")
        return HTML.td(HTML.literal(mytemplate.render(**data)))

    def render_label_td(self, label):
        return self.render_td(renderer="label_td", label=label)

    def render_title_td(self, title, abstract="", keywords=[], data=[], format=None, source="#"):
        return self.render_td(renderer="title_td", title=title, abstract=abstract, keywords=keywords, data=data, format=format, source=source)

    def render_status_td(self, item):
        return self.render_td(renderer="status_td", item=item)
    
    def render_timestamp_td(self, timestamp):
        import datetime
        if timestamp is None:            
            return HTML.td('')
        if type(timestamp) is not datetime.datetime:
            from dateutil import parser as datetime_parser
            timestamp = datetime_parser.parse(str(timestamp))
        span_class = 'due-date badge'
        
        span = HTML.tag(
            "span",
            c=HTML.literal(timestamp.strftime('%Y-%m-%d %H:%M:%S')),
            class_=span_class,
        )
        return HTML.td(span)

    def render_format_td(self, format, source):
        span_class = 'label'
        if 'wps' in format.lower():
            span_class += ' label-warning'
        elif 'wms' in format.lower():
            span_class += ' label-info'
        elif 'netcdf' in format.lower():
            span_class += ' label-success'
        else:
            span_class += ' label-default'
        anchor = string.Template("""\
        <a class="${span_class}" href="${source}" data-format="${format}">${format}</a>
        """)
        return HTML.td(HTML.literal(anchor.substitute(
            {'source': source, 'span_class': span_class, 'format': format} )))

    def render_progress_td(self, identifier, progress=0):
        return self.render_td(renderer="progress_td", identifier=identifier, progress=progress)

    def render_preview_td(self, format, source):
        return self.render_td(renderer="preview_td", format=format, source=source)

    def render_action_td(self, buttongroup=[]):
        return self.render_td(renderer="action_td", buttongroup=buttongroup)

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
            #logger.debug('item %s %s', i, record)
            columns = self.make_columns(i, record)
            if hasattr(self, 'custom_record_format'):
                r = self.custom_record_format(i + 1, record, columns)
            else:
                r = self.default_record_format(i + 1, record, columns)
            records.append(r)
        return HTML(*records)






