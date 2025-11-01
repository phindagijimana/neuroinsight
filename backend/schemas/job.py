"""
Pydantic schemas for Job-related API operations.

These schemas define the structure and validation rules for
job-related API requests and responses.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    """Job status enumeration for API."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobCreate(BaseModel):
    """
    Schema for creating a new job.
    
    Used when uploading a new MRI file for processing.
    """
    
    filename: str = Field(
        ...,
        description="Original filename of the MRI scan",
        example="patient_001_T1w.nii.gz"
    )
    
    file_path: Optional[str] = Field(
        None,
        description="Storage path for the uploaded file",
        example="/data/uploads/patient_001_T1w.nii.gz"
    )


class JobUpdate(BaseModel):
    """
    Schema for updating an existing job.
    
    Used to update job status and related fields during processing.
    """
    
    status: Optional[JobStatus] = Field(
        None,
        description="Updated job status"
    )
    
    error_message: Optional[str] = Field(
        None,
        description="Error message if job failed"
    )
    
    started_at: Optional[datetime] = Field(
        None,
        description="Timestamp when processing started"
    )
    
    completed_at: Optional[datetime] = Field(
        None,
        description="Timestamp when processing completed"
    )
    
    result_path: Optional[str] = Field(
        None,
        description="Path to processing output directory"
    )


class MetricSummary(BaseModel):
    """
    Simplified metric schema for job responses.
    
    Includes key volumetric data without full metric details.
    """
    
    id: UUID
    region: str
    left_volume: float
    right_volume: float
    asymmetry_index: float
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True


class JobResponse(BaseModel):
    """
    Schema for job API responses.
    
    Includes all job details and associated metrics.
    """
    
    id: UUID = Field(
        ...,
        description="Unique job identifier"
    )
    
    filename: str = Field(
        ...,
        description="Original filename"
    )
    
    file_path: Optional[str] = Field(
        None,
        description="Storage path"
    )
    
    status: JobStatus = Field(
        ...,
        description="Current processing status"
    )
    
    error_message: Optional[str] = Field(
        None,
        description="Error details if failed"
    )
    
    created_at: datetime = Field(
        ...,
        description="Job creation timestamp"
    )
    
    started_at: Optional[datetime] = Field(
        None,
        description="Processing start timestamp"
    )
    
    completed_at: Optional[datetime] = Field(
        None,
        description="Processing completion timestamp"
    )
    
    result_path: Optional[str] = Field(
        None,
        description="Output directory path"
    )
    
    metrics: List[MetricSummary] = Field(
        default=[],
        description="Associated hippocampal metrics"
    )
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True

