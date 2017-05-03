from pyramid.view import view_config

from phoenix.account.views import Account


class ESGFAccount(Account):
    def appstruct(self):
        return dict(provider='dkrz')

    @view_config(route_name='esgf_login', renderer='templates/account/login.pt')
    def login(self):
        protocol = 'esgf'
        form = self.generate_form(protocol)
        if 'submit' in self.request.POST:
            return self.process_form(form, protocol)
        return dict(form=form.render(self.appstruct()))
