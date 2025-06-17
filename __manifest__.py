{
    'name': 'Contract Letter',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Generate Surat PKWT dari kontrak karyawan',
    'depends': ['hr_contract'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_mass_action.xml',
        'report/hr_contract_letter_template.xml',
        'report/hr_contract_letter_report.xml',
        'data/ir_sequence_data.xml',
    ],
    'installable': True,
}
