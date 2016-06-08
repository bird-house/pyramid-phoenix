import colander
from deform import Form
from deform import Button
from deform import ValidationFailure
from deform.widget import HiddenWidget

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.security import authenticated_userid

from phoenix.grid import CustomGrid
from phoenix.monitor.views import Monitor
from phoenix.monitor.views.actions import monitor_buttons

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
    """This is the form schema to add and edit form for job labels.
    """
    identifier = colander.SchemaNode(
        colander.String(),
        missing=None,
        widget=HiddenWidget())
    labels = colander.SchemaNode(
        colander.String(),
        title="Input labels as a comma-separated list",
        missing="dev")

class JobList(Monitor):
    def __init__(self, request):
        super(JobList, self).__init__(request, name='monitor', title='Job List')
        self.collection = self.request.db.jobs

    def breadcrumbs(self):
        breadcrumbs = super(JobList, self).breadcrumbs()
        return breadcrumbs

    @view_config(renderer='json', route_name='update_myjobs')
    def update_jobs(self, page=0, limit=10, access=None, status=None):
        search_filter =  {}
        if access == 'public':
            search_filter['access'] = 'public'
        elif access == 'private':
            search_filter['access'] = 'private'
            search_filter['userid'] = authenticated_userid(self.request)
        elif access == 'all' and self.request.has_permission('admin'):
            pass
        else:
            search_filter['userid'] = authenticated_userid(self.request)
        if status:
            search_filter['status'] = status
        count = self.collection.find(search_filter).count()
        items = list(self.collection.find(search_filter).skip(page*limit).limit(limit).sort('created', -1))
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
            self.session.flash("Validation failed.", queue='danger')
        except Exception, e:
            logger.exception("Could not edit job caption.")
            self.session.flash("Edit caption failed.", queue='danger')
        else:
            self.session.flash("Edit caption successful.", queue='success')
        return HTTPFound(location=self.request.route_path('monitor'))

    def generate_labels_form(self, formid="deform_labels"):
        """This helper code generates the form that will be used to add
        and edit job captions based on the schema of the form.
        """
        update_button = Button(name='update_labels', title='Update', css_class='btn btn-success')
        return Form(schema=LabelsSchema(), buttons=(update_button,), formid=formid)

    def process_labels_form(self, form):
        try:
            controls = self.request.POST.items()
            logger.debug("controls %s", controls)
            appstruct = form.validate(controls)
            self.collection.update_one({'identifier': appstruct['identifier']}, {'$set': {'labels': appstruct['labels']}})
        except ValidationFailure, e:
            logger.exception("Validation of labels failed.")
            self.session.flash("Validation failed.", queue='danger')
        except Exception, e:
            logger.exception("Could not edit job labels.")
            self.session.flash("Edit labels failed.", queue='danger')
        else:
            self.session.flash("Edit labels successful.", queue='success')
        return HTTPFound(location=self.request.route_path('monitor'))
    
    @view_config(route_name='monitor', renderer='../templates/monitor/list.pt')
    def view(self):
        caption_form = self.generate_caption_form()
        labels_form = self.generate_labels_form()
        
        if 'update_caption' in self.request.POST:
            return self.process_caption_form(caption_form)
        elif 'update_labels' in self.request.POST:
            return self.process_labels_form(labels_form)
        
        page = int(self.request.params.get('page', '0'))
        limit = int(self.request.params.get('limit', '10'))
        access = self.request.params.get('access')
        status = self.request.params.get('status')

        buttons = monitor_buttons(self.context, self.request)
        for button in buttons:
            if button.name in self.request.POST:
                children = self.request.POST.getall('children')
                self.session['phoenix.selected-children'] = children
                self.session.changed()
                location = button.url(self.context, self.request)
                logger.debug("button url = %s", location)
                return HTTPFound(location, request=self.request)
        
        items, count = self.update_jobs(page=page, limit=limit, access=access, status=status)

        grid = JobsGrid(self.request, items,
                    ['_checkbox', 'status', 'user', 'process', 'service', 'caption', 'duration', 'finished', 'public', 'progress', 'labels', ''],
                    )
        
        return dict(grid=grid, access=access, status=status, page=page, limit=limit, count=count,
                    buttons=buttons,
                    caption_form=caption_form.render(),
                    labels_form=labels_form.render())

class JobsGrid(CustomGrid):
    def __init__(self, request, *args, **kwargs):
        super(JobsGrid, self).__init__(request, *args, **kwargs)
        self.column_formats['status'] = self.status_td
        self.column_formats['user'] = self.user_td('userid')
        self.column_formats['process'] = self.label_td('title')
        self.column_formats['caption'] = self.caption_td
        self.column_formats['duration'] = self.label_td('duration', '???')
        self.column_formats['finished'] = self.time_ago_td('finished')
        self.column_formats['public'] = self.access_td
        self.column_formats['progress'] = self.progress_td('progress')
        self.column_formats['labels'] = self.labels_td
        self.column_formats[''] = self.buttongroup_td
        self.exclude_ordering = self.columns
        
    def status_td(self, col_num, i, item):
        return self.render_status_td(item)
  
    def access_td(self, col_num, i, item):
        return self.render_td(renderer="access_td.mako", access=item.get('access', 'private'))

    def caption_td(self, col_num, i, item):
        return self.render_td(renderer="caption_td.mako", job_id=item.get('identifier'), caption=item.get('caption', '???'))

    def labels_td(self, col_num, i, item):
        return self.render_td(renderer="labels_td.mako", job_id=item.get('identifier'), labels=item.get('labels', 'dev'))
    
    def buttongroup_td(self, col_num, i, item):
        from phoenix.utils import ActionButton
        buttons = []
        buttons.append( ActionButton('results', title=u'Results', css_class=u'btn btn-success btn-xs', icon="fa fa-info-circle",
                                     href=self.request.route_path('monitor_details', tab='log', job_id=item.get('identifier'))))
        buttons.append( ActionButton('restart_job', title=u'Restart', css_class=u'btn btn-success btn-xs', icon="fa fa-refresh",
                                     href="/restart_job/%s" % item.get('identifier'), disabled=item['status']!='ProcessSucceeded'))
        return self.render_buttongroup_td(buttons=buttons)



        


