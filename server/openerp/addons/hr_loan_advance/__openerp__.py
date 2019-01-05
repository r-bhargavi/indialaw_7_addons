# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
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
#
##############################################################################

{
    'name': 'HR Loan and Advance Management',
    'version': '1.0',
    'category': 'Human Resources',
    'description': """Manages loan and advance feature and its effects in payslip """,
    'author': "ZestyBeanz Technologies Pvt Ltd",
    'website' : "http://www.zbeanztech.com",
    'images': [],
    'depends': ['hr_payroll'],
    'init_xml': [],
    'data': [
        'security/ir.model.access.csv',
        'hr_view.xml',
       ],
    'demo_xml': [],
    'test': [],
    'active': False,
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
