from shutil import rmtree
from tempfile import mkdtemp

import pytest
from sekoia_automation import constants

from cybelangel_modules import CybelangelModule
from cybelangel_modules.models import (
    CybelangelModuleConfiguration,
    ReportsTriggerConfiguration,
    CredentialsTriggerConfiguration,
    ClaimedAttacksTriggerConfiguration,
)
from cybelangel_modules.trigger_reports import ReportsTrigger
from cybelangel_modules.trigger_credentials import CredentialsTrigger
from cybelangel_modules.trigger_claimed_attacks import ClaimedAttacksTrigger


@pytest.fixture
def data_storage():
    original_storage = constants.DATA_STORAGE
    constants.DATA_STORAGE = mkdtemp()
    yield constants.DATA_STORAGE
    rmtree(constants.DATA_STORAGE)
    constants.DATA_STORAGE = original_storage


@pytest.fixture
def module():
    m = CybelangelModule()
    m.configuration = CybelangelModuleConfiguration(
        client_id="test-client-id",
        client_secret="test-client-secret",
    )
    return m


@pytest.fixture
def reports_trigger(module, data_storage):
    trigger = ReportsTrigger(module=module, data_path=data_storage)
    trigger.configuration = ReportsTriggerConfiguration(
        intake_key="test-intake-key",
        frequency=1,
        chunk_size=100,
    )
    return trigger


@pytest.fixture
def credentials_trigger(module, data_storage):
    trigger = CredentialsTrigger(module=module, data_path=data_storage)
    trigger.configuration = CredentialsTriggerConfiguration(
        intake_key="test-intake-key",
        frequency=1,
        chunk_size=100,
        limit=10,
    )
    return trigger


@pytest.fixture
def claimed_attacks_trigger(module, data_storage):
    trigger = ClaimedAttacksTrigger(module=module, data_path=data_storage)
    trigger.configuration = ClaimedAttacksTriggerConfiguration(
        intake_key="test-intake-key",
        frequency=1,
        chunk_size=100,
        limit=100,
    )
    return trigger
