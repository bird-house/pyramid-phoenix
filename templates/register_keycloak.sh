{% python
  options = parts.get('settings')
  if options['https-port'] in ('80', '443'):
    redirect_uri = "https://{}/account/auth/keycloak/*".format(options['hostname'])
  else:
    redirect_uri = "https://{}:{}/account/auth/keycloak/*".format(options['hostname'], options['https-port'])
%}
#!/bin/bash
echo -e "Please enter keycloak access token: "
read token

curl -X POST \
-d '{ "clientId": "${parts.settings['keycloak-client-id']}", "redirectUris":["${redirect_uri}"], "secret":"${parts.settings['keycloak-client-secret']}" }' \
-H "Content-Type:application/json" \
-H "Authorization: bearer $$token" \
${parts.settings['keycloak-url']}/auth/realms/${parts.settings['keycloak-realm']}/clients-registrations/default
