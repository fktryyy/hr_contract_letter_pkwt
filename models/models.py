# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class hr_contract_letter_pkwt(models.Model):
#     _name = 'hr_contract_letter_pkwt.hr_contract_letter_pkwt'
#     _description = 'hr_contract_letter_pkwt.hr_contract_letter_pkwt'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
