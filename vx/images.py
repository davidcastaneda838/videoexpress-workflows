"""Image generation: plain, character-consistent, prompt extension."""
from .http import PREVIEW


class ImagesMixin:
    def generate_image(self, prompt, type_="photorealistic", aspect="9:16", enhance_prompt=0):
        """Plain text-to-image. Fire ONCE. Returns the job uuid;
        the image lands at PREVIEW/<uuid>.jpg."""
        r = self.post("/ai/api/generate_image", {
            "prompt": prompt, "enhancePrompt": str(enhance_prompt), "type": type_,
            "uuid": "", "mediaId": "0", "seed": "", "aspect": aspect,
            "generatorName": "create_from_prompt"})
        if not r.get("success"):
            raise RuntimeError(f"image gen rejected: {r}")
        return {"uuid": r["uuid"], "url": self.image_url(r["uuid"])}

    def generate_image_consistent(self, prompt, ref_media_id, aspect="9:16"):
        """Character-consistent image from a reference media item. Fire ONCE."""
        r = self.post("/ai/api/generate_image_consistent_character", {
            "prompt": prompt, "type": "human", "mediaId": ref_media_id,
            "aspect": aspect, "generatorName": "create_from_prompt"})
        if not r.get("success"):
            raise RuntimeError(f"image gen rejected: {r}")
        return {"uuid": r["uuid"], "url": self.image_url(r["uuid"])}

    def image_url(self, job_uuid):
        return f"{PREVIEW}/{job_uuid}.jpg"

    def wait_image(self, job_uuid, timeout_s=900):
        """Image is ready when its preview URL answers 200."""
        return self.poll(lambda: self.head_ok(self.image_url(job_uuid)),
                         lambda ok: ok, timeout_s, interval=20,
                         label=f"image {job_uuid[:8]}")

    def image_ready(self, job_uuid):
        return self.head_ok(self.image_url(job_uuid))

    def save_generated_image(self, job_uuid):
        """Save a generated image into My AI Images (generation alone never
        creates a library item). Fire ONCE."""
        r = self.post("/ai/api/save_generated_image", {
            "uuid": job_uuid, "isShared": "0", "generatorName": "create_from_prompt"})
        if not r.get("success"):
            raise RuntimeError(f"save_generated_image rejected: {r}")
        return r

    def extend_prompt(self, prompt, mode="image", type_=None, style=None):
        """AI prompt enhancer; mode in image|text_to_video|consistent_character|
        video|magic|image_to_prompt."""
        fields = {"prompt": prompt}
        if type_:
            fields["type"] = type_
        if style:
            fields["style"] = style
        r = self.post(f"/ai/api/extend_prompt/{mode}", fields)
        if not r.get("prompt"):
            raise RuntimeError(f"extend_prompt rejected: {r}")
        return r["prompt"]
