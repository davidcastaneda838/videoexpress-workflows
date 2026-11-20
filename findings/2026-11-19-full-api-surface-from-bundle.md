# Full internal API surface extracted from /bundle/js/videoeditor.min.js?24.25

Date: Nov 19 2026. Method: static scan of the 1.93MB editor bundle (scan*.py scripts in repo;
contexts in scan2_out.txt/scan4_out.txt/scan5_out.txt/scan4_ctx.json). All paths relative to
https://app.videoexpress.ai. jQuery $.ajax unless noted; `makeApiRequest(name,data)` = POST
baseUrl+"ai/api/"+name; `ajaxRequest({actionPath,...})` = POST actionPath. Task completion is
delivered via WebSocket (options.wsServerUrl) via createSubscription(uuid) — message is a URL
(artifact) or "Error: ..."; ai/api/status/<uuid> is the HTTP polling fallback.

## AI generation (POST /ai/api/*)
- generate_image — prompt,promptNegative,isHuman,type,style,enhancePrompt,uuid,mediaId,mediaId2,seed,aspect,videoLengthBooster,audioMediaId,speed,generatorName
- generate_image_consistent_character — prompt,type,mediaId/mediaId2,highSimilarity,aspect,generatorName
- generate_image_stylize_character — style,mediaId,aspect,...
- extend_prompt/<mode> (image|text_to_video|consistent_character|video|magic|image_to_prompt) — prompt,type,style
- image2video — (proven) type,imagePrompt,prompt,uuid,mediaId,audioMediaId,isShared,aspect,enhanceHumanFace,isTalkingVideoFromText,isNarrationVideo,enhanceVideoPrompt,videoOnly,speed,generatorName,faceImageMediaId,faceSwap,mode,videoLength,speech1,speech2
- image2video_talking — type,prompt,motion,uuid,mediaId,audioMediaId,isShared,isSingingMode; repair variant {repair:1,mediaId}; faceReplace variant {imageMediaId? mediaId, audioMediaId, type}
- generate_image2video2 — type,mediaId,prompt,videoLengthBooster
- generate_text2video_dialog — prompt,enhanceVideoPrompt,videoLength(dialog mode, actors scripts speech1/speech2)
- create_talking_video — variant A: type,prompt,speed,aspect,uuid,mediaId,audioMediaId,enhanceHumanFace,enhanceVideoPrompt,isShared,isTalkingVideo:1,isSingingMode,isLoopForwardMode,generatorName; variant B: prompt,speed,enhanceVideoPrompt,isSingingMode,audioMediaId,imageMediaId,videoMediaId
- human_background_replace — prompt|promptNegative/backgroundMediaId,title (+mode variants)
- face_swap_image — prompt,promptNegative,type,style,uuid,targetMediaId,sourceMediaId,sourceUuid,isShared,aspect
- inpainting_image — prompt,promptNegative,imageData(canvas dataURL),mediaId,imageUuid,brushColor
- inpainting_video — imageData,mediaId,imageUuid,brushColor
- outpainting_image — prompt,promptNegative,type,mediaId,mediaUrl,aspect
- create_video_object_removal — x1,y1,x2,y2,mediaId
- create_video_special_effects — prompt,promptNegative,imageData,mediaId,brushColor
- create_sound — prompt,duration,mediaId (AI sound effects/music; WS result)
- create_sound_from_video — mediaId,generatorName
- save_sound — uuid
- save_generated_image — uuid,isShared,generatorName
- audio_split (POST JSON) — split audio in cutter
- create_audio_voice_change — referenceAudioId,sourceAudioId,startTime,endTime (voice changer)
- video_length_booster — videoMediaId,generatorName
- voice_recognize — multipart audio blob (speech-to-text voice typing)
- import_from_artistly — JSON {items:[{url,name,data}]}
- cancel/<uuid> (POST), retry/<id> (POST), status/<uuid> (GET ?upd_estimated_time=1),
  get_media_prompt_data/<mediaId> (GET; POST JSON {mode:"redesign"}), get_log_value_by_uid/<uid> (GET),
  result_ai_fix/<fix>/<mediaId> (POST; fix= video_fix_quality | video_fix_quality_v3 | video_fix_physics | video_fix_subtitles),
  locked_message/<ROLE> (GET)

