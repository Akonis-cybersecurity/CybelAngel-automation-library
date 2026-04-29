import base64
import json

import pytest
import requests_mock as req_mock

from cybelangel_modules import CybelangelModule
from cybelangel_modules.models import CybelangelModuleConfiguration
from cybelangel_modules.client import TOKEN_URL, BASE_URL
from cybelangel_modules.actions.get_report_by_id import GetReportById
from cybelangel_modules.actions.update_report_status import UpdateReportStatus
from cybelangel_modules.actions.update_multiple_statuses import UpdateMultipleStatuses
from cybelangel_modules.actions.get_report_comments import GetReportComments
from cybelangel_modules.actions.post_report_comment import PostReportComment
from cybelangel_modules.actions.get_report_attachments import GetReportAttachments
from cybelangel_modules.actions.get_report_pdf import GetReportPdf
from cybelangel_modules.actions.get_report_archive import GetReportArchive
from cybelangel_modules.actions.get_mirror_details import GetMirrorDetails
from cybelangel_modules.actions.create_remediation_request import CreateRemediationRequest
from cybelangel_modules.actions.update_credential_status import UpdateCredentialStatus
from cybelangel_modules.actions.get_claimed_attacks import GetClaimedAttacks
from cybelangel_modules.actions.get_inventory_assets import GetInventoryAssets
from cybelangel_modules.actions.update_inventory_asset_status import UpdateInventoryAssetStatus

TOKEN_RESPONSE = {"access_token": "tok", "expires_in": 3600}


@pytest.fixture
def action_module():
    m = CybelangelModule()
    m.configuration = CybelangelModuleConfiguration(
        client_id="test-client-id",
        client_secret="test-secret",
    )
    return m


def make_action(cls, module):
    action = cls(module=module)
    return action


class TestGetReportById:
    def test_returns_report(self, action_module):
        action = make_action(GetReportById, action_module)
        expected = {"id": "rep-001", "title": "Test Report"}

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v2/reports/rep-001", json=expected)
            result = action.run({"report_id": "rep-001"})

        assert result == expected


class TestUpdateReportStatus:
    def test_update_valid_status(self, action_module):
        action = make_action(UpdateReportStatus, action_module)

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.put(f"{BASE_URL}/v1/reports/rep-001/status", json={"status": "resolved"})
            result = action.run({"report_id": "rep-001", "status": "resolved"})

        assert result is not None

    def test_raises_on_invalid_status(self, action_module):
        action = make_action(UpdateReportStatus, action_module)
        with pytest.raises(ValueError, match="Invalid status"):
            action.run({"report_id": "rep-001", "status": "invalid_status"})


class TestUpdateMultipleStatuses:
    def test_bulk_update(self, action_module):
        action = make_action(UpdateMultipleStatuses, action_module)
        updates = [
            {"report_id": "r1", "status": "resolved"},
            {"report_id": "r2", "status": "in_progress"},
        ]

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.post(f"{BASE_URL}/v1/reports/status", json={"updated": 2})
            result = action.run({"updates": updates})

        assert result["updated"] == 2

    def test_raises_on_invalid_status(self, action_module):
        action = make_action(UpdateMultipleStatuses, action_module)
        with pytest.raises(ValueError):
            action.run({"updates": [{"report_id": "r1", "status": "bad"}]})


class TestGetReportComments:
    def test_returns_comments(self, action_module):
        action = make_action(GetReportComments, action_module)
        expected = {"comments": [{"text": "hello"}]}

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v1/reports/rep-001/comments", json=expected)
            result = action.run({"report_id": "rep-001"})

        assert result == expected


class TestPostReportComment:
    def test_posts_comment(self, action_module):
        action = make_action(PostReportComment, action_module)

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.post(f"{BASE_URL}/v1/reports/rep-001/comments", json={"id": "c1"})
            result = action.run({"report_id": "rep-001", "comment": "Test comment"})

        assert result["id"] == "c1"


class TestGetReportAttachments:
    def test_returns_attachments(self, action_module):
        action = make_action(GetReportAttachments, action_module)
        expected = {"attachments": []}

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v1/reports/rep-001/attachments", json=expected)
            result = action.run({"report_id": "rep-001"})

        assert result == expected


class TestGetReportPdf:
    def test_returns_base64_pdf(self, action_module):
        action = make_action(GetReportPdf, action_module)
        pdf_bytes = b"%PDF-1.4 fake pdf content"

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v1/reports/rep-001/pdf", content=pdf_bytes)
            result = action.run({"report_id": "rep-001"})

        assert result["content_type"] == "application/pdf"
        assert base64.b64decode(result["content_base64"]) == pdf_bytes


class TestGetReportArchive:
    def test_returns_base64_archive(self, action_module):
        action = make_action(GetReportArchive, action_module)
        zip_bytes = b"PK\x03\x04 fake zip"

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v1/reports/rep-001/archive", content=zip_bytes)
            result = action.run({"report_id": "rep-001"})

        assert result["content_type"] == "application/zip"
        assert base64.b64decode(result["content_base64"]) == zip_bytes


class TestGetMirrorDetails:
    def test_returns_mirror(self, action_module):
        action = make_action(GetMirrorDetails, action_module)
        expected = {"url": "https://mirror.example.com"}

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v1/reports/rep-001/mirror", json=expected)
            result = action.run({"report_id": "rep-001"})

        assert result == expected


class TestCreateRemediationRequest:
    def test_creates_remediation(self, action_module):
        action = make_action(CreateRemediationRequest, action_module)

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.post(f"{BASE_URL}/v1/reports/rep-001/remediation", json={"id": "rem-1"})
            result = action.run({"report_id": "rep-001", "reason": "Urgent"})

        assert result["id"] == "rem-1"


class TestUpdateCredentialStatus:
    def test_valid_update(self, action_module):
        action = make_action(UpdateCredentialStatus, action_module)

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.post(f"{BASE_URL}/v1/credentials/status", json={"updated": 1})
            result = action.run({"updates": [{"credential_id": "c1", "status": "addressed"}]})

        assert result["updated"] == 1

    def test_invalid_status_raises(self, action_module):
        action = make_action(UpdateCredentialStatus, action_module)
        with pytest.raises(ValueError, match="Invalid credential status"):
            action.run({"updates": [{"credential_id": "c1", "status": "unknown"}]})


class TestGetClaimedAttacks:
    def test_returns_attacks(self, action_module):
        action = make_action(GetClaimedAttacks, action_module)
        expected = {"claimed_attacks": [{"id": "a1"}]}

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v1/threat-intelligence/claimed-attacks", json=expected)
            result = action.run({"limit": 10})

        assert result == expected


class TestGetInventoryAssets:
    def test_returns_assets(self, action_module):
        action = make_action(GetInventoryAssets, action_module)
        expected = {"assets": []}

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.get(f"{BASE_URL}/v1/adm/assets", json=expected)
            result = action.run({})

        assert result == expected


class TestUpdateInventoryAssetStatus:
    def test_updates_asset(self, action_module):
        action = make_action(UpdateInventoryAssetStatus, action_module)

        with req_mock.Mocker() as m:
            m.post(TOKEN_URL, json=TOKEN_RESPONSE)
            m.put(f"{BASE_URL}/v1/adm/assets/asset-001/status", json={"status": "active"})
            result = action.run({"asset_id": "asset-001", "status": "active"})

        assert result is not None
