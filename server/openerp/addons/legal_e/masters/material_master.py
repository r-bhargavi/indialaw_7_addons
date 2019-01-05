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


class material_master(osv.osv):
    
    _name = 'material.master'

    def _check_name_length(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        name = self.browse(cr, uid, ids[0]).name        
        if len(name)<4:
                return False
        return True
    def onchange_name(self, cr, uid, ids, name, context=None):
        if not name:
            return {'value': {'material_code': False}}
        val = {
            'material_code': (name and len(name)>=4 and name[:4].upper() or False)
        }
        return {'value': val}
        
        
    _columns = {
    		'name': fields.char('Material Title',size=128, required=True),
    		'material_code':fields.char('Material Id',size=28, required=True),
        }
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Material Title must be Unique!'),
        ('code_uniq', 'unique(material_code)', 'Material Id must be Unique!'),
    ]
material_master()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: