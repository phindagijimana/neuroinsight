"""
Job model for tracking MRI processing jobs.

This model stores information about uploaded MRI scans and their
processing status throughout the pipeline.
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.database import Base


class JobStatus(PyEnum):
    """Enumeration of possible job statuses."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(Base):
    """
    Job model representing an MRI processing task.
    
    Attributes:
        id: Unique job identifier
        filename: Original filename of uploaded MRI
        file_path: Path to stored file (local or S3)
        status: Current processing status
        error_message: Error details if job failed
        created_at: Timestamp when job was created
        started_at: Timestamp when processing started
        completed_at: Timestamp when processing completed
        result_path: Path to processing output directory
        metrics: Related hippocampal metrics
    """
    
    __tablename__ = "jobs"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique job identifier"
    )
    
    # File information
    filename = Column(
        String(255),
        nullable=False,
        doc="Original filename of uploaded MRI scan"
    )
    
    file_path = Column(
        Text,
        nullable=True,
        doc="Storage path (local filesystem or S3 URI)"
    )
    
    # Status tracking
    status = Column(
        Enum(JobStatus),
        nullable=False,
        default=JobStatus.PENDING,
        index=True,
        doc="Current processing status"
    )
    
    progress = Column(
        Integer,
        nullable=False,
        default=0,
        doc="Processing progress percentage (0-100)"
    )
    
    current_step = Column(
        String(255),
        nullable=True,
        doc="Current processing step description"
    )
    
    error_message = Column(
        Text,
        nullable=True,
        doc="Error details if job failed"
    )
    
    # Timestamps
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
        doc="Job creation timestamp"
    )
    
    started_at = Column(
        DateTime,
        nullable=True,
        doc="Processing start timestamp"
    )
    
    completed_at = Column(
        DateTime,
        nullable=True,
        doc="Processing completion timestamp"
    )
    
    # Results
    result_path = Column(
        Text,
        nullable=True,
        doc="Path to processing output directory"
    )
    
    # Relationships
    metrics = relationship(
        "Metric",
        back_populates="job",
        cascade="all, delete-orphan",
        doc="Associated hippocampal metrics"
    )
    
    def __repr__(self) -> str:
        """String representation of Job."""
        return f"<Job(id={self.id}, filename={self.filename}, status={self.status.value})>"
    
    @property
    def is_complete(self) -> bool:
        """Check if job has completed processing."""
        return self.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED)
    
    @property
    def is_active(self) -> bool:
        """Check if job is currently processing or waiting to start."""
        return self.status in (JobStatus.PENDING, JobStatus.RUNNING)
    
    @property
    def duration_seconds(self) -> float:
        """Calculate processing duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0

