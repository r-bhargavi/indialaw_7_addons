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


class delivery_master(osv.osv):
    _name = 'delivery.master'
    
    def onchange_name(self, cr, uid, ids, name, context=None):
        if not name:
            return {'value': {'code': False}}
        val = {
            'code': (name and len(name)>=4 and name[:4].upper() or False)
        }
        return {'value': val}
        
        
    _columns = {
    		'name': fields.char('Delivery Type',size=128, required=True),
    		'code':fields.char('Delivery Code',size=64, required=True),
        }
    
delivery_master()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: