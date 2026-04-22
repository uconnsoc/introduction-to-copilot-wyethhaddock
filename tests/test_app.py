import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)

def test_signup_success():
    email = "newstudent@mergington.edu"
    response = client.post(f"/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Signed up {email} for Chess Club" == data["message"]
    # Verify added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities["Chess Club"]["participants"]

def test_signup_already_signed_up():
    email = "duplicate@mergington.edu"
    # First signup
    client.post(f"/activities/Programming Class/signup", params={"email": email})
    # Try again
    response = client.post(f"/activities/Programming Class/signup", params={"email": email})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student already signed up for this activity" == data["detail"]

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent Activity/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]

def test_unregister_success():
    email = "unregister@mergington.edu"
    # First signup
    client.post(f"/activities/Gym Class/signup", params={"email": email})
    # Then unregister
    response = client.delete(f"/activities/Gym Class/signup", params={"email": email})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert f"Unregistered {email} from Gym Class" == data["message"]
    # Verify removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities["Gym Class"]["participants"]

def test_unregister_not_signed_up():
    response = client.delete("/activities/Basketball Team/signup", params={"email": "notsigned@mergington.edu"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Student is not signed up for this activity" == data["detail"]

def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent Activity/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" == data["detail"]