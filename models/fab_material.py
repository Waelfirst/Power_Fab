from odoo import models, fields

class FabMaterial(models.Model):
    _name = 'fab.material'
    _description = 'Fabrication Material'

    name = fields.Char(string='Material Name', required=True)
    code = fields.Char(string='Material Code')
    description = fields.Text(string='Description')
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')
    cost = fields.Float(string='Unit Cost')