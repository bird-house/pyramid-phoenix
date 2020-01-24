#!/bin/bash
echo -e "Please enter keycloak access token: "
read token

curl -X POST \
-d '{ "clientId": "${parts.settings['keycloak-client-id']}", "redirectUris":["https://${parts.settings['hostname']}:${parts.settings['https-port']}/account/auth/keycloak/*"], "secret":"${parts.settings['keycloak-client-secret']}" }' \
-H "Content-Type:application/json" \
-H "Authorization: bearer $$token" \
${parts.settings['keycloak-url']}/auth/realms/${parts.settings['keycloak-realm']}/clients-registrations/default
