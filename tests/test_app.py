import copy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
original_activities = copy.deepcopy(app_module.activities)

@pytest.fixture(autouse=True)
def reset_activities():
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))
    yield
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(original_activities))


def test_get_activities_returns_all_activities():
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == original_activities


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    params = {"email": new_email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for {activity_name}"}
    assert new_email in app_module.activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = "Programming Class"
    existing_email = "emma@mergington.edu"
    params = {"email": existing_email}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=params)

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_missing_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    params = {"email": "student@mergington.edu"}

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_from_activity_success():
    # Arrange
    activity_name = "Gym Class"
    email_to_remove = "john@mergington.edu"
    params = {"email": email_to_remove}

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params=params)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email_to_remove} from {activity_name}"}
    assert email_to_remove not in app_module.activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Art Club"
    missing_email = "notregistered@mergington.edu"
    params = {"email": missing_email}

    # Act
    response = client.delete(f"/activities/{activity_name}/participants", params=params)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
