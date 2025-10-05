from odoo import models, fields, api

class FabOrder(models.Model):
    _name = 'fab.order'
    _description = 'Fabrication Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Fabrication Order Reference', required=True, copy=False, default='New')
    project_id = fields.Many2one('fab.project', string='Project', required=True, ondelete='cascade')
    estimation_id = fields.Many2one('fab.estimation', related='project_id.estimation_id', string='Estimation', store=True)
    sale_order_id = fields.Many2one('sale.order', related='project_id.sale_order_id', string='Sales Order', store=True)
    customer_id = fields.Many2one('res.partner', related='project_id.customer_id', string='Customer', store=True)
    material_id = fields.Many2one('fab.material', string='Material', required=True)
    part_name = fields.Char(string='Part Name', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('quality_check', 'Quality Check'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('fab.order') or 'New'
        return super(FabOrder, self).create(vals)