# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2016 BroadTech Solutions Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

{
    'name': 'Legal Reports',
    'version': '1.6',
    'category': 'Reports',
    'author': 'BroadTech IT Solutions Pvt Ltd.',
    'website': 'http://www.broadtech-innovations.com/',
    'description': """
Legal Reports

    """,
    'depends': [
        'legal_e_account', 
        'legal_e_hr',
        'jasper_reports',
        ],
    'data': [
         'report.xml',
         'res_company_view.xml',
         'wizard/court_diary_view.xml',
         'wizard/cost_sheet_view.xml',
         'wizard/monthly_bill_view.xml',
         ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
