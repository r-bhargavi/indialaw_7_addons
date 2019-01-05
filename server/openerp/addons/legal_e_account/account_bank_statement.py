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
import openerp.addons.decimal_precision as dp

class account_bank_statement(osv.osv):
    
    
    def create(self, cr, uid, vals, context=None):
        if 'line_ids' in vals:
            for idx, line in enumerate(vals['line_ids']):
                line[2]['sequence'] = idx + 1
        return super(account_bank_statement, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        res = super(account_bank_statement, self).write(cr, uid, ids, vals, context=context)
        account_bank_statement_line_obj = self.pool.get('legale.account.bank.statement.line')
        for statement in self.browse(cr, uid, ids, context):
            for idx, line in enumerate(statement.line_ids):
                account_bank_statement_line_obj.write(cr, uid, [line.id], {'sequence': idx + 1}, context=context)
        return res

    def _default_journal_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        journal_pool = self.pool.get('account.journal')
        journal_type = context.get('journal_type', False)
        company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'legale.account.bank.statement',context=context)
        if journal_type:
            ids = journal_pool.search(cr, uid, [('type', '=', journal_type),('company_id','=',company_id)])
            if ids:
                return ids[0]
        return False

   

#     def _get_period(self, cr, uid, context=None):
#         ctx = dict(context or {}, account_period_prefer_normal=True)
#         periods = self.pool.get('account.period').find(cr, uid, context=ctx)
#         if periods:
#             return periods[0]
#         return False

    def _currency(self, cursor, user, ids, name, args, context=None):
        res = {}
        res_currency_obj = self.pool.get('res.currency')
        res_users_obj = self.pool.get('res.users')
        default_currency = res_users_obj.browse(cursor, user,
                user, context=context).company_id.currency_id
        for statement in self.browse(cursor, user, ids, context=context):
            currency = statement.journal_id.currency
            if not currency:
                currency = default_currency
            res[statement.id] = currency.id
        currency_names = {}
        for currency_id, currency_name in res_currency_obj.name_get(cursor,
                user, [x for x in res.values()], context=context):
            currency_names[currency_id] = currency_name
        for statement_id in res.keys():
            currency_id = res[statement_id]
            res[statement_id] = (currency_id, currency_names[currency_id])
        return res


    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        line_obj = self.pool.get('account.move.line')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_total': 0.0,
                'amount_diff_total': 0.0,
                }
            
            val = val1 = cr_amount = dr_amount = total = 0.0
            cur = order.currency
            for line in order.line_ids:
                val += line.amount
                if line.bank_date >= order.from_date and line.bank_date <= order.to_date and line.reconciled:
                    total -= line.cr_amount
                    total += line.dr_amount
                    
                if line.bank_date and line.bank_date > order.to_date:
                    cr_amount += line.cr_amount
                    dr_amount += line.dr_amount
                elif not line.reconciled:
                    cr_amount += line.cr_amount
                    dr_amount += line.dr_amount
                    
                val1 += line.differ_amount
            res[order.id]['amount_total'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_diff_total'] = cur_obj.round(cr, uid, cur, val1)
            domain = [
                ('state', '=', 'valid'),
                ('bank_reco', '=', True),
                ('account_id', '=', order.journal_id.default_debit_account_id.id),
                ]
            if order.from_date:
                domain.append(('date', '<=', order.to_date))
                
            line_ids = line_obj.search(cr, uid, domain, context=context)
            for move_line_obj in line_obj.browse(cr, uid, line_ids, context=context):
                if move_line_obj.debit > 0:
                    total += move_line_obj.debit
                elif move_line_obj.credit > 0:
                    total -= move_line_obj.credit
#             total += order.balance_per_book
            res[order.id]['balance_bank'] = cur_obj.round(cr, uid, cur, total)
            res[order.id]['debit_total'] = cur_obj.round(cr, uid, cur, dr_amount)
            res[order.id]['credit_total'] = cur_obj.round(cr, uid, cur, cr_amount)
            
        return res
    
    def _get_statement(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('legale.account.bank.statement.line').browse(cr, uid, ids, context=context):
            result[line.statement_id.id] = True
        return result.keys()

    _order = "date desc, id desc"
    _name = "legale.account.bank.statement"
    _description = "Bank Statement"
    _inherit = ['mail.thread']
    _columns = {
        'name': fields.char('Reference', size=64, required=True, states={'draft': [('readonly', False)]}, readonly=True, help='if you give the Name other then /, its created Accounting Entries Move will be with same name as statement name. This allows the statement entries to have the same references than the statement itself'), # readonly for account_cash_statement
        'date': fields.date('Date', states={'confirm': [('readonly', True)]}, select=True),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True,
            readonly=True, states={'draft':[('readonly',False)]}),
        'company_id': fields.related('journal_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        'line_ids': fields.one2many('legale.account.bank.statement.line',
            'statement_id', 'Statement lines',
            states={'confirm':[('readonly', True)]}),
        
        'state': fields.selection([('draft', 'New'),
                                   ('open','Open'), # used by cash statements
                                   ('confirm', 'Closed')],
                                   'Status', required=True, readonly="1", track_visibility='always',
                                   help='When new statement is created the status will be \'Draft\'.\n'
                                        'And after getting confirmation from the bank it will be in \'Confirmed\' status.'),
        'currency': fields.function(_currency, string='Currency',
            type='many2one', relation='res.currency'),
        'account_id': fields.related('journal_id', 'default_debit_account_id', type='many2one', relation='account.account', string='Account used in this journal', readonly=True, help='used in statement reconciliation domain, but shouldn\'t be used elswhere.'),
        
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Amount Total',
            store={
                'legale.account.bank.statement': (lambda self, cr, uid, ids, c={}: ids, ['line_ids'], 10),
                'legale.account.bank.statement.line': (_get_statement, ['amount','differ_amount','reconciled','dr_amount','cr_amount','bank_date'], 10),
            },
            multi='sums'),
        'amount_diff_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Diff.Amount Total.',
            store={
                'legale.account.bank.statement': (lambda self, cr, uid, ids, c={}: ids, ['line_ids'], 10),
                'legale.account.bank.statement.line': (_get_statement, ['amount','differ_amount','reconciled','dr_amount','cr_amount','bank_date'], 10),
            },
            multi='sums'),
        
        'balance_per_book': fields.float('Balance as per company book', digits_compute=dp.get_precision('Account'),track_visibility='always'),
        
        'balance_bank': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Balance as per bank',
            store={
                'legale.account.bank.statement': (lambda self, cr, uid, ids, c={}: ids, ['journal_id', 'line_ids','balance_per_book', 'from_date', 'to_date'], 10),
                'legale.account.bank.statement.line': (_get_statement, ['amount','differ_amount','reconciled','dr_amount','cr_amount','bank_date'], 10),
            },
            multi='sums', track_visibility='always'),
        
        'debit_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Debit Total',
            store={
                'legale.account.bank.statement': (lambda self, cr, uid, ids, c={}: ids, ['journal_id', 'line_ids','balance_per_book', 'from_date', 'to_date'], 10),
                'legale.account.bank.statement.line': (_get_statement, ['amount','differ_amount','reconciled','dr_amount','cr_amount','bank_date'], 10),
            },
            multi='sums', track_visibility='always'),
           
        'credit_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Credit Total',
            store={
                'legale.account.bank.statement': (lambda self, cr, uid, ids, c={}: ids, ['journal_id', 'line_ids','balance_per_book', 'from_date', 'to_date'], 10),
                'legale.account.bank.statement.line': (_get_statement, ['amount','differ_amount','reconciled','dr_amount','cr_amount','bank_date'], 10),
            },
            multi='sums', track_visibility='always'),
                
        
    
        'from_date':  fields.date('From', states={'draft': [('readonly', False)]}, readonly=True,),
        'to_date' : fields.date('To', states={'draft': [('readonly', False)]}, readonly=True,),
        
    }

    _defaults = {
        'name': "/",
        'date': fields.date.context_today,
        'state': 'draft',
        'journal_id': _default_journal_id,
#         'period_id': _get_period,
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'legale.account.bank.statement',context=c),
    }

