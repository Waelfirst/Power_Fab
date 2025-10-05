from odoo import models, fields, api

class FabProject(models.Model):
    _name = 'fab.project'
    _description = 'Fabrication Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Project Reference', required=True, copy=False, default='New')
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    project_name = fields.Char(string='Project Name', required=True)
    description = fields.Text(string='Project Description')
    stage = fields.Selection([
        ('new', 'New Project'),
        ('estimation', 'Estimation'),
        ('waiting_approval', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('sale_created', 'Sales Order Created'),
        ('in_fabrication', 'In Fabrication'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], string='Stage', default='new', tracking=True)
    estimation_id = fields.Many2one('fab.estimation', string='Estimation')
    sale_order_id = fields.Many2one('sale.order', string='Sales Order')
    fab_order_ids = fields.One2many('fab.order', 'project_id', string='Fabrication Orders')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('fab.project') or 'New'
        return super(FabProject, self).create(vals)