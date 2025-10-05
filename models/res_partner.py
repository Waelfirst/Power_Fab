from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    fab_project_ids = fields.One2many('fab.project', 'customer_id', string='Fabrication Projects')