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

class assignee_master(osv.osv):
    _name = 'assignee.master'
    
    def onchange_name(self, cr, uid, ids, name, context=None):
        if not name:
            return {'value': {'code': False}}
        val = {
            'code': (name and len(name)>=4 and name[:4].upper() or False)
        }
        return {'value': val}
                
                
    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'country_id':country_id}}
        return {}
        
    _columns = {
    		'name': fields.char('Assignee Name',size=128, required=True),
    		'code':fields.char('Code',size=64, required=True),
    		'email': fields.char('Email', size=240, required=True),
		    'phone': fields.char('Phone', size=64, required=True),
    		'street': fields.char('Street', size=128, required=True),
		    'street2': fields.char('Street2', size=128),
		    'zip': fields.char('Zip', change_default=True, size=24, required=True),
		    'city': fields.char('City', size=128, required=True),
		    'state_id': fields.many2one("res.country.state", 'State', required=True),
		    'country_id': fields.many2one('res.country', 'Country', required=True),		
            }
    
assignee_master()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: