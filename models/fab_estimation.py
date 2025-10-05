from odoo import models, fields, api, _

class FabEstimation(models.Model):
    _name = 'fab.estimation'
    _description = 'Fabrication Estimation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Estimation Reference', required=True, copy=False, default='New')
    project_id = fields.Many2one('fab.project', string='Project', required=True, ondelete='cascade')
    customer_id = fields.Many2one('res.partner', related='project_id.customer_id', string='Customer', store=True)
    material_cost = fields.Monetary(
        string='Material Cost', currency_field='currency_id', compute='_compute_material_cost', store=True)
    labor_cost = fields.Monetary(string='Labor Cost', currency_field='currency_id')
    machine_cost = fields.Monetary(string='Machine Cost', currency_field='currency_id')
    overhead_cost = fields.Monetary(string='Overhead Cost', currency_field='currency_id')
    total_cost = fields.Monetary(string='Total Cost', compute='_compute_total_cost', store=True)
    selling_price = fields.Monetary(string='Selling Price', currency_field='currency_id')
    profit_margin = fields.Float(string='Profit Margin %', compute='_compute_profit_margin', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    estimation_line_ids = fields.One2many('fab.estimation.line', 'estimation_id', string='Estimation Lines')
    bom_line_ids = fields.One2many('fab.estimation.bom.line', 'estimation_id', string='BoM Lines')
    part_line_ids = fields.One2many('fab.estimation.part.line', 'estimation_id', string='Part Lines')

    @api.depends('bom_line_ids.material_id', 'bom_line_ids.quantity')
    def _compute_material_cost(self):
        for rec in self:
            total = 0.0
            for line in rec.bom_line_ids:
                if line.material_id and line.quantity:
                    total += line.material_id.cost * line.quantity
            rec.material_cost = total

    @api.depends('material_cost', 'labor_cost', 'machine_cost', 'overhead_cost')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.material_cost + rec.labor_cost + rec.machine_cost + rec.overhead_cost

    @api.depends('total_cost', 'selling_price')
    def _compute_profit_margin(self):
        for rec in self:
            if rec.total_cost:
                rec.profit_margin = ((rec.selling_price - rec.total_cost) / rec.total_cost) * 100
            else:
                rec.profit_margin = 0.0

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('fab.estimation') or 'New'
        estimation = super().create(vals)
        estimation.project_id.write({'estimation_id': estimation.id, 'stage': 'estimation'})
        return estimation

    def action_submit_for_approval(self):
        self.write({'state': 'submitted'})
        self.project_id.write({'stage': 'waiting_approval'})

    def action_approve_estimation(self):
        for estimation in self:
            estimation.write({'state': 'approved'})
            estimation.project_id.write({'stage': 'approved'})
            sale_order = self.action_create_sale_order()
            estimation.project_id.write({
                'sale_order_id': sale_order.id,
                'stage': 'sale_created'
            })
            estimation._create_fabrication_orders()
            return True

    def action_create_sale_order(self):
        sale_order_obj = self.env['sale.order']
        order_lines = []
        for line in self.estimation_line_ids:
            order_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'price_unit': line.selling_price,
            }))
        vals = {
            'partner_id': self.customer_id.id,
            'fab_project_id': self.project_id.id if 'fab_project_id' in sale_order_obj._fields else False,
            'order_line': order_lines,
        }
        sale_order = sale_order_obj.create(vals)
        self.write({'state': 'approved'})
        return sale_order

    def _create_fabrication_orders(self):
        fab_order_obj = self.env['fab.order']
        for line in self.estimation_line_ids:
            fab_order_obj.create({
                'project_id': self.project_id.id,
                'material_id': line.material_id.id,
                'part_name': line.part_name,
                'quantity': line.quantity,
                'uom_id': line.uom_id.id,
            })

    def open_import_bom_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import BoM from Excel',
            'res_model': 'fab.import.bom.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_estimation_id': self.id,
            }
        }

class FabEstimationLine(models.Model):
    _name = 'fab.estimation.line'
    _description = 'Fabrication Estimation Line'

    estimation_id = fields.Many2one('fab.estimation', string='Estimation', ondelete='cascade')
    part_name = fields.Char(string='Part Name', required=True)
    material_id = fields.Many2one('fab.material', string='Material', required=True)
    quantity = fields.Float(string='Quantity', default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True)
    selling_price = fields.Monetary(string='Selling Price', currency_field='currency_id')
    product_id = fields.Many2one('product.product', string='Product')
    currency_id = fields.Many2one('res.currency', related='estimation_id.currency_id', store=True)

class FabEstimationBomLine(models.Model):
    _name = 'fab.estimation.bom.line'
    _description = 'Estimation BoM Line'

    estimation_id = fields.Many2one('fab.estimation', string='Estimation', ondelete='cascade')
    material_id = fields.Many2one('fab.material', string='Material', required=True)
    part_name = fields.Char(string='Part Name')
    quantity = fields.Float(string='Quantity', default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')

class FabEstimationPartLine(models.Model):
    _name = 'fab.estimation.part.line'
    _description = 'Estimation Part of Product Line'

    estimation_id = fields.Many2one('fab.estimation', string='Estimation', ondelete='cascade')
    part_name = fields.Char(string='Part Name', required=True)
    description = fields.Text(string='Description')
    quantity = fields.Float(string='Quantity', default=1.0)
    uom_id = fields.Many2one('uom.uom', string='Unit of Measure')