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
    'name': 'Employee Birthdays Reminder',
    'version': '1.0',
    'category': 'Customized integration',
    'author': 'Credativ Software (I) Pvt. Ltd.',
    'website': 'http://www.credativ.in',
    'description': """
Employee Birthdays Reminder
====================================

Used for Creating a Birthdays Dashboard which shows today's Birthday Employees, This Week Birthday Employees and This Month Birthday Employees.

    """,
    'depends': ['base','web','hr'],
    'data': [
             'board_birthdays_view.xml',
             'hr_employee_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