#    
    def onchange_journal_id(self, cr, uid, statement_id, journal_id, context=None):
        if not journal_id:
            return {}

        journal_data = self.pool.get('account.journal').read(cr, uid, journal_id, ['company_id', 'currency'], context=context)
        company_id = journal_data['company_id']
        currency_id = journal_data['currency'] or self.pool.get('res.company').browse(cr, uid, company_id[0], context=context).currency_id.id
        return {'value': {'company_id': company_id, 'currency': currency_id}}
    
    def onchange_date(self, cr, uid, ids, date, company_id, context=None):
        """
            Find the correct period to use for the given date and company_id, return it and set it in the context
        """
        res = {}
        period_pool = self.pool.get('account.period')

        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'company_id': company_id, 'account_period_prefer_normal': True})
        pids = period_pool.find(cr, uid, dt=date, context=ctx)
        if pids:
            res.update({'period_id': pids[0]})
            context.update({'period_id': pids[0]})

        return {
            'value':res,
            'context':context,
        }

    
    def button_dummy(self, cr, uid, ids, context=None):
        return True
    
    
    def button_confirm_bank(self, cr, uid, ids, context=None):
        move_line_obj = self.pool.get('account.move.line')
        for reco_obj in self.browse(cr, uid, ids, context=context):
            for line_obj in reco_obj.line_ids:
                if line_obj.reconciled:
                    move_line_obj.write(cr, uid, [line_obj.move_id.id], {'bank_date': line_obj.bank_date, 'bank_reco': line_obj.reconciled}, context=context)
        return self.write(cr, uid, ids, {'state': 'confirm'}, context=context)
    
    def button_cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)
    
    
    def import_journal_entires(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        line_obj = self.pool.get('account.move.line')
        statement_obj = self.pool.get('legale.account.bank.statement')
        statement_line_obj = self.pool.get('legale.account.bank.statement.line')
        currency_obj = self.pool.get('res.currency')
        line_date = time.strftime('%Y-%m-%d')
        
        now = time.strftime('%Y-%m-%d')

        company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        if fiscalyears:
            fiscal_obj = self.pool.get('account.fiscalyear').browse(cr, uid, fiscalyears[0], context=context)
            context.update({
                'date_from': fiscal_obj.date_start,
                })
        for rec_obj in self.browse(cr, uid, ids, context=context):
            statement_line_obj.unlink(cr, uid, [rec_line.id for rec_line in rec_obj.line_ids], context=context)
            context.update({
                'date_to': rec_obj.to_date,
                'journal_ids': [rec_obj.journal_id.id]
                })
            res = self.pool.get('account.account').read(cr, uid, [rec_obj.journal_id.default_debit_account_id.id], ['debit','credit','balance'],context=context)
            if res:
                self.write(cr, uid, [rec_obj.id], {'balance_per_book': res[0]['balance']}, context=context)
            domain = [
                ('date','<=',rec_obj.to_date),
                ('journal_id','=',rec_obj.journal_id.id), 
                ('reconcile_id','=',False), 
                ('state', '=', 'valid'),
                ('bank_reco', '=', False),
                ('account_id', '=', rec_obj.journal_id.default_debit_account_id.id),
                ]
#             if rec_obj.from_date:
#                 domain.append(('date','>=',rec_obj.from_date))
                
            line_ids = line_obj.search(cr, uid, domain, context=context)
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
    
                type = 'general'
                if line.journal_id.type in ('sale', 'sale_refund'):
                    type = 'customer'
                elif line.journal_id.type in ('purchase', 'purchase_refund'):
                    type = 'supplier'
                
                statement_line_obj.create(cr, uid, {
                    'name': line.name or '?',
                    'move_id': line.id,
                    'amount': amount,
                    'dr_amount': dr_amount,
                    'cr_amount': cr_amount,
                    'differ_amount': amount,
                    'type': type,
                    'partner_id': line.partner_id.id,
                    'account_id': line.account_id.id,
                    'statement_id': rec_obj.id,
                    'ref': line.ref,
                    'date': line.date,
                }, context=context)
        
        return True
    

account_bank_statement()

class account_bank_statement_line(osv.osv):

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        obj_partner = self.pool.get('res.partner')
        if context is None:
            context = {}
        if not partner_id:
            return {}
        part = obj_partner.browse(cr, uid, partner_id, context=context)
        if not part.supplier and not part.customer:
            type = 'general'
        elif part.supplier and part.customer:
            type = 'general'
        else:
            if part.supplier == True:
                type = 'supplier'
            if part.customer == True:
                type = 'customer'
        res_type = self.onchange_type(cr, uid, ids, partner_id=partner_id, type=type, context=context)
        if res_type['value'] and res_type['value'].get('account_id', False):
            return {'value': {'type': type, 'account_id': res_type['value']['account_id']}}
        return {'value': {'type': type}}

    def onchange_type(self, cr, uid, line_id, partner_id, type, context=None):
        res = {'value': {}}
        obj_partner = self.pool.get('res.partner')
        if context is None:
            context = {}
        if not partner_id:
            return res
        account_id = False
        line = self.browse(cr, uid, line_id, context=context)
        if not line or (line and not line[0].account_id):
            part = obj_partner.browse(cr, uid, partner_id, context=context)
            if type == 'supplier':
                account_id = part.property_account_payable.id
            else:
                account_id = part.property_account_receivable.id
            res['value']['account_id'] = account_id
        return res
    
    
    def onchange_bank_date(self, cr, uid, ids, bank_date, date, context=None):
        res = {'value': {'reconciled': False}}
        if bank_date:
            if bank_date < date:
                res['value'].update({})
                warning = {
                   'title': _('Error!'),
                   'message' : 'Bank date must be greater than transaction date'
                    }
                return {'value': {'bank_date': False, 'reconciled': False}, 'warning': warning}
            else:
                res['value']['reconciled'] = True
        
        return res
    
    
    _order = "date asc"
    _name = "legale.account.bank.statement.line"
    _description = "Bank Statement Line"
    _columns = {
        'name': fields.char('OBI', required=True, help="Originator to Beneficiary Information"),
        'move_id':  fields.many2one('account.move.line', 'Move Line'),
        'date': fields.date('Date', required=True),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'cr_amount': fields.float('Credit', digits_compute=dp.get_precision('Account')),
        'dr_amount': fields.float('Debit', digits_compute=dp.get_precision('Account')),
        'type': fields.selection([
            ('supplier','Supplier'),
            ('customer','Customer'),
            ('general','General')
            ], 'Type', required=True),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'account_id': fields.many2one('account.account','Account',
            required=True),
        'statement_id': fields.many2one('legale.account.bank.statement', 'Statement',
            select=True, required=True, ondelete='cascade'),
        'journal_id': fields.related('statement_id', 'journal_id', type='many2one', relation='account.journal', string='Journal', store=True, readonly=True),
        'analytic_account_id': fields.many2one('account.analytic.account', 'Analytic Account'),
        'move_ids': fields.many2many('account.move',
            'account_bank_statement_line_move_rel', 'statement_line_id','move_id',
            'Moves'),
        'ref': fields.char('Reference', size=32),
        'note': fields.text('Notes'),
        'sequence': fields.integer('Sequence', select=True, help="Gives the sequence order when displaying a list of bank statement lines."),
        'company_id': fields.related('statement_id', 'company_id', type='many2one', relation='res.company', string='Company', store=True, readonly=True),
        'differ_amount': fields.float('Diff. Amount', digits_compute=dp.get_precision('Account')),
        'bank_date':  fields.date('Bank Date'),
        'reconciled': fields.boolean('Reconciled'),
    }
    _defaults = {
        'name': lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'legale.account.bank.statement.line'),
        'date': lambda self,cr,uid,context={}: context.get('date', fields.date.context_today(self,cr,uid,context=context)),
        'type': 'general',
    }
    
    
    
    def _check_bank_reco_date(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
             if line.bank_date and line.bank_date < line.statement_id.from_date:
                return False
        return True

    _constraints = [
        (_check_bank_reco_date, 'The Reco. Date earlier than transaction date is not allowed .', ['bank_date']),
    ]
    

account_bank_statement_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
