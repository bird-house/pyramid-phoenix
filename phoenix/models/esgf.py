from phoenix.exceptions import MyProxyLogonFailure

import logging
logger = logging.getLogger(__name__)

def query_esgf_files(latest=True, replica=False, distrib=True, **constraints):
    logger.debug('latest=%s, replica=%s, distrib=%s', latest, replica, distrib)
    logger.debug('constraints = %s', constraints)
    from pyesgf.search import SearchConnection
    # TODO: change esgf url
    conn = SearchConnection('http://localhost:8081/esg-search', distrib=distrib)
    fields = ['id', 'title', 'size', 'number_of_files', 'number_of_aggregations']
    ctx = conn.new_context(latest=latest, replica=replica, **constraints)
    logger.debug('datasets found %d', ctx.hit_count)
    result = []
    for ds in ctx.search():
        result.append(ds.json)
    #files = ds.file_context().search()
    #logger.debug('num files = %d', len(files))
    #for file in files:
    #    print file.download_url
    #    print file.filename
    #    print file.size
    return result

def myproxy_logon(request, openid, password):
    inputs = []
    inputs.append( ('openid', openid.encode('ascii', 'ignore')) )
    inputs.append( ('password', password.encode('ascii', 'ignore')) )

    logger.debug('update credentials with openid=%s', openid)

    execution = request.wps.execute(
        identifier='esgf_logon',
        inputs=inputs,
        output=[('output',True),('expires',False)])
    logger.debug('wps url=%s', execution.url)
    
    from owslib.wps import monitorExecution
    monitorExecution(execution)
    
    if not execution.isSucceded():
        raise MyProxyLogonFailure('logon process failed.',
                                  execution.status,
                                  execution.statusMessage)
    credentials = execution.processOutputs[0].reference
    cert_expires = execution.processOutputs[1].data[0]
    logger.debug('cert expires %s', cert_expires)
    return dict(credentials=credentials, cert_expires=cert_expires)

