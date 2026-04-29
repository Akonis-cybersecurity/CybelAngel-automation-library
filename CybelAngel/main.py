from cybelangel_modules import CybelangelModule
from cybelangel_modules.trigger_reports import ReportsTrigger
from cybelangel_modules.trigger_credentials import CredentialsTrigger
from cybelangel_modules.trigger_claimed_attacks import ClaimedAttacksTrigger
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

if __name__ == "__main__":
    module = CybelangelModule()
    module.register(ReportsTrigger, "cybelangel_reports")
    module.register(CredentialsTrigger, "cybelangel_credentials")
    module.register(ClaimedAttacksTrigger, "cybelangel_claimed_attacks")
    module.register(GetReportById, "cybelangel_get_report_by_id")
    module.register(UpdateReportStatus, "cybelangel_update_report_status")
    module.register(UpdateMultipleStatuses, "cybelangel_update_multiple_statuses")
    module.register(GetReportComments, "cybelangel_get_report_comments")
    module.register(PostReportComment, "cybelangel_post_report_comment")
    module.register(GetReportAttachments, "cybelangel_get_report_attachments")
    module.register(GetReportPdf, "cybelangel_get_report_pdf")
    module.register(GetReportArchive, "cybelangel_get_report_archive")
    module.register(GetMirrorDetails, "cybelangel_get_mirror_details")
    module.register(CreateRemediationRequest, "cybelangel_create_remediation_request")
    module.register(UpdateCredentialStatus, "cybelangel_update_credential_status")
    module.register(GetClaimedAttacks, "cybelangel_get_claimed_attacks")
    module.register(GetInventoryAssets, "cybelangel_get_inventory_assets")
    module.register(UpdateInventoryAssetStatus, "cybelangel_update_inventory_asset_status")
    module.run()
