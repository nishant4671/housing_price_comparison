Logging & Metrics (0% -> 100%)
In production, you can't just look at terminal print statements. You need:

Loguru JSON Logging: Saving logs in a structured format (JSON) so cloud tools can read them.

Prometheus Metrics: A tool that tracks how many times your API was called and how fast it responds, served on a /metrics endpoint.