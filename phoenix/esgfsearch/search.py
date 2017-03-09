from pyramid.settings import asbool

from pyesgf.search import SearchConnection
from pyesgf.search.consts import TYPE_DATASET, TYPE_AGGREGATION, TYPE_FILE

import logging
LOGGER = logging.getLogger(__name__)


def search(request):
    settings = request.registry.settings
    dataset_id = request.params.get(
        'dataset_id',
        u'cordex.output.AFR-44.DMI.ECMWF-ERAINT.evaluation.r1i1p1.HIRHAM5.v2.day.prhmax.v20140804|cordexesg.dmi.dk')
    selected = request.params.get('selected', 'project')
    limit = int(request.params.get('limit', '0'))
    distrib = asbool(request.params.get('distrib', 'false'))
    latest = asbool(request.params.get('latest', 'true'))
    if latest is False:
        latest = None  # all versions
    replica = asbool(request.params.get('replica', 'false'))
    if replica is True:
        replica = None  # master + replica

    constraints = dict()
    if 'constraints' in request.params:
        for constrain in request.params['constraints'].split(','):
            if constrain.strip():
                key, value = constrain.split(':', 1)
                constraints[key] = value

    facets = [
        "access",
        "cf_standard_name",
        "cmor_table",
        "data_node",
        "domain",
        "driving_model",
        "ensemble",
        "experiment",
        "institute",
        "model",
        "product",
        "project",
        "realm",
        "time_frequency",
        "variable",
        "variable_long_name",
        "version",
    ]

    conn = SearchConnection(settings.get('esgfsearch.url'), distrib=distrib)
    # ctx = conn.new_context(facets=','.join(facets), latest=latest, replica=replica)
    ctx = conn.new_context(search_type=TYPE_DATASET, latest=latest, replica=replica)
    ctx = ctx.constrain(**constraints)
    if 'start' in request.params and 'end' in request.params:
        ctx = ctx.constrain(
            from_timestamp="{}-01-01T12:00:00Z".format(request.params['start']),
            to_timestamp="{}-12-31T12:00:00Z".format(request.params['end']))
    #return conn.send_search(query_dict=ctx._build_query(), limit=limit)
    #ctx.hit_count
    results = ctx.search(batch_size=10, ignore_facet_check=False)
    categories = [tag for tag in ctx.facet_counts if len(ctx.facet_counts[tag]) > 1]
    keywords = ctx.facet_counts[selected].keys()
    pinned_facets = []
    for facet in ctx.facet_counts:
        if len(ctx.facet_counts[facet]) == 1:
            pinned_facets.append("{}:{}".format(facet, ctx.facet_counts[facet].keys()[0]))
    paged_results = []
    for i in range(0, min(10, ctx.hit_count)):
        paged_results.append(dict(
            title=results[i].dataset_id,
            dataset_id=results[i].dataset_id,
            number_of_files=results[i].number_of_files,
            catalog_url=results[i].urls['THREDDS'][0][0]))
    # get files for dataset
    fctx = conn.new_context(search_type=TYPE_FILE, latest=latest, replica=replica)
    fctx = fctx.constrain(dataset_id=dataset_id)
    file_results = fctx.search(batch_size=10, ignore_facet_check=False)
    return dict(
        hit_count=ctx.hit_count,
        categories=','.join(categories),
        keywords=','.join(keywords),
        pinned_facets=','.join(pinned_facets),
        results=paged_results,
        file_results=file_results)
