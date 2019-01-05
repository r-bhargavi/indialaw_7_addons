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

class area_master(osv.osv):
    _name = 'area.master'    
    
    def onchange_name(self, cr, uid, ids, name, context=None):
        if not name:
            return {'value': {'city_code': False}}
        val = {
            'city_code': (name and len(name)>=3 and name[:3].upper() or False)
        }
        return {'value': val}
    
    _columns = {
    		'name': fields.char('Area/City Name', size=128, required=True),
    		'city_code':fields.char('Area/City Code', size=64, required=True),
        }
       
area_master()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: