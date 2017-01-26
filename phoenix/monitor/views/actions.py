import requests

from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.response import Response

from phoenix.utils import ActionButton
from phoenix.utils import format_tags

import logging
LOGGER = logging.getLogger(__name__)


@view_defaults(permission='submit')
class NodeActions(object):
    """Actions related to job monitor."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session
        self.flash = self.request.session.flash
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

    @view_config(route_name='restart_job')
    def restart_job(self):
        job_id = self.request.matchdict.get('job_id')
        job = self.collection.find_one({'identifier': job_id})
        if job.get('is_workflow', False):
            self.flash("Restarting Workflow {0}.".format(job_id), queue='info')
            return HTTPFound(location=self.request.route_path('wizard', _query=[('job_id', job_id)]))
        else:
            self.flash("Restarting Process {0}.".format(job_id), queue='info')
            return HTTPFound(location=self.request.route_path('processes_execute', _query=[('job_id', job_id)]))

    @view_config(route_name='delete_job')
    def delete_job(self):
        job_id = self.request.matchdict.get('job_id')
        # TODO: check permission ... either admin or owner.
        self.collection.delete_one({'identifier': job_id})
        self.flash("Job {0} deleted.".format(job_id), queue='info')
        return HTTPFound(location=self.request.route_path('monitor'))

    @view_config(route_name='delete_jobs')
    def delete_jobs(self):
        """
        Delete selected jobs.
        """
        ids = self._selected_children()
        if ids is not None:
            self.collection.delete_many({'identifier': {'$in': ids}})
            self.flash(u"Selected jobs were deleted.", queue='info')
        return HTTPFound(location=self.request.route_path('monitor'))

    # @view_config(route_name='delete_all_jobs', permission='admin')
    def delete_all_jobs(self):
        count = self.collection.count()
        self.collection.drop()
        self.flash("%d Jobs deleted." % count, queue='info')
        return HTTPFound(location=self.request.route_path('monitor'))

    @view_config(route_name='make_public')
    def make_public(self):
        """
        Make selected jobs public.
        """
        ids = self._selected_children()
        if ids is not None:
            self.collection.update_many({'identifier': {'$in': ids}}, {'$addToSet': {'tags': 'public'}})
            self.flash(u"Selected jobs were made public.", 'info')
        return HTTPFound(location=self.request.route_path('monitor'))

    @view_config(route_name='make_private')
    def make_private(self):
        """
        Make selected jobs private.
        """
        ids = self._selected_children()
        if ids is not None:
            self.collection.update_many({'identifier': {'$in': ids}}, {'$pull': {'tags': 'public'}})
            self.flash(u"Selected jobs were made private.", 'info')
        return HTTPFound(location=self.request.route_path('monitor'))

    @view_config(route_name='set_favorite')
    def set_favorite(self):
        """
        Set selected jobs as favorite.
        """
        ids = self._selected_children()
        if ids is not None:
            self.collection.update_many({'identifier': {'$in': ids}}, {'$addToSet': {'tags': 'fav'}})
            self.flash(u"Set as favorite done.", 'info')
        return HTTPFound(location=self.request.route_path('monitor'))

    @view_config(route_name='unset_favorite')
    def unset_favorite(self):
        """
        Unset selected jobs as favorite.
        """
        ids = self._selected_children()
        if ids is not None:
            self.collection.update_many({'identifier': {'$in': ids}}, {'$pull': {'tags': 'fav'}})
            self.flash(u"Unset as favorite done.", 'info')
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
    # if request.has_permission('admin'):
    #    buttons.append(ActionButton('delete_all_jobs', title=u'Delete all',
    #                                css_class=u'btn btn-danger'))
    buttons.append(ActionButton('delete_jobs', title=u'Delete',
                                css_class=u'btn btn-danger',
                                disabled=not request.has_permission('submit')))
    buttons.append(ActionButton('make_public', title=u'Make Public',
                                css_class=u'btn btn-warning',
                                disabled=not request.has_permission('submit')))
    buttons.append(ActionButton('make_private', title=u'Make Private',
                                css_class=u'btn btn-warning',
                                disabled=not request.has_permission('submit')))
    buttons.append(ActionButton('set_favorite', title=u'Set Favorite',
                                css_class=u'btn btn-success',
                                disabled=not request.has_permission('submit')))
    buttons.append(ActionButton('unset_favorite', title=u'Unset Favorite',
                                css_class=u'btn btn-success',
                                disabled=not request.has_permission('submit')))
    return buttons


def download_wpsoutputs(request):
    path = '/'.join(request.matchdict['subpath'])
    url = request.registry.settings.get('wps.output.url')
    url += '/' + path
    LOGGER.debug("delegate to wpsoutputs: %s", url)
    # forward request to target (without Host Header)
    # h = dict(request.headers)
    # h.pop("Host", h)
    response = requests.get(url, verify=False)
    response.raise_for_status()

    def remove_header(key, values):
        # the default header key should be the standard capitilized version e.g 'Content-Length'
        #TODO: move code to twitcher owsproxy
        try:
            del headers[key]
        except KeyError:
            try:
                del headers[key.lower()]
            except KeyError:
                try:
                    del headers[key.upper()]
                except KeyError:
                    pass
    # clean up headers
    headers = dict(response.headers)
    keys = [k.lower() for k in headers.keys()]
    if 'content-length' in keys:
        remove_header('Content-Length', headers)
    if 'transfer-encoding' in keys:
        remove_header('Transfer-Encoding', headers)
    if 'content-encoding' in keys:
        remove_header('Content-Encoding', headers)
    if 'connection' in keys:
        remove_header('Connection', headers)
    if 'keep-alive' in keys:
        remove_header('Keep-Alive', headers)

    proxy_response = Response(body=response.content, status=response.status_code)
    proxy_response.headers.update(headers)
    return proxy_response


def includeme(config):
    """ Pyramid includeme hook.

    :param config: app config
    :type config: :class:`pyramid.config.Configurator`
    """

    config.add_route('restart_job', 'restart_job/{job_id}')
    config.add_route('delete_job', 'delete_job/{job_id}')
    config.add_route('delete_jobs', 'delete_jobs')
    # config.add_route('delete_all_jobs', 'delete_all_jobs')
    config.add_route('make_public', 'make_public')
    config.add_route('make_private', 'make_private')
    config.add_route('set_favorite', 'set_favorite')
    config.add_route('unset_favorite', 'unset_favorite')
    # download internal wps outputs
    config.add_route('download_wpsoutputs', '/download/wpsoutputs*subpath')
    config.add_view(download_wpsoutputs, route_name='download_wpsoutputs')
