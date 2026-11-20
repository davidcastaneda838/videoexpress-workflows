"""TTS / voice cloning via /voice_clone/* and AI sound generation."""
import time


class AudioMixin:
    def tts_languages(self):
        return self.get("/voice_clone/languages_list")

    def list_voices(self, category="system", language=None, language_code=None):
        """category: system|designed|public_library|cloned."""
        q = []
        if language is not None:
            q.append(f"language={language}")
        if language_code:
            q.append(f"languageCode={language_code}")
        suffix = ("?" + "&".join(q)) if q else ""
        return self.get(f"/voice_clone/voices/{category}{suffix}")

    def create_audio(self, text, voice, language=None, language_code=None,
                     translate=0, boost_similarity=0, project_id=None):
        """TTS / cloned-voice audio. Fire ONCE. Returns the job uuid;
        poll with wait_audio()."""
        if not voice:
            raise ValueError("voice is required")
        fields = {"text": text, "voice": voice,
                  "translate": str(translate), "boost_similarity": str(boost_similarity)}
        if language is not None:
            fields["lang"] = language
        if language_code:
            fields["langCode"] = language_code
        if project_id is not None:
            fields["project_id"] = str(project_id)
        r = self.post("/voice_clone/create_audio", fields)
        uuid = r.get("uuid") or r.get("id")
        if not uuid:
            raise RuntimeError(f"create_audio rejected: {r}")
        return {"uuid": uuid, "response": r}

    _AUDIO_DONE = {"completed", "done", "finished", "success"}

    def audio_status(self, uuid):
        return self.get(f"/voice_clone/status/{uuid}")

    def audio_done(self, uuid):
        """True when the TTS job carries a mediaUrl / terminal success status.

        NOTE: /voice_clone/status/<uuid> is NOT a reliable completion signal
        for TTS — it can return {"success":false,"status":"","data":[]} even
        after the audio is done (completion normally arrives over WebSocket).
        Use wait_audio(), which verifies via /voice_clone/generated_audio.
        """
        s = self.audio_status(uuid)
        if s.get("mediaUrl") or s.get("mediaId"):
            return s
        return str(s.get("status", "")).lower() in self._AUDIO_DONE

    def generated_audio(self, page=1, per_page=50, type_="audio", query=""):
        """List generated/cloned audio items (id, uuid, src, length, title...)."""
        r = self.get(f"/voice_clone/generated_audio?type={type_}"
                     f"&per_page={per_page}&page={page}&query={query}")
        if isinstance(r, list):
            return r
        if isinstance(r, dict):
            for key in ("data", "results", "items"):
                if isinstance(r.get(key), list):
                    return r[key]
        return []

    def find_audio(self, uuid, max_pages=5, per_page=50):
        """Find a generated audio item by uuid (paginated, newest first)."""
        for page in range(1, max_pages + 1):
            for item in self.generated_audio(page=page, per_page=per_page):
                if str(item.get("uuid") or "") == str(uuid):
                    return item
        return None

    @staticmethod
    def _audio_handle(uuid, item):
        return {"uuid": uuid, "media_id": item.get("id"), "src": item.get("src"),
                "length": item.get("length"), "title": item.get("title"),
                "status": item.get("status")}

    def wait_audio(self, uuid, timeout_s=600):
        """Wait for TTS completion and return the real audio handle.

        Completion is verified by polling /voice_clone/generated_audio
        (paginated, match by uuid) — the HTTP /voice_clone/status/<uuid>
        endpoint is unreliable for TTS (it can stay empty even after the
        audio completes, because completion normally arrives over
        WebSocket). The status endpoint is only consulted as a fallback.
        Never re-POSTs create_audio; on timeout it raises TimeoutError.
        """
        def check():
            item = self.find_audio(uuid)
            if item is not None:
                return self._audio_handle(uuid, item)
            s = self.audio_status(uuid)  # fallback only
            if s.get("mediaUrl") or s.get("mediaId") or \
                    str(s.get("status", "")).lower() in self._AUDIO_DONE:
                return {"uuid": uuid, "media_id": s.get("mediaId"),
                        "src": s.get("mediaUrl"), "length": s.get("length"),
                        "title": s.get("title"), "status": s.get("status")}
            return None

        return self.poll(check, lambda v: bool(v),
                         timeout_s, interval=3, label=f"tts {uuid[:8]}")

    def import_generated_audio(self, items):
        """Import generated audio into the user library.

        items: [{id, uuid, src, title}] as returned by generated_audio().
        Fire ONCE per batch (write-once rule).
        """
        payload = [{"id": it.get("id"), "uuid": it.get("uuid"),
                    "src": it.get("src"), "title": it.get("title")}
                   for it in items]
        return self.post("/voice_clone/generated_audio_import", json_body=payload)

    def create_sound(self, prompt, duration=10, media_id="0"):
        """AI sound/music generation; result URL arrives over WebSocket, so the
        response handle is returned for later library verification. Fire ONCE."""
        r = self.post("/ai/api/create_sound", {
            "prompt": prompt, "duration": str(duration), "mediaId": media_id})
        if not r.get("success") and not (r.get("uuid") or r.get("id")):
            raise RuntimeError(f"create_sound rejected: {r}")
        return r

    def save_sound(self, uuid):
        """Save generated sound into My AI Audio. Fire ONCE."""
        r = self.post("/ai/api/save_sound", {"uuid": uuid})
        if not r.get("success"):
            raise RuntimeError(f"save_sound rejected: {r}")
        return r
