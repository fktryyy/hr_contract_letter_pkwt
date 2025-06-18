import base64
import re
from odoo import models, fields, api, _
from babel.dates import format_date
from datetime import date
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    today_display = fields.Char(compute="_get_today_display", store=False)
    today_weekday = fields.Char(compute="_get_today_display", store=False)

    letter_pkwt_id = fields.Many2one('hr.contract.letter', string="Surat PKWT")
    letter_url = fields.Char("URL Surat PKWT", copy=False)
    generate_letter = fields.Boolean(string="Surat PKWT Dibuat", default=False)
    pkwt_letter_number = fields.Char(string='Nomor Surat PKWT', readonly=True, copy=False)

    def _get_today_display(self):
        today = date.today()
        for rec in self:
            rec.today_display = format_date(today, format='long', locale='id_ID')
            rec.today_weekday = format_date(today, format='EEEE', locale='id_ID')

    def _get_roman_month(self, month):
        roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
        return roman[month - 1]

    def action_generate_contract_letter(self):
        self.ensure_one()
        if not self.pkwt_letter_number:
            self.generate_pkwt_letters()

        return self.env.ref(
            'hr_contract_letter_pkwt.report_hr_contract_letter'
        ).report_action(self)

    def generate_pkwt_letters(self):
        """
        Generate surat PKWT sebagai PDF, upload ke MinIO,
        dan simpan URL serta status ke record kontrak.
        Bisa untuk multiple contract.
        """
        if not self:
            raise UserError(_("Tidak ada kontrak yang dipilih."))

        # Pastikan self adalah recordset, bukan list Python
        if isinstance(self, list):
            self = self.env['hr.contract'].browse([rec.id for rec in self if hasattr(rec, 'id')])

        minio_service = self.env['minio.upload.service']
        report_ref = 'hr_contract_letter_pkwt.report_hr_contract_letter'

        try:
            report = self.env.ref(report_ref)
        except Exception as e:
            raise UserError(_("Gagal memuat report '%s': %s") % (report_ref, str(e)))

        for contract in self:
            if not contract.employee_id:
                raise UserError(_("Kontrak '%s' tidak memiliki karyawan terkait.") % contract.name)

            if not contract.pkwt_letter_number:
                today = fields.Date.context_today(contract)
                number = self.env['ir.sequence'].next_by_code('hr.contract.pkwt')
                roman_month = self._get_roman_month(today.month)
                contract.pkwt_letter_number = f"{number}/PKWT-MCN/IOH-JTM/MPC/{roman_month}/{today.year}"

            try:
                # Gunakan recordset bukan list Python
                report_service = self.env['ir.actions.report']
                pdf_content, content_type = report_service._render_qweb_pdf(report_ref, contract.ids)
            except Exception as e:
                raise UserError("Gagal membuat PDF dari template surat PKWT: %s" % str(e))

            # Pastikan nama employee berupa string
            employee_name = contract.employee_id.name
            if isinstance(employee_name, list):
                employee_name = " ".join(employee_name)
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', employee_name or "unknown")

            filename = f"Surat-PKWT-{safe_name}.pdf"

            try:
                url = minio_service.upload_file(filename, pdf_content)
            except Exception as e:
                raise UserError(_("Gagal upload ke MinIO: %s") % str(e))

            if url:
                contract.letter_url = url
                contract.generate_letter = True
            else:
                raise UserError(_("Gagal mendapatkan URL dari MinIO."))


class HrContractHistory(models.Model):
    _inherit = 'hr.contract.history'

    def generate_pkwt_letters(self):
        """
        Loop semua record history, cari kontrak aktif sesuai employee dan tanggal mulai,
        lalu panggil generate surat dari model kontrak.
        """
        for record in self:
            contract = self.env['hr.contract'].search([
                ('employee_id', '=', record.employee_id.id),
                ('date_start', '=', record.date_start)
            ], limit=1)

            if not contract:
                raise UserError(_(
                    "Tidak ditemukan kontrak untuk %s dengan tanggal mulai %s."
                ) % (record.employee_id.name, record.date_start))

            # panggil function generate surat (dari model contract)
            contract.generate_pkwt_letters()

            contract.message_post(body=_(
                "Surat PKWT berhasil digenerate dari histori kontrak."
            ))
