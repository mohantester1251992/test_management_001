import pytest
from django.contrib.auth import get_user_model

from backend.apps.organizations.models import Membership, Organization
from backend.apps.projects.models import Project

pytestmark = pytest.mark.django_db


def test_project_queryset_for_user():
    User = get_user_model()
    owner = User.objects.create_user(email="owner@example.com", password="test1234")
    other = User.objects.create_user(email="other@example.com", password="test1234")
    org = Organization.objects.create(name="Acme", created_by=owner)
    Membership.objects.create(organization=org, user=owner, role=Membership.ROLE_OWNER)
    project = Project.objects.create(
        organization=org,
        name="Store",
        slug="store",
        description="",
        default_base_url="https://example.com",
        created_by=owner,
    )

    assert project in Project.objects.for_user(owner)
    assert project not in Project.objects.for_user(other)
