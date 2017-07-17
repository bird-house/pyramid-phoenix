from pyramid.settings import asbool


def includeme(config):
    settings = config.registry.settings

    if asbool(settings.get('phoenix.solr', 'false')):
        # actions
        pass
    config.add_route('index_service', '/solr/{service_id}/index')
    config.add_route('clear_index', '/solr/clear')

    # check if solr is activated
    def solr_activated(request):
        settings = request.registry.settings
        return asbool(settings.get('phoenix.solr', 'false'))
    config.add_request_method(solr_activated, reify=True)
