{{- define "socialnetwork.templates.mongo.mongod.conf"  }}
net:
  tls:
    mode: {{ .Values.tls.mode | default "disabled" }}
    {{- if ne .Values.tls.mode "disabled" }}
    certificateKeyFile: {{ .Values.tls.certificateKeyFile | default "" }}
    {{- end }}
{{- end }}
