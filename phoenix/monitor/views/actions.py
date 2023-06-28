import requests

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.response import Response
from pyramid.response import FileIter

from phoenix.utils import ActionButton
from phoenix.utils import format_tags

import logging
LOGGER = logging.getLogger("PHOENIX")


@view_defaults(permission='edit')
class NodeActions(object):
    """Actions related to job monitor."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session
        self.collection = self.request.db.jobs

    def _selected_children(self):
        """
        Get the selected children of the given context.

        :result: List with select children.
        :rtype: list
        """
        ids = self.session.pop('phoenix.selected-children')
        self.session.changed()
        return ids

    @view_config(route_name='delete_job')
    def delete_job(self):
        job_id = self.request.matchdict.get('job_id')
        # TODO: check permission ... either admin or owner.
        self.collection.delete_one({'identifier': job_id})
        self.session.flash("Job {0} deleted.".format(job_id), queue='info')
        return HTTPFound(location=self.request.route_path('monitor'))

    @view_config(route_name='delete_jobs')
    def delete_jobs(self):
        """
        Delete selected jobs.
        """
        ids = self._selected_children()
        if ids is not None:
            self.collection.delete_many({'identifier': {'$in': ids}})
            self.session.flash("Selected jobs were deleted.", queue='info')
        return HTTPFound(location=self.request.route_path('monitor'))

    @view_config(renderer='json', name='edit_job.json')
    def edit_job(self):
        job_id = self.request.params.get('job_id')
        # TODO: check permission ... either admin or owner.
        job = self.collection.find_one({'identifier': job_id})
        labels = format_tags(job.get('tags', ['dev']))
        return {'identifier': job.get('identifier'), 'caption': job.get('caption', '???'), 'labels': labels}

    @view_config(renderer='json', name='active_jobs.json')
    def active_jobs(self):
        search_filter = dict()
        search_filter['userid'] = authenticated_userid(self.request)
        search_filter['status'] = {'$in': ['ProcessAccepted', 'ProcessPaused', 'ProcessStarted']}
        return list(self.collection.find(search_filter).sort('created', -1))


def monitor_buttons(context, request):
    """
    Build the action buttons for the monitor view based on the current
    state and the permissions of the user.

    :result: List of ActionButtons.
    :rtype: list
    """
    buttons = list()
    buttons.append(ActionButton('delete_jobs', title='Delete',
                                css_class='btn btn-danger',
                                disabled=not request.has_permission('edit')))
    return buttons


def includeme(config):
    """ Pyramid includeme hook.

    :param config: app config
    :type config: :class:`pyramid.config.Configurator`
    """
    config.add_route('delete_job', 'delete_job/{job_id}')
    config.add_route('delete_jobs', 'delete_jobs')
