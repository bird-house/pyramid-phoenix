import pysolr

import logging
LOGGER = logging.getLogger("PHOENIX")


def solr_search(url, query, page, category, source, tag):
    rows = 10
    start = page * rows

    if not query or not query.strip():
        query = '*:*'
    try:
        solr = pysolr.Solr(url, timeout=10)
        options = {'start': start,
                   'rows': rows,
                   'facet': 'true',
                   'facet.field': ['category', 'source', 'tags'],
                   'facet.limit': 300,
                   'facet.mincount': 1}
        if tag or category or source:
            options['fq'] = []
            if category:
                options['fq'].append('category:{0}'.format(category))
            if source:
                options['fq'].append('source:{0}'.format(source))
            if tag:
                options['fq'].append('tags:{0}'.format(tag))
        results = solr.search(query, **options)
        sources = results.facets['facet_fields']['source'][::2]
        tag_values = results.facets['facet_fields']['tags'][::2]
        tag_counts = results.facets['facet_fields']['tags'][1::2]
        tags = []
        for i in xrange(0, len(tag_counts)):
            if tag_counts[i] == results.hits:
                # each dataset has the same tag
                continue
            tags.append(tag_values[i])
        hits = results.hits
    except:
        LOGGER.exception("solr search failed")
        results = []
        sources = []
        tags = []
        hits = 0
    finally:
        end = min(hits, ((page + 1) * rows))
    return dict(results=results, sources=sources, tags=tags, hits=hits, start=start + 1, end=end)
