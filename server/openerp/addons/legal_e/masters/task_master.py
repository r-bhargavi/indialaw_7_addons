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


class task_master(osv.osv):
    
    _name = 'task.master'
    
    _columns = {
    		'name': fields.char('Task Title',size=128, required=True),
    		'task_type':fields.selection([('standard','Standard'),('regular','New')], 'Task Type', required=True),
    		'product_id':fields.many2one('product.product','Related Product'),
        }
    _defaults = {
        'task_type':'standard',
    }    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Task Title must be Unique!')
    ]    

    def create(self, cr, uid, vals, context=None):
        product_id = self.pool.get('product.product').create(cr, uid, {'name':vals['name'],'type':'service'})
        vals['product_id'] = product_id
        return super(task_master, self).create(cr, uid, vals, context=context)
    
task_master()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: