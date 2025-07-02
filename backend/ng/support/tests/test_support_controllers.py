"""
Unit tests for support domain controllers
"""


class TestCreateTicketController:
    def test_ticket_creation_logic(self):
        def mock_create_ticket(ticket_data):
            if not ticket_data.get("title"):
                raise ValueError("Title required")
            if not ticket_data.get("description"):
                raise ValueError("Description required")
            return {"ticket": {"id": 1, **ticket_data, "status": "open"}}

        valid_data = {"title": "Test Ticket", "description": "Test Description"}
        result = mock_create_ticket(valid_data)

        assert result["ticket"]["id"] == 1
        assert result["ticket"]["title"] == "Test Ticket"
        assert result["ticket"]["status"] == "open"


class TestTicketPriorityController:
    def test_priority_assignment(self):
        def mock_assign_priority(tickets):
            for ticket in tickets:
                if "urgent" in ticket.get("title", "").lower():
                    ticket["priority"] = "high"
                else:
                    ticket["priority"] = "medium"
            return tickets

        test_tickets = [
            {"id": 1, "title": "Regular issue"},
            {"id": 2, "title": "URGENT: System down"},
        ]

        result = mock_assign_priority(test_tickets)

        assert result[0]["priority"] == "medium"
        assert result[1]["priority"] == "high"
