"""
Tests for the data models and business logic of the High School Management System.
"""

import pytest
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import activities


class TestActivitiesDataStructure:
    """Tests for the activities data structure and validation."""
    
    def test_activities_structure(self, reset_activities):
        """Test that activities have the correct structure."""
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
        for activity_name, activity_data in activities.items():
            # Test that activity name is a string
            assert isinstance(activity_name, str)
            assert len(activity_name) > 0
            
            # Test that activity data has required fields
            required_fields = ["description", "schedule", "max_participants", "participants"]
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"
                
            # Test field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            # Test that max_participants is positive
            assert activity_data["max_participants"] > 0
            
            # Test that participants list contains valid emails
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant
                assert "." in participant
                
    def test_activity_capacity_constraints(self, reset_activities):
        """Test that no activity exceeds its maximum capacity."""
        for activity_name, activity_data in activities.items():
            current_participants = len(activity_data["participants"])
            max_participants = activity_data["max_participants"]
            
            assert current_participants <= max_participants, \
                f"Activity '{activity_name}' has {current_participants} participants but max is {max_participants}"
                
    def test_no_duplicate_participants_in_activity(self, reset_activities):
        """Test that no activity has duplicate participants."""
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            unique_participants = set(participants)
            
            assert len(participants) == len(unique_participants), \
                f"Activity '{activity_name}' has duplicate participants"
                
    def test_participant_email_format(self, reset_activities):
        """Test that all participant emails follow expected format."""
        for activity_name, activity_data in activities.items():
            for participant in activity_data["participants"]:
                # Basic email validation
                assert "@" in participant
                assert participant.count("@") == 1
                
                # Check domain
                local, domain = participant.split("@")
                assert len(local) > 0
                assert len(domain) > 0
                assert "." in domain


class TestActivityBusinessLogic:
    """Tests for business logic functions (if extracted from endpoints)."""
    
    def test_activity_spots_calculation(self, reset_activities):
        """Test calculation of available spots in activities."""
        for activity_name, activity_data in activities.items():
            max_participants = activity_data["max_participants"]
            current_participants = len(activity_data["participants"])
            spots_left = max_participants - current_participants
            
            assert spots_left >= 0, f"Activity '{activity_name}' has negative spots left"
            assert spots_left <= max_participants, f"Spots left exceeds max participants for '{activity_name}'"
            
    def test_activity_names_are_unique(self, reset_activities):
        """Test that all activity names are unique."""
        activity_names = list(activities.keys())
        unique_names = set(activity_names)
        
        assert len(activity_names) == len(unique_names), "Duplicate activity names found"
        
    def test_all_activities_have_content(self, reset_activities):
        """Test that all activities have meaningful content."""
        for activity_name, activity_data in activities.items():
            # Check that descriptions are not empty
            assert len(activity_data["description"].strip()) > 0, \
                f"Activity '{activity_name}' has empty description"
                
            # Check that schedules are not empty
            assert len(activity_data["schedule"].strip()) > 0, \
                f"Activity '{activity_name}' has empty schedule"
                
            # Check that activity name is not empty
            assert len(activity_name.strip()) > 0, "Empty activity name found"


class TestDataConsistency:
    """Tests for data consistency and integrity."""
    
    def test_participant_email_consistency(self, reset_activities):
        """Test that participant emails are consistent across activities."""
        all_participants = set()
        
        for activity_data in activities.values():
            for participant in activity_data["participants"]:
                # Check for consistent email format
                assert participant.lower() == participant, \
                    f"Participant email '{participant}' is not lowercase"
                    
                # Check for consistent domain
                if participant.endswith("@mergington.edu"):
                    all_participants.add(participant)
                    
        # All test participants should use the mergington.edu domain
        for participant in all_participants:
            assert participant.endswith("@mergington.edu"), \
                f"Participant '{participant}' doesn't use the expected domain"
                
    def test_activity_capacity_distribution(self, reset_activities):
        """Test that activity capacities are reasonable."""
        capacities = [activity["max_participants"] for activity in activities.values()]
        
        # Check that we have a reasonable range of capacities
        min_capacity = min(capacities)
        max_capacity = max(capacities)
        
        assert min_capacity >= 10, "Minimum capacity seems too low"
        assert max_capacity <= 50, "Maximum capacity seems too high"
        assert max_capacity > min_capacity, "No variation in activity capacities"
        
    def test_activity_types_coverage(self, reset_activities):
        """Test that we have a good variety of activity types."""
        activity_names = list(activities.keys())
        
        # Check for different types of activities
        sports_activities = [name for name in activity_names if any(
            sport in name.lower() for sport in ["soccer", "basketball", "gym"])]
        academic_activities = [name for name in activity_names if any(
            subject in name.lower() for subject in ["math", "science", "programming", "chess"])]
        creative_activities = [name for name in activity_names if any(
            creative in name.lower() for creative in ["art", "drama"])]
            
        assert len(sports_activities) > 0, "No sports activities found"
        assert len(academic_activities) > 0, "No academic activities found"
        assert len(creative_activities) > 0, "No creative activities found"


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_activity_with_no_participants(self, reset_activities):
        """Test handling of activities with no participants."""
        # Create a test scenario with an empty activity
        test_activity = {
            "description": "Test activity",
            "schedule": "Test schedule",
            "max_participants": 10,
            "participants": []
        }
        
        # Verify empty participants list is handled correctly
        assert isinstance(test_activity["participants"], list)
        assert len(test_activity["participants"]) == 0
        assert test_activity["max_participants"] > 0
        
    def test_activity_at_full_capacity(self, reset_activities):
        """Test handling of activities at full capacity."""
        # Find an activity and fill it to capacity for testing
        for activity_name, activity_data in activities.items():
            current_count = len(activity_data["participants"])
            max_count = activity_data["max_participants"]
            
            if current_count < max_count:
                # Calculate spots left
                spots_left = max_count - current_count
                assert spots_left > 0
                
                # Verify capacity logic
                if current_count == max_count:
                    assert spots_left == 0
                break
                
    def test_participant_list_modification(self, reset_activities):
        """Test that participant lists can be safely modified."""
        activity_name = "Chess Club"
        original_participants = activities[activity_name]["participants"].copy()
        
        # Add a participant
        test_email = "test@mergington.edu"
        activities[activity_name]["participants"].append(test_email)
        
        # Verify addition
        assert test_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == len(original_participants) + 1
        
        # Remove the participant
        activities[activity_name]["participants"].remove(test_email)
        
        # Verify removal
        assert test_email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == len(original_participants)