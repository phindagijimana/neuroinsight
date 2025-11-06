"""
Metric model for storing hippocampal asymmetry measurements.

This model stores volumetric data and computed asymmetry indices
for hippocampal subregions extracted from MRI scans.
"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.database import Base


class Metric(Base):
    """
    Metric model representing hippocampal volumetric measurements.
    
    Attributes:
        id: Unique metric identifier
        job_id: Foreign key to associated job
        region: Hippocampal subregion name
        left_volume: Left hemisphere volume in mm³
        right_volume: Right hemisphere volume in mm³
        asymmetry_index: Computed asymmetry index
        created_at: Timestamp when metric was created
        job: Related job object
    """
    
    __tablename__ = "metrics"
    
    # Primary key
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Unique metric identifier"
    )
    
    # Foreign key
    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="Associated job identifier"
    )
    
    # Region information
    region = Column(
        String(100),
        nullable=False,
        doc="Hippocampal subregion name (e.g., 'CA1', 'CA3', 'subiculum')"
    )
    
    # Volumetric measurements
    left_volume = Column(
        Float,
        nullable=False,
        doc="Left hemisphere volume in cubic millimeters"
    )
    
    right_volume = Column(
        Float,
        nullable=False,
        doc="Right hemisphere volume in cubic millimeters"
    )
    
    asymmetry_index = Column(
        Float,
        nullable=False,
        doc="Computed asymmetry index: (L - R) / (L + R)"
    )
    
    # Timestamp
    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        doc="Metric creation timestamp"
    )
    
    # Relationships
    job = relationship(
        "Job",
        back_populates="metrics",
        doc="Associated job"
    )
    
    def __repr__(self) -> str:
        """String representation of Metric."""
        return (
            f"<Metric(id={self.id}, region={self.region}, "
            f"AI={self.asymmetry_index:.3f})>"
        )
    
    @property
    def total_volume(self) -> float:
        """Calculate total bilateral volume."""
        return self.left_volume + self.right_volume
    
    @property
    def laterality(self) -> str:
        """Determine laterality based on asymmetry index."""
        if self.asymmetry_index > 0.05:
            return "Left > Right"
        elif self.asymmetry_index < -0.05:
            return "Right > Left"
        else:
            return "Symmetric"

