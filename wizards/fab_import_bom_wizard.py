from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import xlrd

class FabImportBomWizard(models.TransientModel):
    _name = 'fab.import.bom.wizard'
    _description = 'Import BoM Lines from Excel'

    estimation_id = fields.Many2one('fab.estimation', string='Estimation', required=True)
    file = fields.Binary(string="Excel File", required=True)
    filename = fields.Char(string="Filename")

    def action_import(self):
        if not self.file:
            raise UserError(_("Please upload an Excel file."))
        try:
            data = base64.b64decode(self.file)
            book = xlrd.open_workbook(file_contents=data)
            sheet = book.sheet_by_index(0)
        except Exception as e:
            raise UserError(_("Invalid Excel file: %s") % e)
        # Expecting columns: Material, Part Name, Qty, UoM
        for row in range(1, sheet.nrows):
            material_name = str(sheet.cell(row, 0).value).strip()
            part_name = str(sheet.cell(row, 1).value).strip()
            qty = float(sheet.cell(row, 2).value)
            uom_name = str(sheet.cell(row, 3).value).strip()

            material = self.env['fab.material'].search([('name', '=', material_name)], limit=1)
            uom = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1)
            if not material or not uom:
                raise UserError(_("Material or UoM not found for row %s" % (row+1)))

            self.env['fab.estimation.bom.line'].create({
                'estimation_id': self.estimation_id.id,
                'material_id': material.id,
                'part_name': part_name,
                'quantity': qty,
                'uom_id': uom.id,
            })