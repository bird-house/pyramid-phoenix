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
        refs = []
        for ref in soup.findAll('catalogref'):
            # Check skips
            title = ref.get("xlink:title")
            if not any([x.match(title) for x in self.skip]):
                refs.append(CatalogRef(url=construct_url(url, ref.get('xlink:href')), title=title))
            else:
                logger.info("Skipping catalogRef based on 'skips'.  Title: %s" % title)
                continue

        # Get the leaf datasets
        ds = []
        for leaf in soup.findAll('dataset'):
            # Subset by the skips
            name = leaf.get("name")
            if any([x.match(name) for x in self.skip]):
                logger.info("Skipping dataset based on 'skips'.  Name: %s" % name)
                continue
            ds.append(Dataset(dataset_url=url, name=name, gid=leaf.get('ID')))
        return dict(datasets=ds, catalogs=refs)

class Dataset(object):
    def __init__(self, dataset_url, name, gid):
        self.id = gid
        self.name = name
        self.catalog_url = dataset_url.split("?")[0]

    def __repr__(self):
        return "<Dataset id: {0.id}, name: {0.name}>".format(self)

class CatalogRef(object):
    def __init__(self, url, title):
        self.title = title
        self.url = url

    def __repr__(self):
        return "<CatalogRef title: {0.title}, url: {0.url}>".format(self)

