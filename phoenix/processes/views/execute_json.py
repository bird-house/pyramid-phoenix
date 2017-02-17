from pyramid.view import view_config, view_defaults

from owslib.wps import ComplexData

from phoenix.utils import wps_describe_url

from phoenix.processes.views.execute import ExecuteProcess

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='view', layout='default')
class ExecuteProcessJson(ExecuteProcess):
    def __init__(self, request):
        ExecuteProcess.__init__(self, request)

    def jsonify(self, value):
        # ComplexData type
        if isinstance(value, ComplexData):
            return {'mimeType': value.mimeType, 'encoding': value.encoding, 'schema': value.schema}
        # other type
        else:
            return value

    @view_config(route_name='processes_execute', renderer='json', accept='application/json')
    def view(self):
        dataInputs = getattr(self.process, 'dataInputs', [])
        json_inputs = [{'dataType': data_input.dataType,
                        'name': getattr(data_input, 'identifier', ''),
                        'title': getattr(data_input, 'title', ''),
                        'description': getattr(data_input, 'abstract', ''),
                        'defaultValue': self.jsonify(getattr(data_input, 'defaultValue', None)),
                        'minOccurs': getattr(data_input, 'minOccurs', 0),
                        'maxOccurs': getattr(data_input, 'maxOccurs', 0),
                        'allowedValues': [self.jsonify(value) for value in getattr(data_input, 'allowedValues', [])],
                        'supportedValues': [self.jsonify(value) for value in getattr(data_input, 'supportedValues', [])]
                        } for data_input in dataInputs]
        return dict(
            description=getattr(self.process, 'abstract', ''),
            url=wps_describe_url(self.wps.url, self.processid),
            inputs=json_inputs)
