"""
Unit tests for asymmetry calculation utilities.

Tests the core asymmetry index computation and related functions.
"""

import pytest
from pipeline.utils.asymmetry import (
    calculate_asymmetry_index,
    classify_laterality,
    calculate_percent_difference,
    calculate_volume_ratio,
)


class TestAsymmetryIndex:
    """Tests for asymmetry index calculation."""
    
    def test_left_larger_than_right(self):
        """Test when left hemisphere is larger."""
        ai = calculate_asymmetry_index(1250, 1200)
        assert ai > 0
        assert abs(ai - 0.0408) < 0.001
    
    def test_right_larger_than_left(self):
        """Test when right hemisphere is larger."""
        ai = calculate_asymmetry_index(1200, 1250)
        assert ai < 0
        assert abs(ai - (-0.0408)) < 0.001
    
    def test_symmetric_volumes(self):
        """Test when volumes are equal."""
        ai = calculate_asymmetry_index(1000, 1000)
        assert ai == 0.0
    
    def test_zero_volumes(self):
        """Test edge case with zero volumes."""
        ai = calculate_asymmetry_index(0, 0)
        assert ai == 0.0


class TestLateralityClassification:
    """Tests for laterality classification."""
    
    def test_left_dominant(self):
        """Test left-dominant classification."""
        result = classify_laterality(0.10)
        assert result == "Left > Right"
    
    def test_right_dominant(self):
        """Test right-dominant classification."""
        result = classify_laterality(-0.10)
        assert result == "Right > Left"
    
    def test_symmetric(self):
        """Test symmetric classification."""
        result = classify_laterality(0.02)
        assert result == "Symmetric"
    
    def test_custom_threshold(self):
        """Test with custom threshold."""
        result = classify_laterality(0.03, threshold=0.02)
        assert result == "Left > Right"


class TestPercentDifference:
    """Tests for percent difference calculation."""
    
    def test_positive_difference(self):
        """Test when left is larger."""
        diff = calculate_percent_difference(1250, 1200)
        assert abs(diff - 4.0) < 0.1
    
    def test_negative_difference(self):
        """Test when right is larger."""
        diff = calculate_percent_difference(1200, 1250)
        assert abs(diff - (-4.17)) < 0.1
    
    def test_zero_left_volume(self):
        """Test edge case with zero left volume."""
        diff = calculate_percent_difference(0, 100)
        assert diff == 0.0


class TestVolumeRatio:
    """Tests for volume ratio calculation."""
    
    def test_left_larger(self):
        """Test when left is larger."""
        ratio = calculate_volume_ratio(1250, 1200)
        assert ratio > 1.0
        assert abs(ratio - 1.042) < 0.01
    
    def test_right_larger(self):
        """Test when right is larger."""
        ratio = calculate_volume_ratio(1200, 1250)
        assert ratio < 1.0
        assert abs(ratio - 0.96) < 0.01
    
    def test_equal_volumes(self):
        """Test when volumes are equal."""
        ratio = calculate_volume_ratio(1000, 1000)
        assert ratio == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

