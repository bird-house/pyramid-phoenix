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
    wms_dataset_path = None
    # get proxy_reference and wms_dataset_path
    LOGGER.debug("output reference: %s", output.reference)
    proxy_reference = output.reference
    if output.reference:
        wps_output_url = request.registry.settings.get('wps.output.url')
        if request.map_activated and output.mimeType and 'netcdf' in output.mimeType:
            if 'wpsoutputs' in output.reference:
                wms_dataset_path = "outputs" + output.reference.split('wpsoutputs', 1)[1]
        if wps_output_url and output.reference.startswith(wps_output_url):
            proxy_reference = request.route_url(
                'download_wpsoutputs',
                subpath=output.reference.split(wps_output_url, 1)[1])
            LOGGER.debug("proxy reference: %s", proxy_reference)
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
                proxy_reference=escape_output(proxy_reference),
                wms_dataset_path=escape_output(wms_dataset_path),
                category=category)
