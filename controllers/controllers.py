# -*- coding: utf-8 -*-
# from odoo import http


# class HrContractLetterPkwt(http.Controller):
#     @http.route('/hr_contract_letter_pkwt/hr_contract_letter_pkwt', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_contract_letter_pkwt/hr_contract_letter_pkwt/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_contract_letter_pkwt.listing', {
#             'root': '/hr_contract_letter_pkwt/hr_contract_letter_pkwt',
#             'objects': http.request.env['hr_contract_letter_pkwt.hr_contract_letter_pkwt'].search([]),
#         })

#     @http.route('/hr_contract_letter_pkwt/hr_contract_letter_pkwt/objects/<model("hr_contract_letter_pkwt.hr_contract_letter_pkwt"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_contract_letter_pkwt.object', {
#             'object': obj
#         })
