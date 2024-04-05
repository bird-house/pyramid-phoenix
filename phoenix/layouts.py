from pyramid_layout.layout import layout_config


@layout_config(name="default", template="phoenix:templates/layouts/default.pt")
class PageLayout(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.home_url = request.application_url
        self.headings = []
        self.breadcrumbs = []

    @property
    def project_brand(self):
        return self.request.registry.settings.get("phoenix.brand", "Phoenix")

    @property
    def project_logo(self):
        return self.request.registry.settings.get("phoenix.logo", "Phoenix")

    @property
    def project_badgeA(self):
        return self.request.registry.settings.get("phoenix.badgeA", "")

    @property
    def project_badgeB(self):
        return self.request.registry.settings.get("phoenix.badgeB", "")

    @property
    def project_title(self):
        return self.request.registry.settings.get("phoenix.title", "Phoenix")

    @property
    def project_description(self):
        return self.request.registry.settings.get(
            "phoenix.description", "A Python Web App to interact with WPS"
        )

    @property
    def project_theme(self):
        return self.request.registry.settings.get("phoenix.theme", "red")

    @property
    def project_docs(self):
        return self.request.registry.settings.get(
            "phoenix.docs", "https://pyramid-phoenix.readthedocs.org/"
        )

    @property
    def project_imprint(self):
        return self.request.registry.settings.get(
            "phoenix.imprint", "https://www.dkrz.de/about/kontakt/impressum"
        )

    @property
    def project_policy(self):
        return self.request.registry.settings.get(
            "phoenix.policy",
            "https://www.dkrz.de/en/about-en/contact/en-datenschutzhinweise",
        )

    @property
    def matomo_enabled(self):
        try:
            enabled = int(self.matomo_site_id) > 0
        except:
            enabled = False
        return enabled

    @property
    def matomo_url(self):
        return self.request.registry.settings.get("matomo.url", "")

    @property
    def matomo_site_id(self):
        return self.request.registry.settings.get("matomo.site_id", "")

    def add_breadcrumb(self, route_path, title):
        self.breadcrumbs.append(dict(route_path=route_path, title=title))

    def add_heading(self, name, *args, **kw):
        self.headings.append((name, args, kw))
