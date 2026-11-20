"""Projects: list, open timeline, save, work copies, availability checks."""
import json


class ProjectsMixin:
    def project_list(self, search=""):
        q = f"?search={search}" if search else ""
        return self.get(f"/project/get_list{q}")["results"]

    def project_open(self, project_id):
        """Open a project timeline (tracks + bricks)."""
        return self.get(f"/project/open/{project_id}")

    def timeline_tracks(self, project_id):
        """Normalize /project/open data into a list of track dicts."""
        proj = self.project_open(project_id)
        d = proj["data"]
        if isinstance(d, dict):  # saved timelines may come back keyed by index
            d = [d[k] for k in d if k != "data" and isinstance(d[k], dict)]
        return d

    def project_save(self, project_id, title, timeline_tracks, save_new=0):
        """POST /project/save/<id>; id 0 creates a new project. Fire ONCE."""
        payload = {
            "title": title, "save_new": str(save_new),
            "data": json.dumps(timeline_tracks),
        }
        r = self.post(f"/project/save/{project_id}", payload)
        if not r.get("success", True):
            raise RuntimeError(f"project_save rejected: {r}")
        return r

    def create_work_copy(self, project_id):
        """Create an editable work copy of a project. Fire ONCE."""
        return self.post(f"/project/create_work_copy/{project_id}")

    def check_availability(self, media_ids):
        """Verify media availability before render."""
        return self.post("/project/check_availability",
                         json_body={"files": [{"id": int(m)} for m in media_ids]})

    def project_progress(self):
        return self.get("/project/progress?start=0")
