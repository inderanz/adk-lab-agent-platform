"""Telemetry & Observability module."""

from .tracing import init_telemetry, trace_span

__all__ = ["init_telemetry", "trace_span"]
