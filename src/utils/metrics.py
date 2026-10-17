from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# define metrics
REQUEST_COUNT = Counter('httP_requests_total', "Total HTTP Requests", ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('httP_requests_duraction_in_seconds', "HTTP Requests Latency", ['method', 'endpoint'])

class PrometheusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        
        endpoint = request.url.path
        
        REQUEST_COUNT.labels(methods=request.method, endpoint=endpoint, status=request.status_code).inc()
        REQUEST_LATENCY.labels(methods=request.method, endpoint=endpoint).observe(duration)

        return response


def setup_metrics(app: FastAPI):
    app.add_middleware(PrometheusMiddleware)

    # a good security measeure is to use a random string instead of "/metrics" so no one tries to predict it
    @app.get("/metrics", include_in_schema=False)
    def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)