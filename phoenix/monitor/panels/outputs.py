from lib2to3.pgen2.token import ISTERMINAL
from pyramid_layout.panel import panel_config

from phoenix.wps import check_status
from phoenix.monitor.utils import output_details

import logging

LOGGER = logging.getLogger(__name__)


def collect_outputs(status_location=None, response=None):
    execution = check_status(url=status_location, response=response, sleep_secs=0)
    outputs = {}
    for output in execution.processOutputs:
        outputs[output.identifier] = output
    return outputs


def process_outputs(request, job_id):
    job = request.db.jobs.find_one({"identifier": job_id})
    outputs = {}
    if job and job.get("status") == "ProcessSucceeded":
        outputs = collect_outputs(
            status_location=job.get("status_location"), response=job.get("response")
        )
    return outputs


class Outputs(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session

    def filter_outputs(self, items):
        # TODO: quick and dirty for CLINT. Needs to use WPS metadata.
        items = sorted(items, key=lambda item: item["identifier"], reverse=1)
        preview = None
        filtered_items = []
        # filter previews
        for item in items:
            if (
                "preview" in item["identifier"].lower()
                or "preview" in item["title"].lower()
            ):
                preview = item["preview"]
            else:
                filtered_items.append(item)
        # set preview
        if preview:
            for item in filtered_items:
                if item["category"] == "ComplexType":
                    if not item["preview"]:
                        item["preview"] = preview
        return filtered_items

    @panel_config(
        name="job_outputs", renderer="phoenix:monitor/templates/monitor/panels/media.pt"
    )
    def panel(self):
        job_id = self.request.matchdict.get("job_id")
        items = []
        for output in list(process_outputs(self.request, job_id).values()):
            items.append(output_details(self.request, output))
        return dict(items=self.filter_outputs(items))
