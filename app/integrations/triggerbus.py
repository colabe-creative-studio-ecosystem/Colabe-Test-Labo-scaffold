import json
import uuid
import datetime
from app.core.models import EventOutbox


class TriggerBus:
    @staticmethod
    def publish(topic: str, payload: dict, tenant_id: str, idempotency_key: str):
        event = {
            "event_id": str(uuid.uuid4()),
            "schema_version": "v1",
            "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "region": "eu-central-1",
            "source": "colabe.testlabo",
            "tenant_id": tenant_id,
            "idempotency_key": idempotency_key,
            "trace_id": "trace-id-placeholder",
            "payload": payload,
        }
        with rx.session() as session:
            outbox_item = EventOutbox(
                event_id=event["event_id"],
                topic=topic,
                payload=json.dumps(event),
                status="pending",
            )
            session.add(outbox_item)
            session.commit()