## TTS / voice (CloneVoice)
- voice_clone/languages_list — GET
- voice_clone/voices/<category>?language=<id>&languageCode=<code> — GET (category: system|designed|public_library|cloned)
- voice_clone/create_audio — POST text,lang,langCode,voice,translate(0/1),boost_similarity(0/1),project_id (standard TTS AND clone tab)
- voice_clone/status/<uuid> — GET (poll every 3s)
- voice_clone/generated_audio?type=audio&per_page=20&page=1&query= — GET
- voice_clone/generated_audio_import — POST [{id,uuid,src,title}]
- import/text_to_speech — form action (legacy TTS import)
- import/text_to_speech_talking_video — POST text/voice/lang/speed/pitch/emotion... (talking-photo TTS)
- avatar/import_tts/<avatarId> — avatar wizard TTS step
- avatar/content_tts/<projectId>/<audioDataFileName> — GET saved avatar TTS content
- api/jvzoo_* — billing (admin)

## Library / media
- library/get_categories/<libraryId> (GET; 4=personal)
- api/library/get_media/<libraryId>?categoryId&page&start&limit&query&orderBy&orderDir&filter (GET)
- library/get_media_item/<id> (GET)
- library/upload/<libraryId> (Dropzone POST)
- library/download/<id> (GET redirect), library/download_items (POST form, ids)
- library/edit_item/<id> (POST name), delete_item/<id> (DELETE), delete_items (POST JSON ids)
- library/move_item/<id>, move_items (POST JSON), copy_item/<id>, share_item/<id> (POST)
- library/empty_category/<id> (POST action=start|process&operationId)
- library/add_category/<libraryId>, rename_category/<id> (new_name), delete_category/<id>
- library/extract_audio/<id> (POST name,startTime,endTime), extract_last_frame/<id> (POST name, frame_time_ms)
- library/separate_audio_video/<id> (POST)
- library/feedback/<id> (PATCH JSON rating)
- library/image/<type>?src=&isPrivate=&w=&h=, library/image_timeline/<type>?src=..., library/image/project?src=cover&project_id=
- library/get_scripts/ (GET — script/template picker)

## Project / editor / render
- project/get_list[?search=] (GET), project/open/<id> (GET)
- project/save/<id> (POST title,save_new,data=JSON timeline; data is bricks/tracks JSON)
- project/<id>/save_image/<name> (POST {data}) — save project preview image
- project/upload (Dropzone), project/check_availability (POST {files:[{id}]})
- project/resolve_media (POST {files:[ids]}), project/get_title/<id>?name=&uniqid= (GET title render)
- project/create_work_copy/<id>, project/clean_temp (POST), project/process_stop (GET), project/progress?start=0|1 (GET)
- project/export/<id> (GET — export page), project/slideshow_project/<id> (GET template data),
  project/slideshow_project (POST multipart save slideshow template: name, size, format, categoryId, video-blob/audio-blob)
- render_project/<id|tmp> (POST JSON {options:{name,quality,size,format,aspect,project_id,project_title},data:[tracks]}) — PROVEN
- projects/get_templates_list (GET — slideshow templates)
- api/get_list_output (GET — exports; PROVEN)
- save_media (POST multipart: name,file_name?,categoryId,audio-blob/video-blob,type,project_id — screen recorder output)
- settings (POST name/value e.g. queue_rendering_size)

## Import / stock
- import/youtube/<videoId> — POST {categoryId,title}; poll same URL for {progress}
- import/download_stock_media — POST mediaId,mediaType,mediaTitle (copies stock item into user library)
- api/user_upgrades/my, api/get_profile, api/update_profile, api/api_key_refresh (POST),
  api/update_default_aspect_ratio (POST update_ratio,default_aspect_ratio), api/get_restrictions/<id>,
  api/get_restrictions_by_role/<id>?user_role=, api/user/<id>/daily-restrictions (GET), terms/agree (POST optionKey)

## Notes
- WS completion: every generation endpoint returns {success,uuid}; app opens WebSocket to options.wsServerUrl
  and the final message is the finished asset URL (or "Error: ..."). HTTP fallback: ai/api/status/<uuid>.
- Background removal UI flag (canRemoveBackground) exists but no dedicated endpoint string found in
  this bundle — likely implemented via human_background_replace / inpainting with generated mask.
- CSRF: writes from outside browser historically hit Laravel 419; same-session cookies + X-Requested-With worked in api_run.py.
