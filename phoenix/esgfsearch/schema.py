import colander
from colander import Invalid

import json

from phoenix.geoform.widget import ESGFSearchWidget


def esgfsearch_validator(node, value):
    search = json.loads(value)
    if search.get('hit-count', 0) > 100:
        raise Invalid(node, 'More than 100 datasets selected: %r.' % search['hit-count'])


class ESGFSearchSchema(colander.MappingSchema):
    selection = colander.SchemaNode(
        colander.String(),
        validator=esgfsearch_validator,
        title='ESGF Search',
        widget=ESGFSearchWidget(url="/esg-search"))
