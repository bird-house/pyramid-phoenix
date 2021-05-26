from pyramid.compat import escape
from urllib.request import urlopen
from lxml import etree

import logging
LOGGER = logging.getLogger("PHOENIX")


def escape_output(output):
    if output:
        if isinstance(output, list):
            return list(map(escape, output))
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


def output_details_from_metlink(output):
    outputs = []
    with urlopen(output.reference) as response:
        html = response.read()

    xml = etree.fromstring(html)

    for child in xml:
        if child.tag.endswith("file"):
            for file_element in child:
                if file_element.tag.endswith("identity"):
                    title = file_element.text
                elif file_element.tag.endswith("metaurl"):
                    reference = file_element.text
                    mime_type = file_element.attrib["mediatype"]

            outputs.append(
                dict(
                    title=title,
                    abstract=f"{title} extracted from {output.title}",
                    identifier=output.identifier,
                    mime_type=mime_type,
                    data=[],
                    reference=escape_output(reference),
                    category="ComplexType",
                )
            )

    return outputs
