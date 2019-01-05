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


class res_partner(osv.osv):
    _inherit = 'res.partner' 
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('employee_pay', False):
            emp_pool = self.pool.get('hr.employee')
            employee_ids = emp_pool.search(cr, uid, [], context=context)
            partner_ids = []
            for emp_obj in emp_pool.browse(cr, uid, employee_ids, context=context):
                if emp_obj.user_id:
                    partner_ids.append(emp_obj.user_id.partner_id.id)
            partner_ids = list(set(partner_ids))
            args += [('id', 'in', partner_ids)]
            
        return super(res_partner, self).search(cr, uid, args, offset, limit, order, context, count)
    
    
res_partner()  

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: