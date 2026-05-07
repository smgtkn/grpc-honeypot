import grpc
import sys
import json
import logging
from datetime import datetime, timezone
from concurrent import futures
from grpc_reflection.v1alpha import reflection
from grpc_health.v1 import health, health_pb2, health_pb2_grpc

import auth_pb2
import auth_pb2_grpc
import admin_pb2
import admin_pb2_grpc
import secrets_pb2
import secrets_pb2_grpc
import riva_asr_pb2
import riva_asr_pb2_grpc
import riva_nlp_pb2
import riva_nlp_pb2_grpc
import riva_tts_pb2
import riva_tts_pb2_grpc
import inference_pb2
import inference_pb2_grpc




def raw_json_log(context, method, request=None):
    try:
        req_str = str(request) if request is not None else None
    except Exception:
        req_str = "<unprintable>"

    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "peer": context.peer(),
        "method": method,
        "metadata": list(context.invocation_metadata()),
        "request": req_str,
    }
    logging.info(json.dumps(event))


class LoggingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        method = handler_call_details.method
        handler = continuation(handler_call_details)

        if handler is None:
            # For unimplemented methods, create a handler that logs and returns UNIMPLEMENTED
            def unimplemented_handler(request, context):
                raw_json_log(context, method, request)
                context.abort(grpc.StatusCode.UNIMPLEMENTED, "method not implemented")

            return grpc.unary_unary_rpc_method_handler(
                unimplemented_handler,
                request_deserializer=None,
                response_serializer=None,
            )

        if handler.unary_unary:
            def wrapper(request, context):
                # If the server machinery handed us raw bytes, try to deserialize
                log_req = request
                try:
                    if isinstance(request, (bytes, bytearray)) and handler.request_deserializer:
                        log_req = handler.request_deserializer(request)
                except Exception:
                    pass

                raw_json_log(context, method, log_req)
                return handler.unary_unary(request, context)

            return grpc.unary_unary_rpc_method_handler(
                wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.stream_stream:
            def wrapper(request_iterator, context):
                def logging_iterator():
                    for req in request_iterator:
                        log_req = req
                        try:
                            if isinstance(req, (bytes, bytearray)) and handler.request_deserializer:
                                log_req = handler.request_deserializer(req)
                        except Exception:
                            pass
                        raw_json_log(context, method, log_req)
                        yield req
                return handler.stream_stream(logging_iterator(), context)

            return grpc.stream_stream_rpc_method_handler(
                wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.unary_stream:
            def wrapper(request, context):
                log_req = request
                try:
                    if isinstance(request, (bytes, bytearray)) and handler.request_deserializer:
                        log_req = handler.request_deserializer(request)
                except Exception:
                    pass

                raw_json_log(context, method, log_req)
                return handler.unary_stream(request, context)

            return grpc.unary_stream_rpc_method_handler(
                wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        if handler.stream_unary:
            def wrapper(request_iterator, context):
                def logging_iterator():
                    for req in request_iterator:
                        log_req = req
                        try:
                            if isinstance(req, (bytes, bytearray)) and handler.request_deserializer:
                                log_req = handler.request_deserializer(req)
                        except Exception:
                            pass
                        raw_json_log(context, method, log_req)
                        yield req
                return handler.stream_unary(logging_iterator(), context)

            return grpc.stream_unary_rpc_method_handler(
                wrapper,
                request_deserializer=handler.request_deserializer,
                response_serializer=handler.response_serializer,
            )

        return handler


class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def Login(self, request, context):
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        return auth_pb2.LoginResponse(success=False)


class AdminService(admin_pb2_grpc.AdminServiceServicer):
    def GetVersion(self, request, context):
        return admin_pb2.VersionResponse(version="1.0.0")


class SecretStore(secrets_pb2_grpc.SecretStoreServicer):
    def GetSecret(self, request, context):
        context.set_code(grpc.StatusCode.PERMISSION_DENIED)
        return secrets_pb2.SecretResponse()


class RivaSpeechRecognition(riva_asr_pb2_grpc.RivaSpeechRecognitionServicer):
    def Recognize(self, request, context):
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        return riva_asr_pb2.RecognizeResponse()

    def StreamingRecognize(self, request_iterator, context):
        for _ in request_iterator:
            break
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        return
        yield


class RivaLanguageUnderstanding(riva_nlp_pb2_grpc.RivaLanguageUnderstandingServicer):
    def Analyze(self, request, context):
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        return riva_nlp_pb2.AnalyzeResponse()

    def ClassifyText(self, request, context):
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        return riva_nlp_pb2.ClassifyTextResponse()


class RivaSpeechSynthesis(riva_tts_pb2_grpc.RivaSpeechSynthesisServicer):
    def Synthesize(self, request, context):
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        return riva_tts_pb2.SynthesizeResponse()

    def SynthesizeOnline(self, request, context):
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        return
        yield


class InferenceService(inference_pb2_grpc.InferenceServiceServicer):
    def Predict(self, request, context):
        context.set_code(grpc.StatusCode.UNAUTHENTICATED)
        return inference_pb2.PredictResponse()


def serve(port=50051, tls_cert=None, tls_key=None):
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=[LoggingInterceptor()],
    )

    auth_pb2_grpc.add_AuthServiceServicer_to_server(AuthService(), server)
    admin_pb2_grpc.add_AdminServiceServicer_to_server(AdminService(), server)
    secrets_pb2_grpc.add_SecretStoreServicer_to_server(SecretStore(), server)
    riva_asr_pb2_grpc.add_RivaSpeechRecognitionServicer_to_server(RivaSpeechRecognition(), server)
    riva_nlp_pb2_grpc.add_RivaLanguageUnderstandingServicer_to_server(RivaLanguageUnderstanding(), server)
    riva_tts_pb2_grpc.add_RivaSpeechSynthesisServicer_to_server(RivaSpeechSynthesis(), server)
    inference_pb2_grpc.add_InferenceServiceServicer_to_server(InferenceService(), server)

    health_servicer = health.HealthServicer()
    health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

    service_names = [
        auth_pb2.DESCRIPTOR.services_by_name["AuthService"].full_name,
        admin_pb2.DESCRIPTOR.services_by_name["AdminService"].full_name,
        secrets_pb2.DESCRIPTOR.services_by_name["SecretStore"].full_name,
        riva_asr_pb2.DESCRIPTOR.services_by_name["RivaSpeechRecognition"].full_name,
        riva_nlp_pb2.DESCRIPTOR.services_by_name["RivaLanguageUnderstanding"].full_name,
        riva_tts_pb2.DESCRIPTOR.services_by_name["RivaSpeechSynthesis"].full_name,
        inference_pb2.DESCRIPTOR.services_by_name["InferenceService"].full_name,
        health.SERVICE_NAME,
        reflection.SERVICE_NAME,
    ]

    for name in service_names:
        health_servicer.set(name, health_pb2.HealthCheckResponse.SERVING)

    reflection.enable_server_reflection(service_names, server)

    # Bind to secure or insecure port depending on provided TLS files
    if tls_cert and tls_key:
        try:
            private_key = open(tls_key, "rb").read()
            certificate_chain = open(tls_cert, "rb").read()
            server_credentials = grpc.ssl_server_credentials(((private_key, certificate_chain),))
            bound = server.add_secure_port(f"[::]:{port}", server_credentials)
            if bound == 0:
                print(f"Failed to bind secure port {port}")
                raise SystemExit(1)
            print(f"Listening securely on {port}")
        except Exception as e:
            print(f"Error setting up TLS: {e}")
            raise
    else:
        server.add_insecure_port(f"[::]:{port}")
        print(f"Listening on {port}")

    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    #take input from user as the port as an argument
    
    import argparse
    parser = argparse.ArgumentParser(description="gRPC Honeypot Server")
    parser.add_argument("--port", type=int, default=50051, help="Port to listen on")
    parser.add_argument("--tls-cert", type=str, default=None, help="Path to TLS certificate (PEM)")
    parser.add_argument("--tls-key", type=str, default=None, help="Path to TLS private key (PEM)")
    args = parser.parse_args()

    if (args.tls_cert and not args.tls_key) or (args.tls_key and not args.tls_cert):
        parser.error("Both --tls-cert and --tls-key must be provided together to enable TLS")

    logging.basicConfig(filename=f"./logs/grpc_honeypot_{args.port}.jsonl", level=logging.INFO, format="%(message)s")

    serve(port=args.port, tls_cert=args.tls_cert, tls_key=args.tls_key)


