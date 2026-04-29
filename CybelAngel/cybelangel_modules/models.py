from pydantic.v1 import BaseModel, Field, SecretStr

from sekoia_automation.connector import DefaultConnectorConfiguration


class CybelangelModuleConfiguration(BaseModel):
    client_id: str = Field(..., description="OAuth2 Client ID")
    client_secret: SecretStr = Field(..., description="OAuth2 Client Secret")


class ReportsTriggerConfiguration(DefaultConnectorConfiguration):
    frequency: int = Field(60, description="Polling frequency in seconds")
    chunk_size: int = Field(100, description="Number of events per push batch")


class CredentialsTriggerConfiguration(DefaultConnectorConfiguration):
    frequency: int = Field(60, description="Polling frequency in seconds")
    chunk_size: int = Field(100, description="Number of events per push batch")
    limit: int = Field(10, description="Number of credentials per page")


class ClaimedAttacksTriggerConfiguration(DefaultConnectorConfiguration):
    frequency: int = Field(60, description="Polling frequency in seconds")
    chunk_size: int = Field(100, description="Number of events per push batch")
    limit: int = Field(100, description="Number of claimed attacks per page (1-1000)", ge=1, le=1000)
