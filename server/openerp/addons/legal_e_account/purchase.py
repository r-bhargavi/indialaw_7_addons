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


class purchase_order_line(osv.osv):
    _inherit = 'purchase.order.line' 
    
    _columns = {
        'division_id': fields.many2one('hr.department', string='Department/Division'),
        'office_id':fields.many2one('ho.branch','Office'),
        }
    
purchase_order_line()  


class purchase_order(osv.osv):
    _inherit = 'purchase.order'
    
    def _get_invoice_number(self, cr, uid, ids, name, args, context=None):
        result = {}
        for po in self.browse(cr, uid, ids, context=context):
            invoice_number = ''
            for invoice in po.invoice_ids:
                if invoice.number:
                    invoice_number += invoice.number + ' '
            result[po.id] = invoice_number
        return result
    
    
    _columns = {
        'invoice_number': fields.function(_get_invoice_number, type="char", string='Invoice Number'),
        }
    
    
    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        res = super(purchase_order,  self)._prepare_inv_line(cr, uid, account_id, order_line, context=context)
        if res:
            res.update({
                'division_id': order_line.division_id and order_line.division_id.id or False,
                'office_id': order_line.office_id and order_line.office_id.id or False,
                })
        return res
    
    
    def _prepare_order_line_move(self, cr, uid, order, order_line, picking_id, context=None):
        res = super(purchase_order,  self)._prepare_order_line_move(cr, uid, order, order_line, picking_id, context=context)
        if res:
            res.update({
                'division_id': order_line.division_id and order_line.division_id.id or False,
                'office_id': order_line.office_id and order_line.office_id.id or False,
                })
        return res
    

purchase_order()

class stock_picking(osv.osv):
    _inherit = 'stock.picking'
    
    
    def _prepare_invoice_line(self, cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=None):
        res = super(stock_picking,  self)._prepare_invoice_line(cr, uid, group, picking, move_line, invoice_id, invoice_vals, context=context)
        if res:
            res.update({
                'division_id': move_line.division_id and move_line.division_id.id or False,
                'office_id': move_line.office_id and move_line.office_id.id or False,
                })
        return res
    
    
stock_picking()

class stock_move(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'division_id': fields.many2one('hr.department', string='Department/Division'),
        'office_id': fields.many2one('ho.branch','Office'),
        }
    
stock_move()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: