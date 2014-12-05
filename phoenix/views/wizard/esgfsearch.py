from pyramid.view import view_config

from phoenix.views.wizard import Wizard

import logging
logger = logging.getLogger(__name__)

class ESGFSearch(Wizard):
    def __init__(self, request):
        super(ESGFSearch, self).__init__(request, name='wizard_esgf', title="ESGF Search")

    def schema(self):
        from phoenix.schema import ESGFSearchSchema
        return ESGFSearchSchema()

    def cert_ok(self):
        # TODO: this is the wrong place to skip steps
        cert_expires = self.get_user().get('cert_expires')
        if cert_expires != None:
            logger.debug('cert_expires: %s', cert_expires)
            from phoenix.utils import localize_datetime
            from dateutil import parser as datetime_parser
            timestamp = datetime_parser.parse(cert_expires)
            logger.debug("timezone: %s", timestamp.tzname())
            import datetime
            now = localize_datetime(datetime.datetime.utcnow())
            valid_hours = datetime.timedelta(hours=8)
            # cert must be valid for some hours
            if timestamp > now + valid_hours:
                return True
        return False

    def next_success(self, appstruct):
        self.success(appstruct)
        
        if self.cert_ok():
            return self.next('wizard_done')
        return self.next('wizard_esgf_credentials')

    @view_config(route_name='wizard_esgf', renderer='phoenix:templates/wizard/esgf.pt')
    def view(self):
        return super(ESGFSearch, self).view()
