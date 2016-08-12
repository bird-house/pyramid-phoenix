import colander
from deform import Form
from deform import Button
from deform import ValidationFailure
from deform.widget import HiddenWidget

from pymongo import ASCENDING, DESCENDING

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid

from phoenix.grid import CustomGrid
from phoenix.views import MyView
from phoenix.monitor.views.actions import monitor_buttons
from phoenix.utils import make_tags

import logging
logger = logging.getLogger(__name__)


class CaptionSchema(colander.MappingSchema):
    """This is the form schema to add and edit form for job captions.
    """
    identifier = colander.SchemaNode(
        colander.String(),
        missing=None,
        widget=HiddenWidget())
    caption = colander.SchemaNode(
        colander.String(),
        missing="???")


class LabelsSchema(colander.MappingSchema):
    """This is the form schema to add and edit form for job tags/labels.
    """
    identifier = colander.SchemaNode(
        colander.String(),
        missing=None,
        widget=HiddenWidget())
    labels = colander.SchemaNode(
        colander.String(),
        title="Input labels as a comma-separated list",
        missing="dev")


@view_defaults(permission='view', layout='default')
class JobList(MyView):
    def __init__(self, request):
        super(JobList, self).__init__(request, name='monitor', title='Job List')
        self.collection = self.request.db.jobs

    def filter_jobs(self, page=0, limit=10, tag=None, access=None, status=None, sort='created'):
        search_filter = {}
        if access == 'public':
            search_filter['tags'] = 'public'
        elif access == 'private':
            search_filter['tags'] = {'$ne': 'public'}
            search_filter['userid'] = authenticated_userid(self.request)
        elif access == 'all' and self.request.has_permission('admin'):
            pass
        else:
            if tag is not None:
                search_filter['tags'] = tag
            search_filter['userid'] = authenticated_userid(self.request)
        if status == 'Running':
            search_filter['status'] = {'$in': ['ProcessAccepted', 'ProcessPaused', 'ProcessStarted']}
        elif status == 'Finished':
            search_filter['status'] = {'$in': ['ProcessSucceeded', 'ProcessFailed']}
        elif status:
            search_filter['status'] = status
        count = self.collection.find(search_filter).count()
        if sort == 'user':
            sort = 'userid'
        elif sort == 'process':
            sort = 'title'
            
        sort_order = DESCENDING if sort == 'finished' or sort == 'created' else ASCENDING
        sort_criteria = [(sort, sort_order)]
        items = list(self.collection.find(search_filter).skip(page*limit).limit(limit).sort(sort_criteria))
        return items, count

    def generate_caption_form(self, formid="deform_caption"):
        """This helper code generates the form that will be used to add
        and edit job captions based on the schema of the form.
        """
        update_button = Button(name='update_caption', title='Update', css_class='btn btn-success')
        return Form(schema=CaptionSchema(), buttons=(update_button,), formid=formid)

    def process_caption_form(self, form):
        try:
            controls = self.request.POST.items()
            logger.debug("controls %s", controls)
            appstruct = form.validate(controls)
            self.collection.update_one({'identifier': appstruct['identifier']}, {'$set': {'caption': appstruct['caption']}})
        except ValidationFailure, e:
            logger.exception("Validation of caption failed.")
            self.session.flash("Validation of caption failed.", queue='danger')
        except Exception, e:
            logger.exception("Edit caption failed.")
            self.session.flash("Edit caption failed.", queue='danger')
        else:
            self.session.flash("Caption updated.", queue='success')
        return HTTPFound(location=self.request.route_path('monitor'))

    def generate_labels_form(self, formid="deform_tags"):
        """This helper code generates the form that will be used to add
        and edit job tags/labels based on the schema of the form.
        """
        update_button = Button(name='update_labels', title='Update', css_class='btn btn-success')
        return Form(schema=LabelsSchema(), buttons=(update_button,), formid=formid)

    def process_labels_form(self, form):
        try:
            controls = self.request.POST.items()
            logger.debug("controls %s", controls)
            appstruct = form.validate(controls)
            tags = make_tags(appstruct['labels'])
            self.collection.update_one({'identifier': appstruct['identifier']}, {'$set': {'tags': tags}})
        except ValidationFailure, e:
            logger.exception("Validation of labels failed.")
            self.session.flash("Validation of labels failed.", queue='danger')
        except Exception, e:
            logger.exception("Edit labels failed.")
            self.session.flash("Edit labels failed.", queue='danger')
        else:
            self.session.flash("Labels updated.", queue='success')
        return HTTPFound(location=self.request.route_path('monitor'))
    
    @view_config(route_name='monitor', renderer='../templates/monitor/list.pt')
    def view(self):
        if not self.request.has_permission('submit'):
            msg = """<strong>Warning:</strong> You are not allowed to monitor jobs. Please <a href="%s" class="alert-link">sign in</a>.""" % self.request.route_path('account_login', protocol='oauth2')
            self.session.flash(msg, queue='warning')
        
        caption_form = self.generate_caption_form()
        labels_form = self.generate_labels_form()
        
        if 'update_caption' in self.request.POST:
            return self.process_caption_form(caption_form)
        elif 'update_labels' in self.request.POST:
            return self.process_labels_form(labels_form)
        
        page = int(self.request.params.get('page', '0'))
        limit = int(self.request.params.get('limit', '50'))
        tag = self.request.params.get('tag')
        access = self.request.params.get('access')
        status = self.request.params.get('status')
        sort = self.request.params.get('sort', 'created')

        buttons = monitor_buttons(self.context, self.request)
        for button in buttons:
            if button.name in self.request.POST:
                children = self.request.POST.getall('children')
                self.session['phoenix.selected-children'] = children
                self.session.changed()
                location = button.url(self.context, self.request)
                logger.debug("button url = %s", location)
                return HTTPFound(location, request=self.request)
        
        items, count = self.filter_jobs(page=page, limit=limit, tag=tag, access=access, status=status, sort=sort)
        # TODO: use mongodb aggregation to get counts by status
        _, count_running = self.filter_jobs(page=page, limit=0, tag=tag, access=access, status='Running', sort=sort)
        _, count_finished = self.filter_jobs(page=page, limit=0, tag=tag, access=access, status='Finished', sort=sort)

        grid = JobsGrid(self.request, items,
                        ['_checkbox', 'status', 'user', 'process', 'service', 'caption', 'duration',
                         'finished', 'labels', ''],)
        
        return dict(grid=grid,
                    access=access, status=status,
                    page=page, limit=limit, tag=tag, sort=sort,
                    count=count, count_running=count_running, count_finished=count_finished,
                    buttons=buttons,
                    caption_form=caption_form.render(),
                    labels_form=labels_form.render())


