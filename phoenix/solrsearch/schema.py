import colander
import deform


class SolrSearchSchema(colander.MappingSchema):
    query = colander.SchemaNode(
        colander.String(),
        missing='',
        default='',
        widget=deform.widget.HiddenWidget())
    category = colander.SchemaNode(
        colander.String(),
        missing='',
        default='',
        widget=deform.widget.HiddenWidget())
    source = colander.SchemaNode(
        colander.String(),
        missing='',
        default='',
        widget=deform.widget.HiddenWidget())
