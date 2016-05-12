import os.path

from webhelpers2.html.builder import HTML
from webhelpers2.html.tags import checkbox
from webhelpers2_grid import Grid

import string # TODO replace by mako template
#from mako.template import Template
from mako.lookup import TemplateLookup

import logging
logger = logging.getLogger(__name__)

def get_value(record, attribute, default=None):
    value = default
    if isinstance(record, dict):
        value = record.get(attribute, default)
    elif hasattr(record, attribute):
        value = getattr(record, attribute)
    return value

class CustomGrid(Grid):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        if 'url' not in kwargs:
            kwargs['url'] = request.current_route_url
        super(CustomGrid, self).__init__(*args, **kwargs)
        self.exclude_ordering = ['', 'preview', 'action', '_numbered', '_checkbox']
        if "_checkbox" in self.columns:
            self.labels["_checkbox"] = ""
        if "_checkbox" not in self.column_formats: 
            self.column_formats["_checkbox"] = self.checkbox_column_format 
        self.lookup = TemplateLookup([os.path.join(os.path.dirname(__file__), 'templates', 'grid')])
        #self.user_tz = u'UTC'

    def checkbox_column_format(self, column_number, i, record):
        return HTML.td(checkbox(name="children", value=record.get('identifier'), title="Select item"))

    def render_td(self, renderer, **data):
        mytemplate = self.lookup.get_template(renderer)
        return HTML.td(HTML.literal(mytemplate.render(**data)))

    def label_td(self, attribute, default=None):
        def _column_format(column_number, i, record):
            label = get_value(record, attribute, default)
            return HTML.td(label)
        return _column_format

    def time_ago_td(self, attribute):
        def _column_format(column_number, i, record):
            from phoenix.utils import time_ago_in_words
            timestamp = get_value(record, attribute)
            return HTML.td(time_ago_in_words(timestamp))
        return _column_format

    def timestamp_td(self, attribute):
        def _column_format(column_number, i, record):
            import datetime

            timestamp = get_value(record, attribute)
            
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
        return _column_format

    def size_td(self, attribute):
        def _column_format(column_number, i, record):
            from webhelpers2.number import format_byte_size
            size_in_bytes = get_value(record, attribute)
            size = ''
            if size_in_bytes is not None:
                size = format_byte_size( size_in_bytes )
            return HTML.td(size)
        return _column_format

    def progress_td(self, attribute):
        def _column_format(column_number, i, record):
            progress = get_value(record, attribute, 0)
            return self.render_td(renderer="progress_td.mako", identifier=i, progress=progress)
        return _column_format

    def userid_td(self, attribute):
        def _column_format(column_number, i, record):
            #TODO: avoid database access ... maybe store additional info at job
            userid = get_value(record, attribute)
            provider_id = 'Unknown'
            if userid:
                user = self.request.db.users.find_one(dict(identifier=userid))
                if user:
                    provider_id = user.get('login_id')
            return HTML.td(provider_id)
        return _column_format
    
    def render_button_td(self, url, title):
        return self.render_td(renderer="button_td.mako", url=url, title=title)

    def render_title_td(self, title, abstract="", keywords=[], data=[], format=None, source="#"):
        return self.render_td(renderer="title_td.mako", title=title, abstract=abstract, keywords=keywords, data=data, format=format, source=source)

    def render_status_td(self, item):
        return self.render_td(renderer="status_td.mako", status=item.get('status'), identifier=item.get('identifier'))

    def render_flag_td(self, flag=False, tooltip=''):
        return self.render_td(renderer="flag_td.mako", flag=flag, tooltip=tooltip)
    
    def render_format_td(self, format, source):
        span_class = 'label'
        if format is None:
            format = 'unknown'
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

    def render_preview_td(self, format, source):
        return self.render_td(renderer="preview_td.mako", format=format, source=source)

    def render_buttongroup_td(self, buttons=[]):
        return self.render_td(renderer="buttongroup_td.mako", buttons=buttons)

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
        return super(CustomGrid, self).generate_header_link(column_number,
                                                            column,
                                                            label_text)
    
    def default_header_column_format(self, column_number, column_name, header_label):
        """Override of the ObjectGrid to use <th> for header columns
        """
        if column_name == "_numbered":
            column_name = "numbered"

        if column_name == "_checkbox":
            header_label = checkbox(name="children", title="Select / deselect all", data_toggle="checkbox")
            return HTML.tag("th", header_label)
        elif column_name in self.exclude_ordering:
            class_name = "c%s %s" % (column_number, column_name)
            return HTML.tag("th", header_label, class_=class_name)
        else:
            header_label = HTML(header_label, HTML.tag("span", class_="marker"))
            class_name = "c%s ordering %s" % (column_number, column_name)
            return HTML.tag("th", header_label, class_=class_name)

    def default_header_ordered_column_format(self, column_number, column_name, header_label):
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






