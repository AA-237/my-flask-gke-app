# SLO Document: My Flask Application

## 1. Service Overview

* **Service Name:** `my-flask-app`
* **Description:** A simple web application deployed on Google Kubernetes Engine (GKE), serving a "Hello World" message. This service represents a critical user-facing component.
* **Critical User Journey:** Successful and timely access to the root path (`/`).

## 2. Service Level Indicators (SLIs)

### 2.1. Availability

* **Description:** The proportion of successful HTTP GET requests to the `/` endpoint.
* **Measurement:**
    * **Good Events:** Count of `http_requests_total` with `method="GET"` and `endpoint="/"`. (Assumes 2xx HTTP status codes are implicitly successful).
    * **Total Events:** Count of `http_requests_total` with `method="GET"` and `endpoint="/"`.
* **Source:** Prometheus metrics scraped from the application, ingested into Google Cloud Monitoring.

### 2.2. Latency

* **Description:** The time taken for HTTP GET requests to the `/` endpoint to complete.
* **Measurement:**
    * **Good Events:** Requests where `http_request_duration_seconds` is less than or equal to 200ms.
    * **Total Events:** All requests where `http_request_duration_seconds` is measured.
* **Source:** Prometheus `http_request_duration_seconds` histogram metric, ingested into Google Cloud Monitoring.

## 3. Service Level Objectives (SLOs)

### 3.1. Availability SLO

* **Objective:** 99.5% of HTTP GET requests to the `/` endpoint will be successful.
* **Period:** Rolling 30-day window.

### 3.2. Latency SLO

* **Objective:** 99% of HTTP GET requests to the `/` endpoint will be served in under 200ms.
* **Period:** Rolling 30-day window.

## 4. Error Budgets and Policies

### 4.1. Availability Error Budget Calculation (30-day window)

* **Total Time in 30 days:** 30 days * 24 hours/day * 60 minutes/hour = 43,200 minutes
* **Allowed Unavailability (Error Budget):** `(1 - 0.995) * 43,200 minutes = 0.005 * 43,200 minutes = 216 minutes`
* **Interpretation:** The `my-flask-app` service can be unavailable for a maximum of 216 minutes (3 hours and 36 minutes) within any rolling 30-day period while still meeting its availability SLO.

### 4.2. Latency Error Budget Calculation (30-day window)

* **Assumed Average Daily Requests:** 10,000 requests/day
* **Total Requests in 30 days:** 10,000 requests/day * 30 days = 300,000 requests
* **Allowed Slow Requests (Error Budget):** `(1 - 0.99) * 300,000 requests = 0.01 * 300,000 requests = 3,000 slow requests`
* **Interpretation:** Up to 3,000 requests can exceed the 200ms latency threshold within any rolling 30-day period.

### 4.3. Error Budget Policies

If the error budget for either SLO is consumed by 50% or more within the rolling 30-day window:

1.  **Review:** An SRE and Development team lead will review recent changes and incident history.
2.  **Prioritize Reliability:** A discussion will be initiated to allocate a portion of the next sprint's capacity (e.g., 20%) to reliability improvements.

If the error budget for either SLO is exhausted (100% consumed):

1.  **Release Freeze:** All non-critical feature deployments to production for `my-flask-app` will be temporarily halted.
2.  **Reliability Sprint:** The team will immediately pivot to a dedicated reliability sprint until the budget begins to replenish or critical issues are resolved.
3.  **Blameless Post-Mortem:** A comprehensive post-mortem will be conducted to identify systemic issues and preventative measures.


