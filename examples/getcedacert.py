import OpenSSL
from OpenSSL import crypto
import base64
import urllib
from dateutil import parser as date_parser
import requests

def make_cert_req(access_token):
    key_pair = crypto.PKey()
    key_pair.generate_key(crypto.TYPE_RSA, 2048)

    cert_req = crypto.X509Req()

    # Create public key object
    cert_req.set_pubkey(key_pair)

    # Add the public key to the request
    cert_req.sign(key_pair, 'md5')

    der_cert_req = crypto.dump_certificate_request(crypto.FILETYPE_ASN1,
                                                   cert_req)

    encoded_cert_req = base64.b64encode(der_cert_req)

    headers = {}
    headers['Authorization'] = 'Bearer %s' % access_token
    #post_data = urllib.urlencode({'certificate_request': encoded_cert_req})
    post_data = {'certificate_request': encoded_cert_req}

    return headers, post_data

if __name__ == '__main__':
    import uuid
    mytoken = uuid.uuid4()
    #mytoken = 'get me from somewhere'
    headers, post_data = make_cert_req(mytoken)

    print(headers)
    print(post_data)

    r = requests.post('https://slcs.ceda.ac.uk/oauth/certificate/',
                      headers=headers,
                      data=post_data)
    print(r.text)

    cert = crypto.load_certificate(OpenSSL.SSL.FILETYPE_PEM, r.text)
    expires = date_parser.parse(cert.get_notAfter())
    print(expires)
    comps = cert.get_subject().get_components()
    print(comps)
    openid = comps.get('CN')
    

    
