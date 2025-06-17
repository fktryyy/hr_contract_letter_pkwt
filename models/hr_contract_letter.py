import base64
from odoo import models, fields, api, _
from babel.dates import format_date
from datetime import date


class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    def _get_today_display(self):
            today = date.today()
            for rec in self:
                rec.today_display = format_date(today, format='long', locale='id_ID')
                rec.today_weekday = format_date(today, format='EEEE', locale='id_ID')

    today_display = fields.Char(compute="_get_today_display", store=False)
    today_weekday = fields.Char(compute="_get_today_display", store=False)

    letter_pkwt_id = fields.Many2one('hr.contract.letter', string="Surat PKWT")
    letter_url = fields.Char("URL Surat PKWT", copy=False)
    generate_letter = fields.Boolean(string="Surat PKWT Dibuat", default=False)
    pkwt_letter_number = fields.Char(string='Nomor Surat PKWT', readonly=True, copy=False)

    def action_generate_contract_letter(self):
        self.ensure_one() 
        if not self.pkwt_letter_number:# pastikan hanya satu record
            self.generate_pkwt_letters()

        # hanya generate report untuk satu record
        return self.env.ref('hr_contract_letter_pkwt.report_hr_contract_letter_template').report_action(self)

    def _get_roman_month(self, month):
        roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
        return roman[month - 1]

    def generate_pkwt_letters(self):
        """
        Generate PDF Surat PKWT, upload ke MinIO, dan update field URL & status.
        """
        minio_service = self.env['minio.upload.service']

        for contract in self:
            if not contract.employee_id:
                raise UserError(_("Kontrak '%s' tidak memiliki employee terkait.") % contract.name)

            if not contract.pkwt_letter_number:
                today = fields.Date.context_today(contract)
                number = contract.env['ir.sequence'].next_by_code('hr.contract.pkwt')
                roman_month = contract._get_roman_month(today.month)
                contract.pkwt_letter_number = f"{number}/PKWT-MCN/IOH-JTM/MPC/{roman_month}/{today.year}"

            # Generate PDF surat PKWT
            pdf_content, _ = contract.env.ref(
                'hr_contract_letter_pkwt.report_hr_contract_letter'
            )._render_qweb_pdf([contract.id])

            filename = f"Surat-PKWT-{contract.employee_id.name.replace(' ', '_')}.pdf"
            url = minio_service.upload_file(filename, pdf_content)

            contract.letter_url = url
            contract.generate_letter = True

    #ini untuk mendukung ir.actions.server pada model `hr.contract.history`
    class HrContractHistory(models.Model):
        _inherit = 'hr.contract.history'

        def generate_pkwt_letters(self):
            """
            Dipanggil oleh ir.actions.server pada model ini untuk generate surat PKWT.
            """
            for record in self:
                contract = self.env['hr.contract'].search([
                    ('employee_id', '=', record.employee_id.id),
                    ('date_start', '=', record.date_start)
                ], limit=1)

                if not contract:
                    raise UserError(_(
                        "Tidak ditemukan kontrak yang cocok untuk %s dengan tanggal mulai %s."
                    ) % (record.employee_id.name, record.date_start))

                contract.generate_pkwt_letters()

                contract.message_post(body=_("Surat PKWT berhasil digenerate dari histori kontrak."))