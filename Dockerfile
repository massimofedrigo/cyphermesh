FROM python:3.9-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir .

# Espone la porta TCP di default E la porta UDP per discovery
EXPOSE 9001 9999/udp

# Avvio senza parametri: Zero-Config!
CMD ["cyphermesh-run-peer"]