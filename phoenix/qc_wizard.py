
from pyramid.view import view_config

@view_config(route_name='qc_wizard',
             renderer='templates/qc_wizard.pt',
             layout='default',
             permission='edit',
             )
def qc_wizard(request):
    return {"form": "Under Construction"}
