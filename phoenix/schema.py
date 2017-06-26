import deform
import colander


class CSRFSchema(colander.MappingSchema):
    csrf_token = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.HiddenWidget())
