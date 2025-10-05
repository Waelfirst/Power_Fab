from odoo import models, fields

class FabOrderCancelWizard(models.TransientModel):
    _name = 'fab.order.cancel.wizard'
    _description = 'Fabrication Order Cancel Wizard'

    fab_order_id = fields.Many2one('fab.order', string='Fabrication Order', required=True)
    reason = fields.Text(string='Cancellation Reason')

    def cancel_order(self):
        self.fab_order_id.write({'state': 'cancel'})