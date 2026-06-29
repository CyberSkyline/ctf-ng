import pytest
from pathlib import Path
from ...config import CERTIFICATES_DIR


pytestmark = pytest.mark.db


class Test_Certificate_Listing:
    endpoint = "/ng/admin/certificates"

    def test_list_matches_directory(self, admin_client):
        response = admin_client.get(self.endpoint)
        assert response.status_code == 200

        root = Path(CERTIFICATES_DIR)
        expected = sorted(
            p.relative_to(root).as_posix()
            for p in root.rglob("*.typ")
            if not p.name.startswith("_")
        )
        assert response.json["data"]["files"] == expected

    def test_requires_admin(self, logged_in_client):
        response = logged_in_client.get(self.endpoint)
        assert response.status_code == 403
