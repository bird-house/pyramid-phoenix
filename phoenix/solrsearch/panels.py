from pyramid_layout.panel import panel_config

from .search import solr_search

import logging
logger = logging.getLogger(__name__)


@panel_config(name='solrsearch_script', renderer='templates/solrsearch/panels/script.pt')
def solrsearch_script(context, request):
    query = request.params.get('q', '')
    page = int(request.params.get('page', '0'))
    return dict(query=query, page=page)


@panel_config(name='solrsearch', renderer='templates/solrsearch/panels/search.pt')
def solrsearch(context, request):
    query = request.params.get('q', '')
    page = int(request.params.get('page', '0'))
    category = request.params.get('category')
    source = request.params.get('source')
    tag = request.params.get('tag')

    result = dict(query=query, page=page, category=category, selected_source=source)
    url = request.registry.settings.get('solr.url')
    result.update(solr_search(url=url, query=query, page=page, category=category, source=source, tag=tag))
    # request.session.flash("Solr service is not available.", queue='danger')
    return result
