from phoenix.exceptions import MyProxyLogonFailure

import logging
logger = logging.getLogger(__name__)

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

