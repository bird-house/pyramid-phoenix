"""
This code is based on thredds_crawler: https://github.com/asascience-open/thredds_crawler
"""

import requests
import urlparse
import re
import os
from bs4 import BeautifulSoup

import logging
logger = logging.getLogger(__name__)

def construct_url(url, href):
    u = urlparse.urlsplit(url)
    base_url = u.scheme + "://" + u.netloc
    relative_path = urlparse.urljoin(base_url,os.path.split(u.path)[0])

    if href[0] == "/":
        # Absolute paths
        cat = urlparse.urljoin(base_url, href)
    elif href[0:4] == "http":
        # Full HTTP links
        cat = href
    else:
        # Relative paths.
        cat = relative_path + "/" + href

    return cat

def dataset_services(dataset_url):
    logger.debug("service for dataset url: %s", dataset_url)
    
    r = requests.get(dataset_url)
    soup = BeautifulSoup(r.content)

    dataset = soup.dataset
    gid = dataset.get("id")
    name = dataset.get("name")
    catalog_url = dataset_url.split("?")[0]
     
    service_tag = dataset.servicename
    if service_tag is None:
        service_tag = dataset.metadata.servicename
    service_name = service_tag.text

    services = []
    for service in soup.findAll('service', attrs=dict(name=service_name)):
        if service.get("servicetype") == "Compound":
            for s in service.findAll("service"):
                url = construct_url(dataset_url, s.get('base')) + dataset.get("urlpath")
                if s.get("suffix") is not None:
                    url += s.get("suffix")
                services.append( {'name' : s.get('name'), 'service' : s.get('servicetype'), 'url' : url } )
        else:
            url = construct_url(dataset_url, service.get('base')) + dataset.get("urlpath") + service.get("suffix", "")
            services.append( {'name' : service.get('name'), 'service' : service.get('servicetype'), 'url' : url } )
    logger.debug("found services: %s", services)
    return services
    
class TdsClient(object):

    SKIPS = [".*files.*", ".*Individual Files.*", ".*File_Access.*", ".*Forecast Model Run.*", ".*Constant Forecast Offset.*", ".*Constant Forecast Date.*"]

    def __init__(self, catalog_url, skip=None):
        """
        skip:   list of dataset names and/or a catalogRef titles.  Python regex supported.
        """
        self.catalog_url = catalog_url

        # Skip these dataset links, such as a list of files
        # ie. "files/"
        if skip is None:
            skip = TdsClient.SKIPS
        self.skip = map(lambda x: re.compile(x), skip)

    def get_objects(self, url=None):
        if url is None:
            url = self.catalog_url
        
        # Replace .html with .xml extension
        u = urlparse.urlsplit(url)
        name, ext = os.path.splitext(u.path)
        if ext == ".html":
            u = urlparse.urlsplit(url.replace(".html", ".xml"))
        url = u.geturl()
        
        # Get soup presentation of thredds xml response
        r = requests.get(url)
        soup = BeautifulSoup(r.content)

        # Get the catalogRefs:
        ds = []
        for ref in soup.findAll('catalogref'):
            # Check skips
            title = ref.get("xlink:title")
            if not any([x.match(title) for x in self.skip]):
                ds.append(CatalogDataset(url=construct_url(url, ref.get('xlink:href')), title=title))
            else:
                logger.info("Skipping catalogRef based on 'skips'.  Title: %s" % title)
                continue

        # Get the leaf datasets
        for leaf in soup.findAll('dataset'):
            # Subset by the skips
            name = leaf.get("name")
            if any([x.match(name) for x in self.skip]):
                logger.info("Skipping dataset based on 'skips'.  Name: %s" % name)
                continue
            elif leaf.get('urlpath') is None:
                logger.debug("Skipping dataset with no urlPath.  Name: %s" % name)
                continue
            ds.append(LeafDataset(name=name, gid=leaf.get('id'), catalog_url=url))
        return ds

class Dataset(object):
    def __init__(self, name, content_type, url=None):
        self._name = name
        self._url = url
        self._content_type = content_type

    def name(self):
        return self._name

    def url(self):
        return self._url

    def content_type(self):
        return self._content_type

    def __repr__(self):
        return "<Dataset name: {0.name}, content type: {0.content_type}>".format(self)
    
class LeafDataset(Dataset):
    def __init__(self, catalog_url, name, gid):
        super(LeafDataset, self).__init__(name=name, content_type="application/netcdf")
        self.gid = gid
        self.catalog_url = catalog_url

    def url(self):
        if self._url is None:
            services = dataset_services(dataset_url="{0.catalog_url}?dataset={0.gid}".format(self))
            for service in services:
                if service.get('service') == 'HTTPServer':
                    self._url = service.get('url')
        return self._url

class CatalogDataset(Dataset):
    def __init__(self, url, title):
        super(CatalogDataset, self).__init__(url=url, name=title, content_type="application/directory")

