"""
Model tests for TicketTag
"""

import pytest
from unittest.mock import patch
from ..models.TicketTag import TicketTag
from ...core.exceptions import ConflictError

class TestTicketTagRepr:
    def test_repr(self, ticket_tag):
        """Test the string representation of the model."""
        assert f"<TicketTag {ticket_tag.name}>" == repr(ticket_tag)


class TestDefaults:
    def test_defaults(self):
        """Test the default values for a new instance."""
        tag = TicketTag()
        assert tag.name is None
        assert tag.color is None
        assert tag.description is None


class TestCreateTag:
    def test_create_tag(self, db_session):
        """Test creating a tag with the create method."""
        tag = TicketTag.create_tag(name="test-tag", description="A test tag")

        refreshed_tag = TicketTag.find_by_id(tag.id)
        assert refreshed_tag is not None
        assert refreshed_tag.name == "test-tag"
        assert refreshed_tag.description == "A test tag"

    def test_create_tag_respects_commit_flag(self, db_session):
        """Test that create respects the commit flag."""
        with patch.object(db_session, "commit") as mock_commit:
            tag = TicketTag.create_tag(
                name="no-commit-tag", description="No commit", commit=False
            )
            mock_commit.assert_not_called()
            assert tag.name == "no-commit-tag"

        with patch.object(db_session, "commit") as mock_commit:
            tag = TicketTag.create_tag(
                name="with-commit-tag", description="With commit", commit=True
            )
            mock_commit.assert_called_once()

    def test_create_tag_duplicate_name(self, db_session):
        """Test that creating a tag with duplicate name raises ConflictError."""
        # Create a tag first
        TicketTag.create_tag(name="unique-tag-test", color="#FF0000")
        db_session.flush()  # Ensure it's in the database

        # Try to create another with the same name
        with pytest.raises(ConflictError) as exc_info:
            TicketTag.create_tag(name="unique-tag-test", color="#00FF00")
        assert "Tag name 'unique-tag-test' already exists" in str(exc_info.value)


class TestUpdateTag:
    def test_update_tag(self, ticket_tag, db_session):
        """Test updating tag properties."""
        tag_id = ticket_tag.id
        original_description = ticket_tag.description

        ticket_tag.update_tag(description="Updated description")

        refreshed_tag = TicketTag.find_by_id(tag_id)
        assert refreshed_tag is not None
        assert refreshed_tag.description == "Updated description"
        assert refreshed_tag.description != original_description

    def test_update_tag_commits_changes(self, ticket_tag, db_session):
        """Test that update_tag commits changes."""
        with patch.object(db_session, "commit") as mock_commit:
            ticket_tag.update_tag(description="New description")
            mock_commit.assert_called_once()


class TestDeleteTag:
    def test_delete_tag(self, ticket_tag_factory, db_session):
        """Test deleting a tag."""
        tag = ticket_tag_factory(name="to-delete")
        tag_id = tag.id

        tag.delete_tag()

        deleted_tag = TicketTag.find_by_id(tag_id)
        assert deleted_tag is None

    def test_delete_tag_commits_changes(self, ticket_tag_factory, db_session):
        """Test that delete_tag commits changes."""
        tag = ticket_tag_factory(name="to-delete-with-commit")

        with patch.object(db_session, "commit") as mock_commit:
            tag.delete_tag()
            mock_commit.assert_called_once()


class TestFindByName:
    def test_find_by_name(self, ticket_tag):
        """Test finding a tag by name."""
        found_tag = TicketTag.find_by_name("bug")
        assert found_tag is not None
        assert found_tag.id == ticket_tag.id

    def test_find_by_name_not_found(self, db_session):
        """Test finding a non-existent tag by name."""
        found_tag = TicketTag.find_by_name("non-existent-tag")
        assert found_tag is None


class TestGetAllTags:
    def test_get_all_tags(self, ticket_tag_factory):
        """Test getting all tags and verify tags match."""
        tags = [
            ticket_tag_factory(name="alpha"),
            ticket_tag_factory(name="beta"),
            ticket_tag_factory(name="gamma"),
        ]

        all_tags = TicketTag.get_all_tags()
        assert len(all_tags) >= 3

        tag_names = [tag.name for tag in all_tags]
        assert tag_names == sorted(tag_names)

        # Verify the returned tags match the created tags
        created_tag_ids = {tag.id for tag in tags}

        # Find the created tags in the returned list
        matching_tags = [tag for tag in all_tags if tag.id in created_tag_ids]
        assert len(matching_tags) == len(tags)

        # Verify they match
        for tag in matching_tags:
            original = next(t for t in tags if t.id == tag.id)
            assert tag.name == original.name
            assert tag.color == original.color
            assert tag.description == original.description


class TestSerialize:
    def test_serialize(self, ticket_with_tags):
        """Test tag serialization."""
        tag = ticket_with_tags.tags[0]
        data = tag.serialize()

        assert "id" in data
        assert "name" in data
        assert "color" in data
        assert "description" in data
        assert "ticket_count" in data
        assert data["ticket_count"] >= 1

    def test_serialize_empty_tag(self, ticket_tag_factory):
        """Test serializing a tag with no tickets."""
        tag = ticket_tag_factory(name="empty-tag")
        data = tag.serialize()

        assert data["ticket_count"] == 0
