{{- $existing := (lookup "v1" "Secret" .Release.Namespace "oauth2-proxy-secret") }}
apiVersion: v1
kind: Secret
metadata:
  name: oauth2-proxy-secret
  namespace: {{ .Release.Namespace }}
  labels:
    app: oauth2-proxy
type: Opaque
data:
  clientID: {{ (lookup "v1" "Secret" "keycloak" "keycloak-client-secret") | dig "data" "client-id" | default (randAlphaNum 16 | b64enc) }}
  clientSecret: {{ (lookup "v1" "Secret" "keycloak" "keycloak-client-secret") | dig "data" "client-secret" | default (randAlphaNum 32 | b64enc) }}
  cookieSecret: {{ if $existing }}{{ index $existing.data "cookieSecret" }}{{ else }}{{ randAlphaNum 32 | b64enc }}{{ end }}
