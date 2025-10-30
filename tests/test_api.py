"""
Tests for the High School Management System API endpoints.
"""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """Test that root endpoint redirects to static/index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that we have the expected activities
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class", 
            "Soccer Team", "Basketball Club", "Art Workshop",
            "Drama Club", "Math Olympiad", "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in data
            
        # Check structure of an activity
        chess_club = data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)
        
    def test_get_activities_has_correct_data_types(self, client, reset_activities):
        """Test that activities have correct data types."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
            
            for participant in activity_data["participants"]:
                assert isinstance(participant, str)
                assert "@" in participant  # Basic email validation


class TestSignupEndpoint:
    """Tests for the signup endpoint."""
    
    def test_signup_for_existing_activity_success(self, client, reset_activities):
        """Test successful signup for an existing activity."""
        email = "newstudent@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity}"
        
        # Verify the participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
    def test_signup_for_nonexistent_activity_fails(self, client, reset_activities):
        """Test signup for an activity that doesn't exist."""
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
        
    def test_signup_already_registered_fails(self, client, reset_activities):
        """Test that signing up twice for the same activity fails."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is already signed up"
        
    def test_signup_with_special_characters_in_activity_name(self, client, reset_activities):
        """Test signup with URL encoding for activity names."""
        # Add a test activity with special characters to the activities dict
        from app import activities
        activities["Test & Special Club"] = {
            "description": "Test club with special characters",
            "schedule": "Test schedule",
            "max_participants": 10,
            "participants": []
        }
        
        email = "student@mergington.edu"
        activity = "Test & Special Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
    def test_signup_with_special_characters_in_email(self, client, reset_activities):
        """Test signup with special characters in email."""
        email = "test+user@mergington.edu"
        activity = "Chess Club"
        
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200


class TestRemoveEndpoint:
    """Tests for the remove participant endpoint."""
    
    def test_remove_participant_success(self, client, reset_activities):
        """Test successful removal of a participant."""
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"
        
        # Verify participant is initially in the activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        
        # Remove the participant
        response = client.delete(f"/activities/{activity}/remove?email={email}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == f"Removed {email} from {activity}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
        
    def test_remove_from_nonexistent_activity_fails(self, client, reset_activities):
        """Test removal from an activity that doesn't exist."""
        email = "student@mergington.edu"
        activity = "Nonexistent Club"
        
        response = client.delete(f"/activities/{activity}/remove?email={email}")
        assert response.status_code == 404
        
        data = response.json()
        assert data["detail"] == "Activity not found"
        
    def test_remove_unregistered_participant_fails(self, client, reset_activities):
        """Test removal of a participant who isn't registered."""
        email = "unregistered@mergington.edu"
        activity = "Chess Club"
        
        response = client.delete(f"/activities/{activity}/remove?email={email}")
        assert response.status_code == 400
        
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"
        
    def test_remove_all_participants_from_activity(self, client, reset_activities):
        """Test removing all participants from an activity."""
        activity = "Chess Club"
        
        # Get initial participants
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        initial_participants = activities_data[activity]["participants"].copy()
        
        # Remove all participants
        for email in initial_participants:
            response = client.delete(f"/activities/{activity}/remove?email={email}")
            assert response.status_code == 200
            
        # Verify all participants were removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert len(activities_data[activity]["participants"]) == 0


class TestIntegrationScenarios:
    """Integration tests for complete user workflows."""
    
    def test_signup_and_remove_workflow(self, client, reset_activities):
        """Test complete signup and removal workflow."""
        email = "workflow@mergington.edu"
        activity = "Programming Class"
        
        # Initial state - participant not in activity
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
        initial_count = len(activities_data[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Verify signup
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity]["participants"]
        assert len(activities_data[activity]["participants"]) == initial_count + 1
        
        # Remove participant
        remove_response = client.delete(f"/activities/{activity}/remove?email={email}")
        assert remove_response.status_code == 200
        
        # Verify removal
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity]["participants"]
        assert len(activities_data[activity]["participants"]) == initial_count
        
    def test_multiple_activities_signup(self, client, reset_activities):
        """Test signing up for multiple activities."""
        email = "multi@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Workshop"]
        
        for activity in activities_to_join:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
            
        # Verify participant is in all activities
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        
        for activity in activities_to_join:
            assert email in activities_data[activity]["participants"]