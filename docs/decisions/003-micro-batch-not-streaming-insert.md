# ADR 003: Micro-batch load thay vì BigQuery Streaming Insert API

## Quyết định
Consumer gom batch 30s → load job thay vì dùng BigQuery tabledata.insertAll API.

## Lý do
- Streaming Insert API tính phí $0.01/200MB, tốn hơn load job ở scale thấp
- Streaming Insert có 1-2 phút buffer trước khi data queryable
- Load job đơn giản hơn, không cần handle streaming buffer inconsistency
- Latency 30s đủ "near real-time" cho use case banking analytics

## Trade-off
- Không phải true real-time (30s delay)
- Nếu consumer crash giữa batch, batch đó bị delay đến lần poll tiếp theo
