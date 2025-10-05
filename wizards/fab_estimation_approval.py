from odoo import models, fields

class FabEstimationApprovalWizard(models.TransientModel):
    _name = 'fab.estimation.approval.wizard'
    _description = 'Estimation Approval Wizard'

    estimation_id = fields.Many2one('fab.estimation', string='Estimation', required=True)
    action = fields.Selection([('approve', 'Approve'), ('reject', 'Reject')], required=True)

    def do_approval(self):
        if self.action == 'approve':
            self.estimation_id.action_approve_estimation()
        else:
            self.estimation_id.write({'state': 'rejected'})