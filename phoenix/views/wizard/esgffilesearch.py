from pyramid.view import view_config

from phoenix.views.wizard import Wizard

import logging
logger = logging.getLogger(__name__)

class ESGFFileSearch(Wizard):
    def __init__(self, request):
        super(ESGFFileSearch, self).__init__(
            request, name='wizard_esgf_files',
            title="ESGF File Search")

    def schema(self):
        from phoenix.schema import ESGFFilesSchema
        return ESGFFilesSchema().bind(selection=self.wizard_state.get('wizard_esgf')['selection'])

    def next_success(self, appstruct):
        self.success(appstruct)
        
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
            hours_3 = datetime.timedelta(hours=3)
            # cert must be valid for three hours
            if timestamp > now + hours_3:
                return self.next('wizard_check_parameters')
        return self.next('wizard_esgf_credentials')
        
    @view_config(route_name='wizard_esgf_files', renderer='phoenix:templates/wizard/esgf.pt')
    def view(self):
        return super(ESGFFileSearch, self).view()
