"""
Tests for DELETE /activities/{activity_name}/unregister endpoint.
"""

import pytest


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success(self, client_with_test_data):
        """
        Test that a student can successfully unregister from an activity.
        """
        # Verify student is in participants before unregister
        activities_before = client_with_test_data.get("/activities").json()
        assert "alice@test.edu" in activities_before["Test Activity 1"]["participants"]
        
        # Unregister
        response = client_with_test_data.delete(
            "/activities/Test Activity 1/unregister?email=alice@test.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "alice@test.edu" in data["message"]
        assert "Test Activity 1" in data["message"]
        
        # Verify participant was removed
        activities_after = client_with_test_data.get("/activities").json()
        assert "alice@test.edu" not in activities_after["Test Activity 1"]["participants"]

    def test_unregister_not_registered(self, client_with_test_data):
        """
        Test that unregistering a student who was never signed up returns 400.
        """
        response = client_with_test_data.delete(
            "/activities/Test Activity 3/unregister?email=notregistered@test.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_invalid_activity(self, client_with_test_data):
        """
        Test that unregistering from a non-existent activity returns 404.
        """
        response = client_with_test_data.delete(
            "/activities/Nonexistent Activity/unregister?email=student@test.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_unregister_frees_a_spot(self, client_with_test_data):
        """
        Test that after unregistering, a freed spot allows another student to sign up.
        Test Activity 1 has max=2 and is currently full (2/2).
        After unregistering alice, bob should be able to register.
        """
        # Try to sign up new student (should fail - full)
        response_before = client_with_test_data.post(
            "/activities/Test Activity 1/signup?email=newstudent@test.edu"
        )
        assert response_before.status_code == 400
        
        # Unregister alice to free up a spot
        unregister_response = client_with_test_data.delete(
            "/activities/Test Activity 1/unregister?email=alice@test.edu"
        )
        assert unregister_response.status_code == 200
        
        # Try to sign up new student again (should succeed)
        response_after = client_with_test_data.post(
            "/activities/Test Activity 1/signup?email=newstudent@test.edu"
        )
        assert response_after.status_code == 200
        
        # Verify new participant is in the activity
        activities = client_with_test_data.get("/activities").json()
        assert "newstudent@test.edu" in activities["Test Activity 1"]["participants"]

    def test_unregister_with_encoded_activity_name(self, client_with_test_data):
        """
        Test that unregister works with URL-encoded activity names (with spaces).
        """
        # First add a participant
        client_with_test_data.post(
            "/activities/Test%20Activity%202/signup?email=tounregister@test.edu"
        )
        
        # Then unregister using encoded name
        response = client_with_test_data.delete(
            "/activities/Test%20Activity%202/unregister?email=tounregister@test.edu"
        )
        
        assert response.status_code == 200
        activities = client_with_test_data.get("/activities").json()
        assert "tounregister@test.edu" not in activities["Test Activity 2"]["participants"]

    def test_unregister_multiple_times(self, client_with_test_data):
        """
        Test that attempting to unregister twice returns 400 on the second attempt.
        """
        # First unregister should succeed
        response1 = client_with_test_data.delete(
            "/activities/Test Activity 1/unregister?email=alice@test.edu"
        )
        assert response1.status_code == 200
        
        # Second unregister for same student should fail
        response2 = client_with_test_data.delete(
            "/activities/Test Activity 1/unregister?email=alice@test.edu"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "not signed up" in data["detail"].lower()
