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
from openerp import SUPERUSER_ID

        
class ho_branch(osv.osv):
    _description="Head Office"
    _name = 'ho.branch'
    _columns = {
        'state_id': fields.many2one('res.country.state', 'State', required=True),
        'name': fields.char('Office Name', size=64, required=True),
        'code': fields.char('Office Code', size=10, required=True),
        'sequence_id': fields.many2one('ir.sequence', 'Entry Sequence', help="This field contains the information related to the numbering of the Case Entries."),
        'district_id':fields.many2one('district.district', 'District'),
        'country_id':fields.many2one('res.country', 'Country'),
        'active':  fields.boolean('Active'),
    }

    #district set as null when no state present
    def onchange_state(self, cr, uid, ids, state_id, context=None):
        return {'value':{ 'district_id' : False}}
    
    #state set as null when no country preset 
    def onchange_country(self, cr, uid, ids, country_id, context=None):
        return {'value':{ 'state_id' : False}}
    
    def create_sequence(self, cr, uid, vals, context=None):
        """ Create new no_gap entry sequence for every new Branch
        """
        seq = {
            'name': vals['name'],
            'implementation':'no_gap',
            'padding': 3,
            'number_increment': 1
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        return self.pool.get('ir.sequence').create(cr, uid, seq)
        

    def create(self, cr, uid, vals, context=None):
        if vals is None:
           vals = {}
        vals.update({'sequence_id': False})
        return super(ho_branch, self).create(cr, uid, vals, context)
        
ho_branch()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
