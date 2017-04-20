def patch_myproxy_client():
    """
    Patch myproxyclient to use MESSAGE_DIGEST_TYPE sha256.
    """
    def patched_createCertReq(self, CN, keyPair, messageDigest=None):
        from OpenSSL import crypto
        messageDigest = 'sha256'
        certReq = crypto.X509Req()
        certReq.set_pubkey(keyPair)
        certReq.sign(keyPair, messageDigest)
        derCertReq = crypto.dump_certificate_request(crypto.FILETYPE_ASN1,
                                                     certReq)
        return derCertReq
    import myproxy.client
    myproxy.client.MyProxyClient._createCertReq = patched_createCertReq
