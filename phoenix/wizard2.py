from pyramid.view import view_config, view_defaults

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='edit', layout='default')
class Wizard:
    def __init__(self, request):
        self.request = request
        self.session = self.request.session
        self.csw = self.request.csw

    # csw function
    def search_csw(self, query=''):
        keywords = [k for k in map(str.strip, str(query).split(' ')) if len(k)>0]

        results = []
        try:
            self.csw.getrecords(keywords=keywords)
            logger.debug('csw results %s', self.csw.results)
            for rec in self.csw.records:
                myrec = self.csw.records[rec]
                results.append(dict(
                    identifier = myrec.identifier,
                    title = myrec.title,
                    abstract = myrec.abstract,
                    subjects = myrec.subjects,
                    format = myrec.format,
                    creator = myrec.creator,
                    modified = myrec.modified,
                    bbox = myrec.bbox,
                    ))
        except:
            logger.exception('could not get items for csw.')
        return results

    @view_config(renderer='json', name='select.csw')
    def select(self):
        # TODO: refactor this ... not efficient
        identifier = self.request.params.get('identifier', None)
        logger.debug('called with %s', identifier)
        if identifier is not None:
            if 'selection' in self.session:
                if identifier in self.session['selection']:
                    self.session['selection'].remove(identifier)
                else:
                    self.session['selection'].append(identifier)
            else:
                self.session['selection'] = [identifier]
        return {}

    @view_config(route_name='csw', renderer='templates/csw.pt')
    def csw_view(self):
        if 'next' in self.request.POST:
            return HTTPFound(location=self.request.route_url('csw'))
        elif 'previous' in self.request.POST:
            return HTTPFound(location=self.request.route_url('csw'))
        elif 'cancel' in self.request.POST:
            return HTTPFound(location=self.request.route_url('csw'))

        query = self.request.params.get('query', None)
        checkbox = self.request.params.get('checkbox', None)
        logger.debug(checkbox)
        items = self.search_csw(query)
        for item in items:
            
            if 'selection' in self.session and  item['identifier'] in self.session['selection']:
                item['selected'] = True
            else:
                item['selected'] = False

        from .grid import CatalogSearchGrid    
        grid = CatalogSearchGrid(
                self.request,
                items,
                ['title', 'subjects', 'selected'],
            )

        return dict(
            title="Catalog Search", 
            description="Search in Catalog Service",
            grid=grid,
            items=items,
        )
