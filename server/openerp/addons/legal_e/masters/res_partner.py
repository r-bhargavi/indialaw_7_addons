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
from openerp.tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    def onchange_name(self, cr, uid, ids, name, context=None):
        if not name:
            return {'value': {'client_data_id': False}}
        val = {
            'client_data_id': (name and len(name.replace(" ",""))>=4 and name.replace(" ","")[:4].upper() or False)
        }
        return {'value': val}
    
    _columns = {
    		'client_data_id': fields.char('Client ID',size=10),
    		'pan':fields.char('PAN',size=50),
    		'client_branch': fields.char('Location/Division',size=40),
    		'extension':fields.char('Extension',size=10),
    		'company_parent_id': fields.many2one('res.partner', 'Parent Company'),
    		'opposite':fields.boolean('Opposite Party'),
    		'district_id':fields.many2one('district.district', 'District'),
    		'property_account_payable': fields.property('account.account', type='many2one', relation='account.account', string="Account Payable", view_load=True,   domain="[('type', '=', 'payable')]", help="This account will be used instead of the default one as the payable account for the current partner"),
	        'property_account_receivable': fields.property('account.account', type='many2one', relation='account.account', string="Account Receivable",           view_load=True, domain="[('type', '=', 'receivable')]", help="This account will be used instead of the default one as the receivable account for the current partner"),
            'associate': fields.boolean('Associate'),
            'supplier_code': fields.char('Supplier Code', size=128),
            'create_date': fields.datetime('Create Date', readonly=True),
            'client_manager_id': fields.many2one('hr.employee','Client Relationship Manager'),
            }
    _defaults = {
        #'associate': True,      
        }
                
    def _get_supplier_code(self, cr, uid, context=None):
        supplier_code=self.pool.get('ir.sequence').get(cr, uid, 'res.partner')
        return supplier_code
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('supplier', False):
            supplier_code = self._get_supplier_code(cr, uid, context=context)
            vals.update({'supplier_code': supplier_code})
        res = super(res_partner, self).create(cr, uid, vals, context=context)
        return res
    
    
#     def onchange_district(self, cr, uid, ids, district_id, context=None):
#         if district_id:
#             state_id = self.pool.get('district.district').browse(cr, uid, district_id, context).state_id.id
#             country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
#             return {'value':{'country_id':country_id,'state_id':state_id}}
#         return {}
    
    def onchange_state(self, cr, uid, ids, state_id, context=None):
        return {'value':{ 'district_id' : False}}
     
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        if type(ids) is not list:
            ids = [ids]
        for line in self.browse(cr, uid, ids, context=context):
            name=False
            if line.name:
                name =line.name
            if line.supplier_code and line.supplier:
                name = (name and name + '['+line.supplier_code +'] ' or False)
            if line.client_branch:
                name += ' ,' + line.client_branch
            res.append((line.id,name))
        return res
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        args = args or []
        ids = []
        if name:
            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, ['|',('name', operator, name), ('supplier_code', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)
    
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        return super(res_partner, self).search(cr, uid, args, offset, limit, order, context, count)
    
    
res_partner()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: