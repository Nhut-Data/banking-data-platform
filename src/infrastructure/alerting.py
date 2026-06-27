"""
Slack alerting — gửi notification khi DAG/task fail.
"""
import json
import urllib.request
from datetime import datetime

from src.infrastructure.config import settings
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


def send_slack_alert(
    dag_id: str,
    task_id: str,
    error: str,
    execution_date: str | None = None,
) -> None:
    if not settings.slack_webhook_url:
        logger.warning("SLACK_WEBHOOK_URL chưa set — skip alert")
        return

    message = {
        "text": ":red_circle: *Airflow Task Failed*",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🔴 Airflow Task Failed"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*DAG:*\n`{dag_id}`"},
                    {"type": "mrkdwn", "text": f"*Task:*\n`{task_id}`"},
                    {"type": "mrkdwn", "text": f"*Time:*\n{execution_date or datetime.now().isoformat()}"},
                    {"type": "mrkdwn", "text": f"*Error:*\n```{error[:300]}```"},
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View in Airflow"},
                        "url": f"http://localhost:8080/dags/{dag_id}",
                    }
                ],
            },
        ],
    }

    try:
        data = json.dumps(message).encode("utf-8")
        req = urllib.request.Request(
            settings.slack_webhook_url,
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            logger.info("Slack alert sent | status=%d", resp.status)
    except Exception as e:
        logger.error("Slack alert FAILED | error=%s", e)


def on_failure_callback(context: dict) -> None:
    """Airflow on_failure_callback — thêm vào DEFAULT_ARGS của DAG."""
    send_slack_alert(
        dag_id=context["dag"].dag_id,
        task_id=context["task_instance"].task_id,
        error=str(context.get("exception", "Unknown error")),
        execution_date=str(context.get("logical_date", "")),
    )
