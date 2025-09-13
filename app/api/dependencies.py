from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app.business.detection import DetectionManager
from app.business.entity import EntityManager
from app.business.entity_media_gallery import EntityMediaGalleryManager
from app.business.healthcheck import HealthcheckManager
from app.business.segment_detection import SegmentDetectionManager
from app.business.taxonomy import TaxonomyManager
from app.business.video import VideoManager
from app.core.config import settings


class ManagerFactory:

    """
    A factory class to handle the business managers instantiation.
    """

    @staticmethod
    def for_healthchecks() -> HealthcheckManager:
        """
        Build an instance of HealthcheckManager to inject
        as a dependency in the endpoints.

        Returns:
            An instance of HealthcheckManager.
        """

        return HealthcheckManager()

    @staticmethod
    def for_video(
        token: str = Depends(APIKeyHeader(name=settings.AUTH_HEADER_KEY)),
    ) -> VideoManager:
        """
        Build an instance of VideoManager to inject
        as a dependency in the endpoints.

        Returns:
            An instance of VideosManager.
        """

        if token != settings.AUTH_SECRET_KEY:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return VideoManager()

    @staticmethod
    def for_taxonomy(
        token: str = Depends(APIKeyHeader(name=settings.AUTH_HEADER_KEY)),
    ) -> TaxonomyManager:
        """
        Build an instance of TaxonomyManager to inject
        as a dependency in the endpoints.

        Returns:
            An instance of TaxonomyManager.
        """

        if token != settings.AUTH_SECRET_KEY:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return TaxonomyManager()

    @staticmethod
    def for_entity(
        token: str = Depends(APIKeyHeader(name=settings.AUTH_HEADER_KEY)),
    ) -> EntityManager:
        """
        Build an instance of EntityManager to inject
        as a dependency in the endpoints.

        Returns:
            An instance of EntityManager.
        """

        if token != settings.AUTH_SECRET_KEY:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return EntityManager()

    @staticmethod
    def for_entity_media_gallery(
        token: str = Depends(APIKeyHeader(name=settings.AUTH_HEADER_KEY)),
    ) -> EntityMediaGalleryManager:
        """
        Build an instance of EntityMediaGalleryManager to inject
        as a dependency in the endpoints.

        Returns:
            An instance of EntityMediaGalleryManager.
        """

        if token != settings.AUTH_SECRET_KEY:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return EntityMediaGalleryManager()

    @staticmethod
    def for_segment_detection(
        token: str = Depends(APIKeyHeader(name=settings.AUTH_HEADER_KEY)),
    ) -> SegmentDetectionManager:
        """
        Build an instance of SegmentDetectionManager to inject
        as a dependency in the endpoints.

        Returns:
            An instance of SegmentDetectionManager.
        """

        if token != settings.AUTH_SECRET_KEY:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return SegmentDetectionManager()

    @staticmethod
    def for_detection(
        token: str = Depends(APIKeyHeader(name=settings.AUTH_HEADER_KEY)),
    ) -> DetectionManager:
        """
        Build an instance of DetectionManager to inject
        as a dependency in the endpoints.

        Returns:
            An instance of DetectionManager.
        """

        if token != settings.AUTH_SECRET_KEY:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        return DetectionManager()
