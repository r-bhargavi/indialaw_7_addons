# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Legal Hr Customization',
    'version': '1.20',
    'category': 'Customized integration',
    'author': 'BroadTech It Solutions Pvt Ltd.',
    'website': 'http://www.broadtech-innovations.com/',
    'description': """
Hr Customization

    """,
    'depends': ['legal_e', 'hr_payroll', 'hr_overtime', 'hr_loan_advance'
    ],
    'data': [
         'edi/hr_holiday_data.xml',
         'hr_attendance_view.xml',
         'hr_view.xml',
         'security/ir.model.access.csv',
         'security/hr_security.xml',
         'hr_payroll_data.xml',
         'hr_payroll_view.xml',
         'hr_expense_workflow.xml',
         'hr_data.xml',
         'res_company_view.xml',
         'hr_holidays_workflow.xml'
         ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
