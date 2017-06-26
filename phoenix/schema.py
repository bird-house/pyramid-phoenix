import deform
import colander

from phoenix.geoform.widget import TagsWidget


class CSRFSchema(colander.MappingSchema):
    csrf_token = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget())


class PublishSchema(colander.MappingSchema):
    import uuid

    @colander.deferred
    def deferred_default_creator(node, kw):
        return kw.get('email')

    @colander.deferred
    def deferred_default_format(node, kw):
        return kw.get('format', "application/x-netcdf")

    identifier = colander.SchemaNode(
        colander.String(),
        default=uuid.uuid4().get_urn())
    title = colander.SchemaNode(colander.String())
    abstract = colander.SchemaNode(
        colander.String(),
        missing='',
        default='',
        validator=colander.Length(max=150),
        widget=deform.widget.TextAreaWidget(rows=2, cols=80))
    creator = colander.SchemaNode(
        colander.String(),
        validator=colander.Email(),
        default=deferred_default_creator,)
    source = colander.SchemaNode(
        colander.String(),
        description='URL to the source',
        validator=colander.url)
    format = colander.SchemaNode(
        colander.String(),
        default=deferred_default_format,
        description='Format of your source. Example: NetCDF',
    )
    subjects = colander.SchemaNode(
        colander.String(),
        default='test',
        missing='test',
        description="Keywords: tas, temperature, ...",
        widget=TagsWidget(),
    )
    rights = colander.SchemaNode(
        colander.String(),
        missing='Unknown',
        default='Free for non-commercial use',
    )
