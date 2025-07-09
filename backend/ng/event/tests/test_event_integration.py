# import json

class TestEventIntegration:
    """Integration tests for event API endpoints."""

    def test_list_events_endpoint(self, admin_client):
        """Test listing events through the API endpoint."""
        response = admin_client.get("/ng/events")

        assert response.status_code != 404, "Events endpoint not found"

        # TODO - Actually check the response

    # def test_create_event_endpoint(self, admin_client):
    #     """Test creating an event through the API endpoint."""
    #     event_data = {
    #         "name": "Test Integration Event",
    #         "description": "A simple integration test event",
    #         "max_team_size": 4,
    #         "locked": False,
    #     }

    #     response = admin_client.post("/ng/events", data=json.dumps(event_data), content_type="application/json")

    #     assert response.status_code != 404, "Create event endpoint not found"

    #     # TODO actually verify the event was created correctly

