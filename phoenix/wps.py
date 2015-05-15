import logging
logger = logging.getLogger(__name__)

def count_literal_inputs(wps, identifier):
    process = wps.describeprocess(identifier)
    literal_inputs = []
    for input in process.dataInputs:
        if input.dataType != 'ComplexData':
            literal_inputs.append(input)
    logger.debug('num literal inputs: %d', len(literal_inputs))
    return len(literal_inputs)

def execute_dispel(email, wps, nodes, name='esgsearch_workflow'):
    """
    execute dispel workflow on given wps and with given nodes
    """
    import json
    nodes_json = json.dumps(nodes)

    # generate and run dispel workflow
    identifier='dispel'
    inputs=[('nodes', nodes_json), ('name', name)]
    outputs=[('output', True)]
    from phoenix.tasks import execute
    execute.delay(email, wps.url, identifier, inputs=inputs, outputs=outputs, workflow=True)

def appstruct_to_inputs(appstruct):
    import types
    inputs = []
    for key,values in appstruct.items():
        if key == 'keywords':
            continue
        if type(values) != types.ListType:
            values = [values]
        for value in values:
            inputs.append( (str(key).strip(), str(value).strip()) )
    return inputs

def execute(email, wps, identifier, appstruct):
    process = wps.describeprocess(identifier)
    
    inputs = appstruct_to_inputs(appstruct)
    outputs = []
    for output in process.processOutputs:
        outputs.append( (output.identifier, output.dataType == 'ComplexData' ) )

    from phoenix.tasks import execute
    execute.delay(email, wps.url, identifier, inputs=inputs, outputs=outputs)
    

        
    
