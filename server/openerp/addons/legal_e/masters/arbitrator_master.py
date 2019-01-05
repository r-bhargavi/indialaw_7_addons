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


class arbitrator_master(osv.osv):
    
    _name = 'arbitrator.master'
    _columns = {
    		'name': fields.char('Arbitrator Name',size=128, required=True),
    		'number':fields.char('Arbitrator No',size=64, required=True),
            'street': fields.char('Street', size=128),
            'street2': fields.char('Street2', size=128),
            'zip': fields.char('Zip', change_default=True, size=24),
            'city': fields.char('City', size=128),
            'district_id':fields.many2one("district.district",'District'),
            'state_id': fields.many2one("res.country.state", 'State'),
            'country_id': fields.many2one('res.country', 'Country'),
            'email': fields.char('Email', size=240),
            'phone': fields.char('Phone', size=64),
            'fax': fields.char('Fax', size=64),
            'mobile': fields.char('Mobile', size=64),
            'bank_ids': fields.one2many('res.partner.bank', 'arbitrator_id', 'Banks'),
            }
    
    
    def onchange_state(self, cr, uid, ids, state_id, context=None):
        return {'value':{ 'district_id' : False}}
    
    
arbitrator_master()

class res_partner_bank(osv.osv):
    _inherit = 'res.partner.bank'
    _columns = {
        'arbitrator_id': fields.many2one('arbitrator.master', 'Arbitrator'),
        'partner_id': fields.many2one('res.partner', 'Account Owner',
            ondelete='cascade', select=True),
        }
    
res_partner_bank()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: