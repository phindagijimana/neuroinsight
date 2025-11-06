"""
Metric service for managing hippocampal volumetric measurements.

This service provides business logic for creating and retrieving
hippocampal asymmetry metrics.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from backend.core.logging import get_logger
from backend.models import Metric
from backend.schemas import MetricCreate

logger = get_logger(__name__)


class MetricService:
    """
    Service class for metric-related operations.
    
    Handles CRUD operations for hippocampal volumetric metrics.
    """
    
    @staticmethod
    def create_metric(db: Session, metric_data: MetricCreate) -> Metric:
        """
        Create a new metric.
        
        Args:
            db: Database session
            metric_data: Metric creation data
        
        Returns:
            Created metric instance
        """
        metric = Metric(
            job_id=metric_data.job_id,
            region=metric_data.region,
            left_volume=metric_data.left_volume,
            right_volume=metric_data.right_volume,
            asymmetry_index=metric_data.asymmetry_index,
        )
        
        db.add(metric)
        db.commit()
        db.refresh(metric)
        
        logger.info(
            "metric_created",
            metric_id=str(metric.id),
            job_id=str(metric.job_id),
            region=metric.region,
            asymmetry_index=metric.asymmetry_index,
        )
        
        return metric
    
    @staticmethod
    def create_metrics_bulk(
        db: Session,
        metrics_data: List[MetricCreate]
    ) -> List[Metric]:
        """
        Create multiple metrics in bulk.
        
        Args:
            db: Database session
            metrics_data: List of metric creation data
        
        Returns:
            List of created metric instances
        """
        metrics = [
            Metric(
                job_id=data.job_id,
                region=data.region,
                left_volume=data.left_volume,
                right_volume=data.right_volume,
                asymmetry_index=data.asymmetry_index,
            )
            for data in metrics_data
        ]
        
        db.add_all(metrics)
        db.commit()
        
        for metric in metrics:
            db.refresh(metric)
        
        logger.info(
            "metrics_created_bulk",
            count=len(metrics),
            job_id=str(metrics[0].job_id) if metrics else None,
        )
        
        return metrics
    
    @staticmethod
    def get_metric(db: Session, metric_id: UUID) -> Optional[Metric]:
        """
        Retrieve a metric by ID.
        
        Args:
            db: Database session
            metric_id: Metric identifier
        
        Returns:
            Metric instance if found, None otherwise
        """
        return db.query(Metric).filter(Metric.id == metric_id).first()
    
    @staticmethod
    def get_metrics_by_job(db: Session, job_id: UUID) -> List[Metric]:
        """
        Retrieve all metrics for a specific job.
        
        Args:
            db: Database session
            job_id: Job identifier
        
        Returns:
            List of metric instances
        """
        return db.query(Metric).filter(Metric.job_id == job_id).all()
    
    @staticmethod
    def get_metrics_by_region(db: Session, region: str) -> List[Metric]:
        """
        Retrieve all metrics for a specific hippocampal region.
        
        Args:
            db: Database session
            region: Hippocampal subregion name
        
        Returns:
            List of metric instances
        """
        return db.query(Metric).filter(Metric.region == region).all()