class JobsGrid(CustomGrid):
    def __init__(self, request, *args, **kwargs):
        super(JobsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['status'] = self.status_td
        self.column_formats['user'] = self.user_td('userid')
        self.column_formats['process'] = self.label_td('title')
        self.column_formats['service'] = self.label_td('service')
        self.column_formats['caption'] = self.caption_td
        self.column_formats['duration'] = self.duration_td
        self.column_formats['finished'] = self.time_ago_td('finished')
        self.column_formats['labels'] = self.labels_td
        self.column_formats[''] = self.buttongroup_td
        self.exclude_ordering = self.columns
        
    def status_td(self, col_num, i, item):
        return self.render_td(renderer="status_td.mako", job_id=item.get('identifier'), status=item.get('status'),
                              progress=item.get('progress', 0))

    def duration_td(self, col_num, i, item):
        return self.render_td(renderer="duration_td.mako", job_id=item.get('identifier'),
                              duration=item.get('duration', '???'))
  
    def caption_td(self, col_num, i, item):
        return self.render_td(renderer="caption_td.mako", job_id=item.get('identifier'),
                              caption=item.get('caption', '???'))

    def labels_td(self, col_num, i, item):
        return self.render_td(renderer="labels_td.mako", job_id=item.get('identifier'), labels=item.get('tags'))
    
    def buttongroup_td(self, col_num, i, item):
        from phoenix.utils import ActionButton
        buttons = list()
        buttons.append(ActionButton('results', title=u'Details', css_class=u'btn btn-default',
                                    href=self.request.route_path('monitor_details', tab='log',
                                                                 job_id=item.get('identifier'))))
        buttons.append(ActionButton('restart_job', title=u'Restart', css_class=u'btn btn-default',
                                    href="/restart_job/%s" % item.get('identifier'),
                                    disabled=item['status'] != 'ProcessSucceeded'))
        return self.render_buttongroup_td(buttons=buttons)



        


