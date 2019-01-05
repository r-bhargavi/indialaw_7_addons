# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013-2014 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>).
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
    "name": "Human Resources Overtime Management",
    "version": "1.0",
    "author": "Zesty Beanz Technologies",
    "category": "Human Resources",
    "website": "www.zbeanztech.com",
    "description": """Human Resources: Overtime tracking and workflow""",
    'depends': ['hr','resource'],
    'init_xml': [],
    'data': [
#              'report.xml',
             'hr_overtime_view.xml',
             'hr_overtime_workflow.xml',
             'security/ir_rule.xml',
             'security/ir.model.access.csv',
             ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'certificate': '',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: