import os
import base64
import pytest
from datetime import datetime, timedelta
from ...core.utils import utc_now
from ...core.utils import utc_now
from ...user.models.User import User
from ...team.models.Team import Team
from ...team.models.TeamMember import TeamMember
from ...event.models.Demographic import Demographic
from ...challenge.models.Challenge import Challenge
from ...scoring.models.Score import Score


pytestmark = pytest.mark.db_session



class Test_Sponsor_Listing:
    endpoint = "/ng/sponsors"
    def test_get_all_sponsors_empty(self, logged_in_client):
        response = logged_in_client.get(self.endpoint)
        assert response.status_code == 200
        assert response.json["data"] == []

    def test_get_all_sponsors(self, logged_in_client, sponsor_factory):
        sponsor_factory(name="Sponsor One", logo="logo1.png")
        sponsor_factory(name="Sponsor Two", logo="logo2.png")

        response = logged_in_client.get("/ng/sponsors")
        assert response.status_code == 200
        data = response.json["data"]
        assert len(data) == 2
        assert any(sponsor["name"] == "Sponsor One" for sponsor in data)
        assert any(sponsor["name"] == "Sponsor Two" for sponsor in data)


class Test_Sponsor_ByID:
    endpoint = "/ng/sponsors/{sponsor_id}"
    def test_get_sponsor_by_id_not_found(self, logged_in_client):
        response = logged_in_client.get(self.endpoint.format(sponsor_id=999))
        assert response.status_code == 404

    def test_get_sponsor_by_id(self, logged_in_client, sponsor_factory):
        sponsor = sponsor_factory(name="Test Sponsor", logo="testlogo.png")

        response = logged_in_client.get(self.endpoint.format(sponsor_id=sponsor.id))
        assert response.status_code == 200
        data = response.json["data"]
        assert data["id"] == sponsor.id
        assert data["name"] == "Test Sponsor"


class Test_Sponsor_Admin_Creation:
    endpoint = "/ng/admin/sponsors"
    def test_create_sponsor_admin(self, admin_client):
        sponsor_data = {
            "name": "New Sponsor",
            "logo": "branta_canadensis-scaled.jpeg"
        }
        response = admin_client.post(self.endpoint, json=sponsor_data)
        print(response.get_json())
        assert response.status_code == 201
        data = response.json["data"]
        assert data["name"] == "New Sponsor"
        assert data["logo"] == "branta_canadensis-scaled.jpeg"

    def test_create_sponsor_invalid_data_admin(self, admin_client):
        sponsor_data = {
            "name": "",
            "logo": "branta_canadensis-scaled.jpeg"
        }
        response = admin_client.post(self.endpoint, json=sponsor_data)
        assert response.status_code == 400

    def test_only_admins_can_create_sponsor(self, logged_in_client):
        sponsor_data = {
            "name": "New Sponsor",
            "logo": "branta_canadensis-scaled.jpeg"
        }
        response = logged_in_client.post(self.endpoint, json=sponsor_data)
        assert response.status_code == 403

class Test_Sponsor_Admin_Update:
    endpoint = "/ng/admin/sponsors/{sponsor_id}"
    def test_update_sponsor_admin(self, admin_client, sponsor_factory):
        sponsor = sponsor_factory(name="Old Sponsor", logo="oldlogo.png")
        update_data = {
            "name": "Updated Sponsor",
            "logo": "branta_canadensis-scaled.jpeg"
        }
        response = admin_client.put(self.endpoint.format(sponsor_id=sponsor.id), json=update_data)
        assert response.status_code == 200
        data = response.json["data"]
        assert data["name"] == "Updated Sponsor"
        assert data["logo"] == "branta_canadensis-scaled.jpeg"

    def test_update_sponsor_invalid_data_admin(self, admin_client, sponsor_factory):
        sponsor = sponsor_factory(name="Old Sponsor", logo="oldlogo.png")
        update_data = {
            "name": "",  # Invalid name
            "logo": "branta_canadensis-scaled.jpeg"
        }
        response = admin_client.put(self.endpoint.format(sponsor_id=sponsor.id), json=update_data)
        assert response.status_code == 400

    def test_only_admins_can_update_sponsor(self, logged_in_client, sponsor_factory):
        sponsor = sponsor_factory(name="Old Sponsor", logo="oldlogo.png")
        update_data = {
            "name": "Updated Sponsor",
            "logo": "branta_canadensis-scaled.jpeg"
        }
        response = logged_in_client.put(self.endpoint.format(sponsor_id=sponsor.id), json=update_data)
        assert response.status_code == 403

class Test_Sponsor_Search:
    endpoint = "/ng/sponsors/search"
    def test_search_sponsor_found(self, logged_in_client, sponsor_factory):
        sponsor_factory(name="Unique Sponsor", logo="uniquelogo.png")

        response = logged_in_client.get(self.endpoint, json={"name": "Unique Sponsor"})
        assert response.status_code == 200
        data = response.json["data"]
        assert any(s["name"] == "Unique Sponsor" for s in data)

    def test_search_sponsor_not_found(self, logged_in_client):
        response = logged_in_client.get(self.endpoint, json={"name": "Nonexistent Sponsor"})
        assert response.status_code == 404

    def test_search_sponsor_missing_name_param(self, logged_in_client):
        response = logged_in_client.get(self.endpoint, json={})
        assert response.status_code == 400

    def test_search_sponsor_partial_name(self, logged_in_client, sponsor_factory):
        sponsor_factory(name="Alpha Sponsor", logo="alphalogo.png")
        sponsor_factory(name="Beta Sponsor", logo="betalogo.png")

        response = logged_in_client.get(self.endpoint, json={"name": "Alpha"})
        assert response.status_code == 200
        data = response.json["data"]
        assert len(data) == 1
        assert any(s["name"] == "Alpha Sponsor" for s in data)

    def test_search_multiple_matches(self, logged_in_client, sponsor_factory):
        sponsor_factory(name="Gamma Sponsor", logo="gammalogo.png")
        sponsor_factory(name="Gamma Technologies", logo="gammatechlogo.png")

        response = logged_in_client.get(self.endpoint, json={"name": "Gamma"})
        assert response.status_code == 200
        data = response.json["data"]
        assert len(data) == 2
        assert any(s["name"] == "Gamma Sponsor" for s in data)
        assert any(s["name"] == "Gamma Technologies" for s in data)

