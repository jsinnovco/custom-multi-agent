from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_oltp_tracing(endpoint: str = None) -> trace.TracerProvider:
    # Configure Tracing
    # --- Sanitizer span processor to trim overly long attribute values ---
    from opentelemetry.sdk.trace import ReadableSpan, SpanProcessor
    from typing import Any

    _MAX_TAG_LEN = 46
    _SANITIZE_KEYS = {"ai.location.ip", "net.peer.ip", "http.client_ip", "ai.user.ip"}

    def _sanitize_value(val: Any) -> Any:
        if isinstance(val, str) and len(val) > _MAX_TAG_LEN:
            return val[:_MAX_TAG_LEN]
        return val

    class AttributeSanitizerSpanProcessor(SpanProcessor):
        """Trim or sanitize span attributes that are too long before export."""

        def on_start(self, span: ReadableSpan) -> None:
            return None

        def on_end(self, span: ReadableSpan) -> None:
            try:
                attrs = dict(span.attributes) if getattr(span, "attributes", None) is not None else {}
                changed = False
                for k, v in list(attrs.items()):
                    if (k in _SANITIZE_KEYS) or (isinstance(v, str) and len(v) > _MAX_TAG_LEN):
                        safe = _sanitize_value(v)
                        if safe != v:
                            attrs[k] = safe
                            changed = True
                if changed:
                    try:
                        span.attributes.update(attrs)
                    except Exception:
                        for kk, vv in attrs.items():
                            try:
                                span.set_attribute(kk, vv)
                            except Exception:
                                continue
            except Exception:
                return None

        def shutdown(self) -> None:
            return None

        def force_flush(self, timeout_millis: int = 30000) -> bool:
            return True

    # Configure TracerProvider with a Resource and sanitizer
    resource = Resource.create({"service.name": "macwe"})
    tracer_provider = TracerProvider(resource=resource)

    # Add sanitizer before exporter so we don't send overly long values
    tracer_provider.add_span_processor(AttributeSanitizerSpanProcessor())

    # configure OTLP exporter; use provided endpoint if present
    exporter_kwargs = {}
    if endpoint:
        exporter_kwargs["endpoint"] = endpoint

    processor = BatchSpanProcessor(OTLPSpanExporter(**exporter_kwargs))
    tracer_provider.add_span_processor(processor)

    trace.set_tracer_provider(tracer_provider)

    return tracer_provider
