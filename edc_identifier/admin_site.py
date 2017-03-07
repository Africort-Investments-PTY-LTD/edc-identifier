from django.contrib.admin.sites import AdminSite


class EdcIdentifierAdminSite(AdminSite):
    site_header = 'Edc Identifier'
    site_title = 'Edc Identifier'
    index_title = 'Edc Identifier'
    site_url = '/'
edc_identifier_admin = EdcIdentifierAdminSite(name='edc_identifier_admin')
