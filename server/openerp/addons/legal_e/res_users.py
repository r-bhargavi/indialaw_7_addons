# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

class res_users(osv.osv):
    _inherit = 'res.users'
    _columns = {
        'location_ids':fields.many2many('ho.branch','res_location_users_rel','user_id','location_id','Allowed Locations'),
    }

    def create(self, cr, uid, vals, context=None):
        gids = self.pool.get('res.groups').search(cr, uid, [('name','=','Associate'),('category_id','=',False)])
        gstring=False
        if len(gids):
            if vals.has_key('in_group_' + str(gids[0])) and vals['in_group_' + str(gids[0])]:
                gstring = True 
            
        user_id = super(res_users, self).create(cr, uid, vals, context=context)
        user = self.browse(cr, uid, user_id, context=context)
        if user.partner_id and gstring: 
            user.partner_id.write({'supplier': True})
        elif user.partner_id and not gstring: 
            user.partner_id.write({'supplier': False})
        return user_id        

    def write(self, cr, uid, ids, values, context=None):
        gids = self.pool.get('res.groups').search(cr, uid, [('name','=','Associate'),('category_id','=',False)])
        gstring=False
        
        if len(gids):
            if values.has_key('in_group_' + str(gids[0])) and values['in_group_' + str(gids[0])]:
                gstring = True
                
        if values.get('password', False):
            uid = SUPERUSER_ID
        res = super(res_users, self).write(cr, uid, ids, values, context)        
        if not isinstance(ids,(list)):
            ids = [ids]
        for user in self.browse(cr, uid, ids, context=context):
            if user.partner_id and gstring: 
                user.partner_id.write({'supplier': True})
            elif user.partner_id and not gstring: 
                user.partner_id.write({'supplier': False})
                 
        return res
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: