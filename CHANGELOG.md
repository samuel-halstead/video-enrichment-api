# Changelog

## [0.1.0] - Unreleased

### Added

- Initialize repo
- Video GET /video
- Video GET /video/{video_uuid}
- Video POST /video (file upload with metadata extraction)
- Video GET /video/{video_uuid}/thumbnail
- Video GET /video/{video_uuid}/bytes
- Video DELETE /video/{video_uuid}
- Taxonomy GET /taxonomy
- Taxonomy GET /taxonomy/{taxonomy_uuid}
- Taxonomy POST /taxonomy
- Taxonomy PUT /taxonomy/{taxonomy_uuid}
- Taxonomy DELETE /taxonomy/{taxonomy_uuid}
- Entity GET /entity
- Entity GET /entity/{entity_uuid}
- Entity GET /entity/by-taxonomy/{taxonomy_id}
- Entity POST /entity
- Entity PUT /entity/{entity_uuid}
- Entity DELETE /entity/{entity_uuid}
- Entity Media Gallery GET /entity-media-gallery
- Entity Media Gallery GET /entity-media-gallery/{media_gallery_uuid}
- Entity Media Gallery GET /entity-media-gallery/by-entity/{entity_id}
- Entity Media Gallery POST /entity-media-gallery
- Entity Media Gallery PUT /entity-media-gallery/{media_gallery_uuid}
- Entity Media Gallery DELETE /entity-media-gallery/{media_gallery_uuid}
- Segment Detection GET /segment-detection/by-video/{video_id}
- Segment Detection GET /segment-detection/by-video/{video_id}/taxonomy/{taxonomy_id}
- Detection GET /detection/by-video/{video_id}
- Detection GET /detection/by-segment-detection/{segment_detection_id}
- Healthcheck GET /healthcheck

### Changed

- Video POST /video now accepts file uploads instead of JSON data
- Video upload automatically extracts metadata (frames, frame_rate, length, extension)
- Video upload automatically generates and stores thumbnails in S3
- Video upload stores files in S3_VIDEO_PATH/{video_uuid}/ structure
