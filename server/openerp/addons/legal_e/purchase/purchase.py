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
import time
from openerp.tools.translate import _
from openerp.osv import fields, osv
from openerp import netsvc


class purchase_order(osv.osv):
    
    _inherit = 'purchase.order' 
        
    _columns = {
               'date_order':fields.date('Order Date', help="Date on which this document has been created."),
               'create_date':fields.datetime('Create Date'),
               'order_line': fields.one2many('purchase.order.line', 'order_id', 'Order Lines', states={'approved':[('readonly',True)],'done':[('readonly',True)]}),
        
               'office_id': fields.many2one('hr.office', 'Office'),
               'ho_branch_id':fields.many2one('ho.branch','HO Branch'),
                }
    _defaults = {
               'date_order': lambda *a: time.strftime('%Y-%m-%d'),
#                'create_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    		}

    #load office automatically when po create
    def create(self, cr, uid, vals, context=None):
        hr_employee_pool = self.pool.get('hr.employee')
        employee_ids = hr_employee_pool.search(cr, uid, [('user_id', '=', uid)], context=context)
        if employee_ids:
            employee = hr_employee_pool.browse(cr, uid, employee_ids, context=context)
            if vals:
                vals['office_id'] = employee[0].office_id.id
                vals['ho_branch_id'] = employee[0].ho_branch_id.id
        order =  super(purchase_order, self).create(cr, uid, vals, context=context)
        return order
    
    def copy(self, cr, uid, ids, default=None, context=None):
        default = default or {}
        default.update({
            'date_approve': False,
        })        
        res = super(purchase_order, self).copy(cr, uid, ids, default, context)
        return res
    
    def _choose_account_from_po_line(self, cr, uid, po_line, context=None):
        fiscal_obj = self.pool.get('account.fiscal.position')
        
        if po_line.product_id:
            acc_id = po_line.product_id.property_account_expense.id
            if not acc_id:
                acc_id = po_line.product_id.categ_id.property_account_expense_categ.id
            if not acc_id:
                raise osv.except_osv(_('Error!'), _('Define expense account for this company: "%s" (id:%d).') % (po_line.product_id.name, po_line.product_id.id,))
        else:
            acc_id = False#property_obj.get(cr, uid, 'property_account_expense_categ', 'product.category', context=context).id
        fpos = po_line.order_id.fiscal_position or False
        return fiscal_obj.map_account(cr, uid, fpos, acc_id)
    
    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the request for quotation and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        res = super(purchase_order, self).print_quotation(cr, uid, ids, context=context)
        if res.get('report_name'):
            res.update({'report_name': 'purchase.order'})
        return res
        
purchase_order()

class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line' 
    
    STATE_SELECTION = [
        ('draft', 'Draft PO'),
        ('sent', 'RFQ Sent'),
        ('confirmed', 'Waiting Approval'),
        ('approved', 'Purchase Order'),
        ('except_picking', 'Shipping Exception'),
        ('except_invoice', 'Invoice Exception'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ]     

    def _get_state(self, cr, uid, ids, context=None):
        result = {}
        for order in self.pool.get('purchase.order').browse(cr, uid, ids, context=context):
            for line in order.order_line:
                result[line.id] = True
        return result.keys() 
    
    _columns = {
               'order_state':fields.related('order_id','state',type='selection',selection=STATE_SELECTION,string='Order State',
            store={
                'purchase.order.line': (lambda self, cr, uid, ids, c={}: ids, ['order_id'], 10),
                'purchase.order': (_get_state, ['state'], 10),
            }),
            }
    
    _defaults = {
               'order_state': 'draft',
    		}
            

#     def view_init(self, cr, uid, fields, context=None):
#         if not context:
#             context = {}
#         po_obj = self.pool.get('purchase.order')
#         data = context and context.get('active_id', False)
#         if data:
#             po = po_obj.browse(cr, uid, data, context=context)
#             if po.state in ('done','approved'):
#                 raise osv.except_osv(_('Warning!'), _("Purchase Order is already Approved. So, now you cannot add new Line Now!"))
#       
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.order_id.state in ('approved','done'):
                raise osv.except_osv(_('Warning!'), _("'You cannot delete an Order line which is already Approved.'!"))
        return super(purchase_order_line, self).unlink(cr, uid, ids, context=context)
            
purchase_order_line()


class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    _columns = {
               'user_id_done':fields.many2one('res.users', 'Received By'),
               'office_id': fields.many2one('hr.office', 'Office'),
                }
    #
    # TODO: change and create a move if not parents
    #
    def action_done(self, cr, uid, ids, context=None):
        """Changes picking state to done.
        
        This method is called at the end of the workflow by the activity "done".
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'done', 'date_done': time.strftime('%Y-%m-%d %H:%M:%S'), 'user_id_done':uid})
        return True
    
stock_picking()


class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    
    _columns = {
               'user_id_done':fields.many2one('res.users', 'Received By'),
               'office_id': fields.many2one('hr.office', 'Office'),
                }
    
stock_picking_in()


class stock_move(osv.osv):
    _inherit = "stock.move"
    
    _columns = {
               'user_id_done':fields.many2one('res.users', 'Received By'),
               'date_done': fields.datetime('Date done'),
                }
   
    def action_done(self, cr, uid, ids, context=None):
        res = super(stock_move,self).action_done(cr, uid, ids, context)
        self.write(cr, uid, ids, {'date_done': time.strftime('%Y-%m-%d %H:%M:%S'), 'user_id_done':uid})
        return True
    
stock_move()


class stock_partial_move(osv.osv_memory):
    _inherit = "stock.partial.move"
    
    def do_partial(self, cr, uid, ids, context=None):
        # no call to super!
        assert len(ids) == 1, 'Partial move processing may only be done one form at a time.'
        partial = self.browse(cr, uid, ids[0], context=context)
        partial_data = {
            'delivery_date' : partial.date
        }
        moves_ids = []
        for move in partial.move_ids:
            if not move.move_id:
                raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))
            if move.move_id.product_qty < move.quantity or move.quantity == 0:
                raise osv.except_osv(_('Warning !'), _("please check quantity"))
            move_id = move.move_id.id
            partial_data['move%s' % (move_id)] = {
                'product_id': move.product_id.id,
                'product_qty': move.quantity,
                'product_uom': move.product_uom.id,
                'prodlot_id': move.prodlot_id.id,
            }
            moves_ids.append(move_id)
            if (move.move_id.picking_id.type == 'in') and (move.product_id.cost_method == 'average'):
                partial_data['move%s' % (move_id)].update(product_price=move.cost,
                                                          product_currency=move.currency.id)
        self.pool.get('stock.move').do_partial(cr, uid, moves_ids, partial_data, context=context)
        return {'type': 'ir.actions.act_window_close'}
    
stock_partial_move()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: