# Reference: PrometheusRule for Image Inspection Failure Rate

## SLO Parameters (from RELIABILITY.md)
- SLO threshold: image inspection success rate > 95% (i.e., failure rate > 5% triggers alert)
- Measurement window: 5-minute rate for the alert expression
- Alert severity: critical

## Correct Metric Names
- Failures: `mto_ppo_ctrl_failed_image_inspection_total`
- Total processed: `mto_ppo_ctrl_processed_pods_total`

Using any other metric names (e.g., `image_inspection_errors_total`) is a hallucination.

## Correct YAML

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: multiarch-tuning-operator-alerts
  namespace: multiarch-tuning-operator
  labels:
    prometheus: k8s
    role: alert-rules
spec:
  groups:
    - name: multiarch-tuning-operator.rules
      rules:
        - alert: MultiarchImageInspectionFailureRateCritical
          expr: |
            rate(mto_ppo_ctrl_failed_image_inspection_total[5m])
            /
            rate(mto_ppo_ctrl_processed_pods_total[5m])
            > 0.05
          for: 5m
          labels:
            severity: critical
          annotations:
            message: >-
              Multiarch Tuning Operator image inspection failure rate is above 5%
              (SLO threshold). Current rate: {{ $value | humanizePercentage }}.
              Check image registry connectivity and authentication.
```

## Key Correctness Criteria
- Threshold is exactly `0.05` (5%) — not a made-up number
- Uses the documented metric counter names with `mto_ppo_ctrl_` prefix
- `rate()` applied to counters (correct) — not `irate()` or raw counter value
- `for: 5m` prevents flapping from transient errors
- `severity: critical` matches the SLO importance

## Score 5 Criteria
- Correct metric names (`mto_ppo_ctrl_failed_image_inspection_total` and `mto_ppo_ctrl_processed_pods_total`)
- Threshold of 0.05 (5%) — the documented SLO
- Valid PrometheusRule YAML structure
- Human-readable annotations.message
- `rate()` function applied correctly to counters
