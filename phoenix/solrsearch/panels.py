from pyramid_layout.panel import panel_config

from phoenix.solrsearch.search import solr_search

import logging
LOGGER = logging.getLogger("PHOENIX")


def query_path(request):
    # TODO: this is dirty. solrsearch should be a widget or/and use jquery ajax requests.
    current_path = request.current_route_path()
    if current_path.startswith('/wizard'):
        q_path = 'wizard_solr'
    else:
        q_path = 'solrsearch'
    return q_path


@panel_config(name='solrsearch_script', renderer='templates/solrsearch/panels/script.pt')
def solrsearch_script(context, request):
    query = request.params.get('q', '')
    page = int(request.params.get('page', '0'))
    return dict(query_path=query_path(request), query=query, page=page)


@panel_config(name='solrsearch', renderer='templates/solrsearch/panels/search.pt')
def solrsearch(context, request):
    # TODO: configure this panel dynamically
    query = request.params.get('q', '')
    page = int(request.params.get('page', '0'))
    category = request.params.get('category')
    source = request.params.get('source')
    tag = request.params.get('tag')

    LOGGER.debug("solrsearch panel context %s", context)

    result = dict(query_path=query_path(request), query=query, page=page, category=category, selected_source=source)
    url = request.registry.settings.get('solr.url')
    result.update(solr_search(url=url, query=query, page=page, category=category, source=source, tag=tag))
    return result
