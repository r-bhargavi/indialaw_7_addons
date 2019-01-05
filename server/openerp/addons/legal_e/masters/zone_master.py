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

        
class state_zone(osv.osv):
    _description="State Zone"
    _name = 'state.zone'
    _columns = {
        'state_id': fields.many2one('res.country.state', 'State', required=True),
        'name': fields.char('Zone Name', size=64, required=True),
        'branch_ids': fields.one2many('sale.shop', 'zone_id', 'Branches', ),
    }

state_zone()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: