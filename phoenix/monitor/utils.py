from pyramid.compat import escape

import logging
LOGGER = logging.getLogger("PHOENIX")


def escape_output(output):
    if output:
        if isinstance(output, list):
            return map(escape, output)
        else:
            return escape(output)
    else:
        return output


def output_details(request, output):
    # get category and data
    if output.mimeType:
        category = 'ComplexType'
        data = output.data
    elif output.dataType == 'BoundingBoxData':
        category = 'BoundingBoxType'
        data = ["{0.minx},{0.miny},{0.maxx},{0.maxy}".format(bbox) for bbox in output.data]
    else:
        category = 'LiteralType'
        data = output.data
    return dict(title=output.title,
                abstract=output.abstract,
                identifier=output.identifier,
                mime_type=output.mimeType,
                data=escape_output(data),
                reference=escape_output(output.reference),
                category=category)
