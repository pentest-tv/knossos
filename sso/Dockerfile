# Lightweight SSO / token service (sso-01). Issues HS256 JWTs signed with a weak secret.
# The student captures a user token, cracks the signing secret offline (hashcat -m 16500),
# forges an admin token, and reads the flag from the admin endpoint. Stands in for a heavy
# IdP while teaching the core JWT/token attack.
ARG PYTHON_IMAGE=python:3.12-slim
FROM ${PYTHON_IMAGE}

RUN pip install --no-cache-dir flask pyjwt

COPY app.py /app/app.py

EXPOSE 80
CMD ["python3", "/app/app.py"]
