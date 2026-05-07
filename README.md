# gRPC Honeypot

gRPC request logging with reflection enabled.

## Services

- auth.v1.AuthService
- admin.v1.AdminService
- secrets.v1.SecretStore
- nvidia.riva.asr.RivaSpeechRecognition
- nvidia.riva.nlp.RivaLanguageUnderstanding
- nvidia.riva.tts.RivaSpeechSynthesis
- inference.v1.InferenceService
- grpc.health.v1.Health
- grpc.reflection.v1alpha.ServerReflection

## Run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./generate.sh
python server.py --port 50051
```

## Test

```bash
grpcurl -plaintext localhost:50051 list
grpcurl -plaintext localhost:50051 list nvidia.riva.asr.RivaSpeechRecognition
grpcurl -plaintext localhost:50051 list nvidia.riva.nlp.RivaLanguageUnderstanding
tail -f grpc_honeypot_50051.jsonl
```

## TLS (optional)

Generate a self-signed cert for local testing and run the server securely:

```bash
./dev-cert.sh  # creates server.crt and server.key
python server.py --port 443 --tls-cert server.crt --tls-key server.key
```

Then test with `grpcurl` over TLS (no client auth):

```bash
grpcurl -proto protos/admin.proto -D . -insecure localhost:443 list
``` 
## Envoy Proxy (optional)

Set up an envoy proxy that logs all the HTTP requests on port 50051 and redirects the traffic to the gRPC server on port 50052.

```bash
docker run --rm -it \
  -v $(pwd)/envoy.yaml:/etc/envoy/envoy.yaml \
  -v $(pwd)/logs:/var/log/envoy \
  -p 50051:50051 \
  --add-host=host.docker.internal:host-gateway \
  -d \
  envoyproxy/envoy:v1.28-latest
  ```