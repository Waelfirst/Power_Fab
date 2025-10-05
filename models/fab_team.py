from odoo import models, fields

class FabTeam(models.Model):
    _name = 'fab.team'
    _description = 'Fabrication Team'

    name = fields.Char(string='Team Name', required=True)
    members = fields.Many2many('res.users', string='Team Members')
    leader_id = fields.Many2one('res.users', string='Team Leader')