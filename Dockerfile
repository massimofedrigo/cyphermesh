FROM python:3.9-slim

WORKDIR /app

COPY . .
RUN pip install --no-cache-dir .

EXPOSE 9001

CMD ["cyphermesh-run-peer", "--bootstrap", "SEED"]