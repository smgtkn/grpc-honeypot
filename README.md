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
