"""
Tests for GET /activities and POST /signup endpoints.
"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_success(self, client_with_test_data):
        """
        Test that GET /activities returns 200 and all activities.
        """
        response = client_with_test_data.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all test activities are present
        assert "Test Activity 1" in data
        assert "Test Activity 2" in data
        assert "Test Activity 3" in data
        assert len(data) == 3

    def test_get_activities_response_format(self, client_with_test_data):
        """
        Test that each activity has the correct structure with required fields.
        """
        response = client_with_test_data.get("/activities")
        data = response.json()
        
        # Check first activity structure
        activity = data["Test Activity 1"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        
        # Verify types
        assert isinstance(activity["description"], str)
        assert isinstance(activity["schedule"], str)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["participants"], list)
        
        # Verify participants are strings (emails)
        for participant in activity["participants"]:
            assert isinstance(participant, str)

    def test_get_activities_with_participants(self, client_with_test_data):
        """
        Test that activities with participants return correct participant list.
        """
        response = client_with_test_data.get("/activities")
        data = response.json()
        
        activity = data["Test Activity 1"]
        assert len(activity["participants"]) == 2
        assert "alice@test.edu" in activity["participants"]
        assert "bob@test.edu" in activity["participants"]

    def test_get_activities_without_participants(self, client_with_test_data):
        """
        Test that activities without participants return empty list.
        """
        response = client_with_test_data.get("/activities")
        data = response.json()
        
        activity = data["Test Activity 3"]
        assert len(activity["participants"]) == 0
        assert activity["participants"] == []


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client_with_test_data):
        """
        Test that a student can successfully sign up for an activity with available spots.
        """
        response = client_with_test_data.post(
            "/activities/Test Activity 2/signup?email=newstudent@test.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@test.edu" in data["message"]
        assert "Test Activity 2" in data["message"]
        
        # Verify participant was added
        activities_response = client_with_test_data.get("/activities")
        activities = activities_response.json()
        assert "newstudent@test.edu" in activities["Test Activity 2"]["participants"]

    def test_signup_duplicate_prevention(self, client_with_test_data):
        """
        Test that a student cannot sign up twice for the same activity.
        """
        # First signup should succeed
        response1 = client_with_test_data.post(
            "/activities/Test Activity 3/signup?email=duplicate@test.edu"
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client_with_test_data.post(
            "/activities/Test Activity 3/signup?email=duplicate@test.edu"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_invalid_activity(self, client_with_test_data):
        """
        Test that signing up for a non-existent activity returns 404.
        """
        response = client_with_test_data.post(
            "/activities/Nonexistent Activity/signup?email=student@test.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_signup_max_participants_validation(self, client_with_test_data):
        """
        Test that a student cannot sign up if the activity is at max capacity.
        Test Activity 1 has max=2 and already has 2 participants.
        """
        # Activity 1 is full (2/2 participants)
        response = client_with_test_data.post(
            "/activities/Test Activity 1/signup?email=newstudent@test.edu"
        )
        
        # Should fail because activity is at max capacity
        assert response.status_code == 400
        data = response.json()
        # Error could be about being full or reaching max
        assert "max" in data["detail"].lower() or "full" in data["detail"].lower() \
               or "cannot" in data["detail"].lower()

    def test_signup_multiple_students(self, client_with_test_data):
        """
        Test that multiple different students can sign up for the same activity.
        """
        # Sign up first student
        response1 = client_with_test_data.post(
            "/activities/Test Activity 3/signup?email=student1@test.edu"
        )
        assert response1.status_code == 200
        
        # Sign up second student
        response2 = client_with_test_data.post(
            "/activities/Test Activity 3/signup?email=student2@test.edu"
        )
        assert response2.status_code == 200
        
        # Verify both are in participants
        activities_response = client_with_test_data.get("/activities")
        participants = activities_response.json()["Test Activity 3"]["participants"]
        assert "student1@test.edu" in participants
        assert "student2@test.edu" in participants
        assert len(participants) == 2

    def test_signup_email_formats(self, client_with_test_data):
        """
        Test that signup accepts various email formats.
        """
        test_emails = [
            "simple@test.edu",
            "with.dot@test.edu",
            "with+plus@test.edu",
            "123numbers@test.edu",
        ]
        
        for email in test_emails:
            # Each email should not be in initial data
            response = client_with_test_data.post(
                f"/activities/Test Activity 3/signup?email={email}"
            )
            # First attempt should succeed
            assert response.status_code == 200, f"Failed for email: {email}"

    def test_signup_with_encoded_activity_name(self, client_with_test_data):
        """
        Test that signup works with URL-encoded activity names (with spaces).
        """
        response = client_with_test_data.post(
            "/activities/Test%20Activity%202/signup?email=encoded@test.edu"
        )
        
        assert response.status_code == 200
        activities_response = client_with_test_data.get("/activities")
        activities = activities_response.json()
        assert "encoded@test.edu" in activities["Test Activity 2"]["participants"]
