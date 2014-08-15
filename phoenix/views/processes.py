from pyramid.view import view_config, view_defaults

from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from deform import Form, Button
from deform import ValidationFailure

from phoenix.views import MyView
from phoenix.grid import MyGrid

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class Processes(MyView):
    def __init__(self, request):
        super(Processes, self).__init__(request, 'Processes')

        self.wps = None
        if 'wps.url' in self.session:
            try:
                from owslib.wps import WebProcessingService
                self.wps = WebProcessingService(url=self.session['wps.url'])
                self.description = self.wps.identification.title
            except:
                msg = "Could not connect to wps"
                logger.exception(msg)
                self.session.flash(msg, queue='error')

    def sort_order(self):
        """Determine what the current sort parameters are.
        """
        order = self.request.GET.get('order_col', 'identifier')
        order_dir = self.request.GET.get('order_dir', 'asc')
        order_dir = 1 if order_dir == 'asc' else -1
        return dict(order=order, order_dir=order_dir)
    
    def generate_form(self, formid='deform'):
        from phoenix.schema import ChooseWPSSchema
        from phoenix.models import get_wps_list
        schema = ChooseWPSSchema().bind(wps_list = get_wps_list(self.request))
        return Form(
            schema,
            buttons=('submit',),
            formid=formid
            )
    def process_form(self, form):
        controls = self.request.POST.items()
        try:
            captured = form.validate(controls)
            url = captured.get('url', '')
            session = self.request.session
            session['wps.url'] = url
            session.changed()
        except ValidationFailure, e:
            logger.exception('validation of process view failed.')
            return dict(form=e.render())
        return HTTPFound(location=self.request.route_url('processes'))

    @view_config(route_name='processes', renderer='phoenix:templates/processes.pt')
    def view(self):
        form = self.generate_form()
        if 'submit' in self.request.POST:
            return self.process_form(form)

        items = []
        if self.wps is not None:
            for process in self.wps.processes:
                # TODO: sometime no abstract avail. Fix handling this in owslib
                abstract = ''
                if hasattr(process, 'abstract'):
                    abstract = process.abstract
                processVersion = ''
                if hasattr(process, 'processVersion'):
                    processVersion = process.processVersion
                source = "%s?version=1.0.0&service=WPS&request=describeprocess&identifier=%s" % (self.wps.url, process.identifier)
                items.append(dict(title=process.title,
                                  identifier=process.identifier,
                                  abstract=abstract,
                                  version=processVersion,
                                  source=source))

        # sort items
        order = self.sort_order()
        import operator
        items.sort(key=operator.itemgetter(order['order']), reverse=order['order_dir']==-1)

        grid = ProcessesGrid(
                self.request,
                items,
                ['title', ''],
            )
        return dict(
            grid=grid,
            items=items,
            form=form.render())

from webhelpers.html.builder import HTML
from string import Template

class ProcessesGrid(MyGrid):
    def __init__(self, request, *args, **kwargs):
        super(ProcessesGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['title'] = self.title_td
        self.column_formats[''] = self.action_td

    def title_td(self, col_num, i, item):
        return self.render_title_td(
            title=item.get('title'), 
            abstract=item.get('abstract'),
            format="XML",
            source=item.get('source'))

    def action_td(self, col_num, i, item):
        div = Template("""\
        <div class="btn-group">
            <button class="btn btn-mini btn-success execute" data-value="${identifier}">Execute</button>
        </div>
        """)
        return HTML.td(HTML.literal(div.substitute({'identifier': item.get('identifier')} )))
        
