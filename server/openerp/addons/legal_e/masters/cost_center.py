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
from openerp.osv import fields, osv


class cost_center(osv.osv):
    _description="Cost Center"
    _name = 'legal.cost.center'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'office_id':fields.many2one('ho.branch', 'Office', required=True),
        'dept_ids': fields.one2many('hr.department', 'cost_id', "Departments")
        }
    
cost_center()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: