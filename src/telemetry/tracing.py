"""Enterprise OpenTelemetry and Cloud Trace instrumentation."""

import logging
from contextlib import contextmanager
from typing import Generator, Optional
import google.cloud.logging

logger = logging.getLogger("agent_platform.telemetry")

_tracer = None

def init_telemetry(project_id: Optional[str] = None):
    """Initializes Cloud Logging and OpenTelemetry tracing providers."""
    global _tracer
    try:
        logging_client = google.cloud.logging.Client(project=project_id)
        logging_client.setup_logging()
        logger.info("[Telemetry] Google Cloud Logging configured.")
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        logger.warning(f"[Telemetry] Running local logging fallback: {e}")

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

        provider = TracerProvider()
        cloud_exporter = CloudTraceSpanExporter(project_id=project_id)
        provider.add_span_processor(BatchSpanProcessor(cloud_exporter))
        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer("agent-platform-runtime")
        logger.info("[Telemetry] OpenTelemetry Cloud Trace SpanExporter initialized.")
    except Exception as e:
        logger.info(f"[Telemetry] OpenTelemetry Cloud Trace unavailable in local test mode ({e}). Using standard tracer.")
        try:
            from opentelemetry import trace
            _tracer = trace.get_tracer("agent-platform-runtime-fallback")
        except ImportError:
            _tracer = None

@contextmanager
def trace_span(span_name: str, attributes: Optional[dict] = None) -> Generator:
    """Context manager for distributed tracing spans."""
    if _tracer:
        with _tracer.start_as_current_span(span_name) as span:
            if attributes:
                for k, v in attributes.items():
                    span.set_attribute(k, str(v))
            yield span
    else:
        logger.debug(f"[TraceSpan: {span_name}] attributes={attributes}")
        yield None
