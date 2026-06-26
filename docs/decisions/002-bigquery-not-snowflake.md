# ADR 002: BigQuery thay vì Snowflake

## Quyết định
Dùng Google BigQuery làm data warehouse.

## Lý do
- GCP free trial $300 credit đủ cho toàn bộ project
- BigQuery serverless — không cần quản lý cluster hay warehouse size
- Tích hợp tốt với gcloud ADC, không cần service account key
- Native SQL syntax quen thuộc

## Trade-off
- Vendor lock-in với GCP ecosystem
- Snowflake có Time Travel và Zero-Copy Clone tốt hơn cho một số use case
