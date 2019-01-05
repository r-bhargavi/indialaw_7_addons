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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class account_statement_from_invoice_lines(osv.osv_memory):
    """
    Generate Entries by Statement from Invoices
    """
    _name = "legale.account.statement.from.invoice.lines"
    _description = "Entries by Statement from Invoices"
    _columns = {
        'journal_id': fields.many2one('account.journal', 'Journal'),
        'period_id': fields.many2one('account.period', 'Period'),
        'line_ids': fields.many2many('account.move.line', 'legale_account_move_line_relation', 'move_id', 'line_id', 'Invoices'),
    }

    def populate_statement(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        statement_id = context.get('statement_id', False)
        if not statement_id:
            return {'type': 'ir.actions.act_window_close'}
        data =  self.read(cr, uid, ids, context=context)[0]
        line_ids = data['line_ids']
        if not line_ids:
            return {'type': 'ir.actions.act_window_close'}

        line_obj = self.pool.get('account.move.line')
        statement_obj = self.pool.get('legale.account.bank.statement')
        statement_line_obj = self.pool.get('legale.account.bank.statement.line')
        currency_obj = self.pool.get('res.currency')
        line_date = time.strftime('%Y-%m-%d')
        statement = statement_obj.browse(cr, uid, statement_id, context=context)

        # for each selected move lines
        for line in line_obj.browse(cr, uid, line_ids, context=context):
            voucher_res = {}
            ctx = context.copy()
            #  take the date for computation of currency => use payment date
            ctx['date'] = line_date
            
                
            amount = dr_amount = cr_amount = 0.0
    
            if line.debit > 0:
                dr_amount = amount = line.debit
            elif line.credit > 0:
                cr_amount = amount = line.credit

            if line.amount_currency:
                amount = currency_obj.compute(cr, uid, line.currency_id.id,
                    statement.currency.id, line.amount_currency, context=ctx)
            elif (line.invoice and line.invoice.currency_id.id <> statement.currency.id):
                amount = currency_obj.compute(cr, uid, line.invoice.currency_id.id,
                    statement.currency.id, amount, context=ctx)

            type = 'general'
            if line.journal_id.type in ('sale', 'sale_refund'):
                type = 'customer'
            elif line.journal_id.type in ('purchase', 'purchase_refund'):
                type = 'supplier'
            
            statement_line_obj.create(cr, uid, {
                'name': line.name or '?',
                'amount': amount,
                'dr_amount': dr_amount,
                'cr_amount': cr_amount,
                'differ_amount': amount,
                'type': type,
                'partner_id': line.partner_id.id,
                'account_id': line.account_id.id,
                'statement_id': statement_id,
                'ref': line.ref,
                'date': line.date,
            }, context=context)
        return {'type': 'ir.actions.act_window_close'}

account_statement_from_invoice_lines()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
