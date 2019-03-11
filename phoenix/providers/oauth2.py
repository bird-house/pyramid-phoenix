from authomatic.providers.oauth2 import OAuth2


class CEDAProvider(OAuth2):
    """ CEDA oauth2 provider based on classes within the
    authomatic.providers.oauth2 package.
    """

    user_authorization_url = 'https://slcs.ceda.ac.uk/oauth/authorize'
    access_token_url = 'https://slcs.ceda.ac.uk/oauth/access_token'
    user_info_url = 'https://slcs.ceda.ac.uk/oauth/profile/'
    user_info_scope = ['https://slcs.ceda.ac.uk/oauth/profile/']

    same_origin = False

    type_id = 100000  # Any unused ID will do

    @staticmethod
    def _x_user_parser(user, data):

        user_profile = data.get('profile')
        user.username = user_profile.get('accountid') if user_profile else None
        return user
