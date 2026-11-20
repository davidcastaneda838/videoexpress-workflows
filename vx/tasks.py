"""Task management: status polling, cancel, retry."""
import json


class TasksMixin:
    def task_status(self, uuid):
        """HTTP fallback status for an AI task (primary channel is WebSocket)."""
        return self.get(f"/ai/api/status/{uuid}?upd_estimated_time=1")

    def cancel_task(self, uuid):
        """Cancel a running AI task. Fire ONCE."""
        return self.post(f"/ai/api/cancel/{uuid}")

    def retry_task(self, task_id):
        """Retry a failed task. Fire ONCE."""
        return self.post(f"/ai/api/retry/{task_id}")

    def task_log(self, uid):
        return self.get(f"/ai/api/get_log_value_by_uid/{uid}")
