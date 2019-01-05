# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2013 ZestyBeanz Technologies Pvt. Ltd.
#    (http://wwww.zbeanztech.com)
#    contact@zbeanztech.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp import pooler
from openerp.tools.translate import _

class purchase_order(osv.osv):
    
     _inherit = 'purchase.order'
     _columns = {
        'is_modify' : fields.boolean('Is Modification Required?'),
            }
     _defaults = {
        'is_modify': False,
            }
     
     def action_modify_order_line(self, cr, uid, ids, context=None):
         self.write(cr, uid, ids, {'is_modify': True}, context=context)
         return True
     
     def get_invoice_id(self, cr, uid, ids, order_id):
         cr.execute('select invoice_id from purchase_invoice_rel where purchase_id=%s' %(order_id,))
         res = cr.fetchall()
         if res:
             return res[0][0]
         else: 
            return [] 
        
     def update_moves(self, cr, uid, ids, context=None):
         order = self.browse(cr, uid, ids, context)[0]
         mov_obj = self.pool.get('stock.move')
         move_id_list = []
         move_list = []
         picking_id = self.pool.get('stock.picking.in').search(cr, uid, [('purchase_id', '=', order.id)])
         for picking in picking_id:
             move_list.append(self.pool.get('stock.picking.in').browse(cr, uid, picking, context).move_lines)
             if self.pool.get('stock.picking.in').browse(cr, uid, picking, context).state == 'assigned':
                 picking_record = picking
         for order_line in order.order_line:
              draft_records = []
              move_ids = mov_obj.search(cr, uid, [('purchase_line_id', '=', order_line.id)])
              move_records = mov_obj.browse(cr,uid,move_ids)
              draft_qty = 0.00
              done_qty = 0.00
              if move_records:
                  for move_record in move_records:
                      if move_record.state != 'done':
                          draft_qty += move_record.product_qty
                          draft_records.append(move_record)
                      else:
                          done_qty += move_record.product_qty
                      if order_line.product_qty < done_qty:
                          raise osv.except_osv(_('Warning!'), _('You have already received the product %s of a quantity %s.') % (move_record.product_id.name, done_qty ))
                  if order_line.product_qty > done_qty + draft_qty:
                      if draft_records:
                          qty = draft_records[0].product_qty
                          current = order_line.product_qty - (done_qty + draft_qty)
                          qty = qty + current
                          mov_obj.write(cr, uid ,draft_records[0].id,{'product_qty': qty,
                                                                       'product_uos_qty': qty,
                                                                       'price_unit': order_line.price_unit,
                                                                       })
                  elif order_line.product_qty < done_qty + draft_qty:
                      if draft_records:
                          current = (done_qty + draft_qty) - order_line.product_qty 
                          for draft_record in draft_records:
                              if draft_record.product_qty >= current:
                                  qty = draft_record.product_qty - current
                                  current = 0.00
                                  mov_obj.write(cr, uid ,draft_record.id,{'product_qty': qty,
                                                                          'product_uos_qty': qty,
                                                                          'price_unit': order_line.price_unit,
                                                                           })
                              else:
                                  current = current - draft_record.product_qty
                                  mov_obj.write(cr, uid ,draft_record.id,{'product_qty': 0.00,
                                                                          'product_uos_qty': 0.00,
                                                                           'price_unit': order_line.price_unit,
                                                                           })
                  else:
                      if draft_records:
                          for draft_record in draft_records:
                             mov_obj.write(cr, uid ,draft_record.id,{'price_unit': order_line.price_unit,
                                                                     'product_uom': order_line.product_uom.id ,})
              else:
                  vals = self._prepare_order_line_move(cr, uid, order, order_line, picking_record, context)
                  mov_id = mov_obj.create(cr, uid, vals, context=context)
                  mov_obj.action_confirm(cr, uid, [mov_id])
                  mov_obj.force_assign(cr, uid, [mov_id])
         for list in move_list:
             for record in list:
                 if record.state != 'done' and not record.purchase_line_id:
                     mov_obj.action_cancel(cr, uid, [record.id], context=context)
                     context.update({'call_unlink': True})
                     mov_obj.unlink(cr, uid, [record.id], context=context)
                     del context['call_unlink']
         return True
     
     def update_invoice(self, cr, uid, ids, context=None):
         order = self.browse(cr, uid, ids, context)[0]
         invoice_id_list = []
         invoice_id_list2 = []
         invoice_line_obj = self.pool.get('account.invoice.line')
#          account_id = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category').id
         picking_id = self.pool.get('stock.picking.in').search(cr, uid, [('purchase_id', '=', order.id)])
         for picking in picking_id:
             if self.pool.get('stock.picking.in').browse(cr, uid, picking, context).state == 'assigned':
                 picking_record = picking
         invoice_id = self.get_invoice_id(cr, uid, ids, order.id)
         invoice_record = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context)
         for invoice in order.invoice_ids:
             invoice_id_list2.append(invoice.invoice_line)
         for order_line in order.order_line:
             if order_line.invoice_lines:
                  for invoice in order_line.invoice_lines:
                      invoice_id_list.append(invoice.id)
             if order_line.move_ids:
                  move_state = order_line.move_ids[0].state
             if order.invoice_method != 'picking':
                  account_id = self._choose_account_from_po_line(cr, uid, order_line, context=context)
                  res = self. _prepare_inv_line(cr, uid, account_id, order_line, context)
                  if order_line.move_ids:
                      for invoice_line_id in order_line.invoice_lines:
                          if move_state != 'done':
                              invoice_line_obj.write(cr, uid, invoice_line_id.id, res, context=context)
                  else:
                      res['invoice_id'] = invoice_id
                      inv_id = invoice_line_obj.create(cr, uid, res, context=context)
                      self.pool.get('purchase.order.line').write(cr, uid, [order_line.id], {'invoice_lines': [(4, inv_id)]})
             else:
                  if order_line.move_ids:
                       for invoice_line_id in order_line.invoice_lines:
                           if invoice_line_id.invoice_id.state == 'draft':
                               invoice_line_obj.write(cr, uid, invoice_line_id.id, {'price_unit': order_line.price_unit}, context=context)
                
         if order.invoice_method != 'picking':
              for invoice_list in invoice_id_list2:
                  for invoice in invoice_list:
                      if not invoice.id in invoice_id_list:
                          invoice_line_obj.unlink(cr, uid, [invoice.id], context=context)
         return True
     
     def action_update_order_line(self, cr, uid, ids, context=None):
         if context is None:
            context = {}
         self.update_invoice(cr, uid, ids, context)
         self.update_moves(cr, uid, ids, context)
         self.write(cr, uid, ids, {'is_modify': False}, context=context)
         return True
     
purchase_order()

class purchase_order_line(osv.osv):
    
     _inherit = 'purchase.order.line'
     _columns = {
        'move_state': fields.related('move_ids','state', type='char', string='Move State'),
            }
     
     def unlink(self, cr, uid, ids, context=None):
        mov_obj = self.pool.get('stock.move')
        move_states = []
        for order_line in self.browse(cr, uid, ids, context=context):
            move_ids = mov_obj.search(cr, uid, [('purchase_line_id', '=', order_line.id)])
            move_records = mov_obj.browse(cr,uid,move_ids)
            for move_record in move_records:
                move_states.append(move_record.state)
            if 'done' not in move_states:
                return super(purchase_order_line, self).unlink(cr, uid, ids, context=context)
            
purchase_order_line()