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
from datetime import datetime, timedelta
from lxml import etree

from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp.tools import float_compare
import openerp.exceptions
from openerp import SUPERUSER_ID
from openerp.osv import expression

account_codes = [[4250,205651],[50000,2054228],[10000,2054081],[10000,2054288],[777500,2054059],[17500,2054059],[202013,2054154],[6050100,205597],[180000,2054074],[227500,205599],[37500,2054166],[60000,2054061],[12000,2054089],[50000,2054059],[15000,2054129],[50000,1001],[13467,2054019],[100000,2054065],[250000,2054044],[62500,2054279],[31900,205599],[23180,205602],[100000,2054005],[175000,2054017],[15000,2054272],[6875,205651],[15000,2054069],[495159,2054040],[2040,2054074],[6250,205604],[8000,2054081],[3355340,2054055],[37500,2054159],[120000,2054024],[44250,205597],[50750,205597],[14000,205597],[8750,205597],[50000,2054155],[40000,2054173],[20000,2054191],[22500,2054271],[44500,2054275],[30000,2054139],[50000,2054236],[50000,2054168],[20000,2054174],[20000,2054103],[75400,2054061],[256500,2054323],[50000,2054209],[8000,205526],[20000,2054002],[21000,205651],[20000,2054176],[20000,2054177],[60000,2054051],[15000,2054321],[20000,2054178],[20000,2054197],[20000,2054179],[180000,2054172],[20000,2054180],[3000,2054059],[17000,2054110],[40000,2054093],[20000,2054181],[85000,2054130],[25000,2054003],[5000,2054316],[250000,205553],[50000,1001],[20000,2054182],[80000,2054183],[345000,2054039],[20000,205565],[100000,2054212],[20000,2054117],[500,205572],[215000,2054203],[30000,2054111],[277500,2054234],[20000,2054184],[25000,2054185],[793037,2054019],[35000,2054041],[50000,2054308],[20000,205584],[795860,205586],[20000,2054286],[35000,2054044],[622250,205597],[134000,205599],[60000,205602],[11850,205604],[116000,2054005],[50000,2054277],[20000,2054187],[100000,2054113],[25000,2054188],[20000,2054189],[100000,205611],[20000,2054190],[233000,2054001],[60000,2054200],[50000,2054063],[25000,2054099],[55000,205597],[6250,205604],[33625,205651],[5000,205572],[250000,2054027],[71500,2054039],[12000,2054228],[195000,2054061],[23500,2054139],[150000,2054033],[8000,2054123],[85000,2054101],[30000,2054114],[62000,2054117],[275000,2054019],[52500,205586],[12000,2054286],[655500,205599],[290000,2054001],[56000,2054228],[5000,205651],[30000,205599],[52200,2054228],[62500,2054228],[90000,2054228],[10000,2054089],[6500,2054005],[60000,2054061],[7500,2054123],[89500,205599],[8000,205602],[75000,2054142]]


class account_invoice(osv.osv):
    
    def _compute_bad_debts(self, cr, uid, ids, name, args, context=None):
        result = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            src = []
            bad_debts = 0.0
            if invoice.payment_ids:
                for m in invoice.payment_ids:
                    if m.journal_id.id ==  invoice.company_id.bad_debts_journal_id.id:
                        bad_debts += m.credit
            result[invoice.id] = bad_debts
        return result
    
    
    def _compute_next_followup_date(self, cr, uid, ids, name, args, context=None):
        result = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            result[invoice.id] = {
                'next_followup_date': False,
                }
            if invoice.invoice_followup_ids:
                line = len(invoice.invoice_followup_ids) - 1
                result[invoice.id]['next_followup_date'] = invoice.invoice_followup_ids[line].next_date
        return result
    
    
    def _get_invoice(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.followup').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
    
    
    
    _inherit = 'account.invoice'
    _rec_name = 'legale_number'     
    _columns = {
        'subject_line':fields.text('Subject Line'),
        'legale_number':fields.char('Invoice Number',char=100, track_visibility='always'),
        'invoice_template':fields.selection([
            ('general','General'),
            ('vodafone','Vodafone'),
            ('india_llp','INDIALAW LLP'),
            ('hdfc', 'HDFC'),
            ('india_llp1','Indialaw LLP'),
            ], 'Invoice Template'),
        'case_id':fields.many2one('case.sheet','Case Sheet'),
        'assignee_id': fields.related('case_id', 'assignee_id', type='many2one', relation='hr.employee', string='Assignee', readonly=True),
        'branch_id': fields.related('case_id', 'ho_branch_id', type='many2one', relation='ho.branch', string='Office', store=True),
        'consolidated_id':fields.many2one('consolidated.bill','Consolidated Bill No.'),
        'company_ref_no':fields.related('case_id','company_ref_no',type='char',size=40,string='Company Ref #'),
        'flg_tds_note':fields.boolean('TDS Note'),
        'flg_pan_no':fields.boolean('Comapny PAN Number'),
        'assignee_id': fields.related('case_id', 'assignee_id', type='many2one', relation='hr.employee', string='Assignee', readonly=True),
        'division_id': fields.related('case_id', 'division_id', type='many2one', relation='hr.department', string='Department/Division', readonly=True),
        'client_service_manager_id': fields.related('case_id', 'client_service_manager_id', type='many2one', relation='hr.employee', string='Client Relationship Manager', readonly=True, store=True),
        'client_service_executive_id': fields.related('case_id', 'client_service_executive_id', type='many2one', relation='hr.employee', string='Client Service Manager', readonly=True, store=True),
        
        'invoice_followup_ids': fields.one2many('account.invoice.followup', 'invoice_id', 'Invoice Followup'),
        
        'bad_debts': fields.function(_compute_bad_debts, type="float", string='Bad Debts', digits_compute=dp.get_precision('Account'),),
        
        'next_followup_date': fields.function(_compute_next_followup_date, type="date", string='Next Followup Date', store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_followup_ids'], 10),
                'account.invoice.followup': (_get_invoice, ['date', 'next_date'], 10),
            },
            multi='sums', help="Next Followup Date.",  track_visibility='always'),
        
        'due_date_over': fields.boolean('Due Date Over', track_visibility='onchange'),
        'due_days_string':fields.char('Aging'),
        'due_date_red': fields.boolean('Due Date Red'),
        'partially_paid': fields.boolean('Partially Paid')
        }
    _defaults = {
        'legale_number':'',
        'invoice_template':'general',
        'due_date_over': False,
        'due_date_red': False,
        'due_days_string': '',
        }
    _order = "legale_number ASC" 
#     _order = "date_invoice desc"
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('order_by_inv_date', False):
            order = 'date_invoice desc'
        res = super(account_invoice, self).search(cr, uid, args, offset, limit, order, context, count)
        return res
    
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}

        res = super(account_invoice, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)

        doc = etree.XML(res['arch'])
        if view_type == 'tree':
            partner_string = _('Client Name')
            if context.get('type', 'out_invoice') in ('in_invoice', 'in_refund'):
                partner_string = _('Supplier')
                for node in doc.xpath("//field[@name='reference']"):
                    node.set('invisible', '0')
            for node in doc.xpath("//field[@name='partner_id']"):
                node.set('string', partner_string)
            res['arch'] = etree.tostring(doc)
        return res
    
    
    
    def invoice_due_date_scheduler(self, cr, uid, context=None):
        invoice_ids = self.search(cr, uid, [('state', '=', 'open'),('type','=','out_invoice'),('consolidated_id', '=', False)], context=context)
        for invoice_obj in self.browse(cr, uid, invoice_ids, context=context):
            due_date = (datetime.strptime(invoice_obj.date_invoice, '%Y-%m-%d') + timedelta(days=7)).strftime('%Y-%m-%d')
            due_days_string = ''
            today = time.strftime('%Y-%m-%d')
            days = (datetime.strptime(today, '%Y-%m-%d') - datetime.strptime(due_date, '%Y-%m-%d')).days
            vals = {}
            if days > 0:
                due_days_string = str(days) + ' days over due'
                vals.update({'due_days_string': due_days_string})
                if not invoice_obj.invoice_followup_ids:
                    self.pool.get('account.invoice.followup').create(cr, uid, {
                        'name': 'Missing Followup(System Generated Messages)',
                        'date': today,
                        'next_date': today,
                        'state': 'communicate',
                        'invoice_id': invoice_obj.id,
                        'due_next_date_over': True,
                        }, context=context)
                if days >= 30:
                    vals.update({'due_date_red': True})
            else:
                due_days_string = str(abs(days)) + ' days to over due'
                vals.update({'due_days_string': due_days_string})
            if today >= due_date:
                vals.update({'due_date_over': True})
            self.write(cr, uid, [invoice_obj.id], vals, context=context)
            
        invoice_ids = self.search(cr, uid, [('state', '!=', 'open'),('type','=','out_invoice'),('consolidated_id', '=', False)], context=context)
        self.write(cr, uid, invoice_ids, {'due_date_over': False, 'due_date_red': False, 'due_days_string': ''}, context=context)
        return True
    
    def account_line_create(self, cr, uid, ids, context=None):
        for account in account_codes:
            account_ids = self.pool.get('account.account').search(cr, uid, [('code', '=', account[1])], context=context)
            if account_ids:
                field_names = ['credit', 'debit', 'balance']
                context = {'lang': 'en_US', 'tz': 'Asia/Kolkata', 'uid': 1, 'active_model': 'account.chart', 'state': 'posted', 'periods': [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],  'fiscalyear': 2}
                res = self.pool.get('account.account').__compute(cr, uid, account_ids, field_names, None, context, '', ())
        return True
    
    
    def invoice_pay_customer(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')
        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Pay Invoice"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'payment_expected_currency': inv.currency_id.id,
                'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(inv.partner_id).id,
                'default_amount': inv.type in ('out_refund', 'in_refund') and -inv.residual or inv.residual,
                'default_reference': inv.name,
                'default_invoice_ids': [(6, 0, ids)],
                'close_after_process': True,
                'invoice_type': inv.type,
                'invoice_id': inv.id,
                'default_type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment',
                'type': inv.type in ('out_invoice','out_refund') and 'receipt' or 'payment'
            }
        }
        
        
    
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        for line in self.browse(cr, uid, ids, context=context):
            res.append((line.id,line.legale_number))
        return res  
    
 
    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, ['|',('number','ilike',name), ('legale_number','ilike',name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)      
    
    def invoice_validate(self, cr, uid, ids, context=None):
        case_invoice_pool = self.pool.get('case.sheet.invoice')
        case_inv_ids = case_invoice_pool.search(cr, uid, [('invoice_id','in',ids)])
        case_inv_total = case_invoice_pool.get_total_amount(cr, uid, case_inv_ids)
        inv_total = 0.00
        for inv in self.browse(cr, uid, ids):
            inv_total += inv.amount_total
        if inv_total != case_inv_total and len(case_inv_ids)>0:
            raise openerp.exceptions.Warning(_('Cost Details related to this Invoice are Changed. Total Amount should be ' + str(case_inv_total)))    
        res = super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        obj = self.browse(cr, uid, ids and ids[0])
        if obj and obj.consolidated_id:
            number = obj.consolidated_id.name
        elif obj.case_id and obj.case_id.name != obj.legale_number:
            return res    
        else:
            number = self.pool.get('ir.sequence').get(cr, uid, 'account.invoice.legale') or '/'
            fl_no = self.read(cr, uid, ids and ids[0], ['legale_number'], context=context)['legale_number']
            number = (fl_no!='' and fl_no+'/' or '')+str(number)
        self.write(cr, uid, ids and ids[0], {'legale_number':number})
        return res
    
    def invoice_print(self, cr, uid, ids, context=None):
        '''
        This function prints the invoice and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        self.write(cr, uid, ids, {'sent': True}, context=context)
        invoice = self.browse(cr, uid, ids[0])
        datas = {
             'ids': ids,
             'model': 'account.invoice',
             'form': self.read(cr, uid, ids[0], context=context)
        }
        if invoice.invoice_template=='general':        
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.invoice.legale2',
                'datas': datas,
                'name':self.read(cr, uid, ids[0],['legale_number'])['legale_number'],
                'nodestroy' : True
            }
        elif invoice.invoice_template=='vodafone':        
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.invoice.legale_vodafone',
                'datas': datas,
                'name':self.read(cr, uid, ids[0],['legale_number'])['legale_number'],
                'nodestroy' : True
            }
        elif invoice.invoice_template=='india_llp':        
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.invoice.legale_india_llp',
                'datas': datas,
                'name':self.read(cr, uid, ids[0],['legale_number'])['legale_number'],
                'nodestroy' : True
            } 
            
        elif invoice.invoice_template=='hdfc':        
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.invoice.legale_hdfc_2',
                'datas': datas,
                'name':self.read(cr, uid, ids[0],['legale_number'])['legale_number'],
                'nodestroy' : True
            }
        elif invoice.invoice_template== 'india_llp1':
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.invoice.legale_india_llp_3',
                'datas': datas,
                'name':self.read(cr, uid, ids[0],['legale_number'])['legale_number'],
                'nodestroy' : True
            }
            
    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'internal_number': False}, context=context)
        case_invoice_pool = self.pool.get('case.sheet.invoice')
        retvals = super(account_invoice, self).action_cancel(cr, uid, ids, context=context)     
        case_inv_ids = case_invoice_pool.search(cr, uid, [('invoice_id','in',ids)])
        case_invoice_pool.cancel_invoice_case_sheet(cr, uid, case_inv_ids, context=context)
        return retvals
        
    # go from canceled state to draft state
    def action_cancel_draft(self, cr, uid, ids, *args):
        case_invoice_pool = self.pool.get('case.sheet.invoice')
        retvals = super(account_invoice, self).action_cancel_draft(cr, uid, ids, args)
        case_inv_ids = case_invoice_pool.search(cr, uid, [('invoice_id','in',ids)])
        case_invoice_pool.draft_invoice_case_sheet(cr, uid, case_inv_ids)
        return retvals        
    
    def unlink(self, cr, uid, ids, context=None):
        case_invoice_pool = self.pool.get('case.sheet.invoice')
        case_inv_ids = case_invoice_pool.search(cr, uid, [('invoice_id','in',ids)])
        retvals = super(account_invoice, self).unlink(cr, uid, ids, context=context)
        case_invoice_pool.cancel_invoice_case_sheet(cr, uid, case_inv_ids, context=context)
        case_invoice_pool.unlink(cr, uid, case_inv_ids, context=context)        
        return retvals
        
    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(account_invoice, self).line_get_convert(cr, uid, x, part, date, context=context)
        res.update({
            'office_id': x.get('office_id', False),
            'case_id': x.get('case_id', False),
            'department_id':  x.get('department_id', False),
            })
        return res
    
    
account_invoice()


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line' 
    
    _columns = {
        'division_id': fields.many2one('hr.department', string='Department/Division'),
        }
    
    def move_line_get_item(self, cr, uid, line, context=None):
        res = super(account_invoice_line, self).move_line_get_item(cr, uid, line, context=context)
        res.update({
            'office_id': line.office_id and line.office_id.id or False, 
            'case_id': line.invoice_id.case_id and line.invoice_id.case_id.id or False,
            'department_id': line.invoice_id.case_id and line.invoice_id.case_id.division_id and line.invoice_id.case_id.division_id.id or False,
            } )
        if line.invoice_id.type == 'in_invoice':
            res.update({
            'office_id': line.office_id and line.office_id.id or False, 
            'department_id': line.division_id and line.division_id.id or False,
            } )
        return res
    
account_invoice_line()


class account_invoice_followup(osv.osv):
    _name = 'account.invoice.followup'
    _description = 'Account Invoice Follow-up'
    _order = "date"
    
    
    def _get_invoice_amount(self, cr, uid, ids, field_name, args, context=None):
        res={}
        uid = SUPERUSER_ID
        for obj in self.browse(cr, uid, ids, context=context):
            res[obj.id] = obj.invoice_id.amount_total
        return res
    
    _columns = {
        'date': fields.date('Date'),
        'create_date': fields.datetime('Create Date'),
        'name': fields.text('Description'),
        'next_date': fields.date('Next Date'),
        'invoice_id': fields.many2one('account.invoice', 'Invoice'),
        'state': fields.selection([('communicate', 'To Communicate'),('communicated', 'Communicated'),('completed', 'Completed')], 'Status'),
        'communicate_via': fields.selection([('email', 'Email'),('phone', 'Phone'),('meeting', 'Meeting')], 'Communicated Via'),
        
        'client_service_manager_id': fields.related('invoice_id', 'client_service_manager_id', type='many2one', relation='hr.employee', string='Client Relationship Manager', readonly=True, store=True),
        'due_next_date_over': fields.boolean('Due Date Over'),
        'partner_id': fields.related('invoice_id', 'partner_id', type='many2one', relation='res.partner', string='Client', readonly=True, store=True),
        
        'date_invoice': fields.related('invoice_id', 'date_invoice', type='date', string='Invoice Date', readonly=True),
        'division_id': fields.related('invoice_id', 'division_id', type='many2one', relation='hr.department', string='Department', readonly=True),
        'branch_id': fields.related('invoice_id', 'branch_id', type='many2one', relation='ho.branch', string='Office', readonly=True),
        'contact_partner1_id': fields.related('invoice_id', 'case_id', 'contact_partner1_id', type='many2one', relation='res.partner', string='Contact Person 1', readonly=True),
        'due_days_string':fields.related('invoice_id', 'due_days_string', type='char', string='Aging', readonly=True),
        'amount': fields.function(_get_invoice_amount, type='float', string='Amount'),
        'remark_id': fields.many2one('legal.followup.remark', 'Followup Remarks')
        }
    
    _defaults = {
        'due_next_date_over':  False
        }
    
    
    def write(self, cr, uid, ids, vals, context=None):
        for follow_obj in self.browse(cr, uid, ids, context=context):
            if follow_obj.name == 'Missing Followup(System Generated Messages)' and vals.get('name', False):
                vals.update({'due_next_date_over': False})
        res = super(account_invoice_followup, self).write(cr, uid, ids, vals, context=context)
        return res
    
    def next_date_scheduler(self, cr, uid, context=None):
        followup_ids = self.search(cr, uid, [('state', '=', 'communicate'),('invoice_id.state', '=', 'open')], context=context)
        invoice_ids = [follow_obj.invoice_id.id for follow_obj in self.browse(cr, uid, followup_ids, context=context)]
        for invoice_obj in self.pool.get('account.invoice').browse(cr, uid, invoice_ids, context=context):
            if invoice_obj.next_followup_date and time.strftime('%Y-%m-%d') >= invoice_obj.next_followup_date:
                for line in invoice_obj.invoice_followup_ids:
                    if line.next_date == invoice_obj.next_followup_date:
                        self.write(cr, uid, [line.id], {'due_next_date_over': True}, context=context)
                    else:
                        if line.name != 'Missing Followup(System Generated Messages)':
                            self.write(cr, uid, [line.id], {'due_next_date_over': False}, context=context)
        
        followup_ids = self.search(cr, uid, [('state', '!=', 'communicate'),('due_next_date_over', '=', True)], context=context)
        self.write(cr, uid, followup_ids, {'due_next_date_over': False}, context=context)
        return True
    

account_invoice_followup()
    



def resolve_o2m_operations(cr, uid, target_osv, operations, fields, context):
    results = []
    for operation in operations:
        result = None
        if not isinstance(operation, (list, tuple)):
            result = target_osv.read(cr, uid, operation, fields, context=context)
        elif operation[0] == 0:
            # may be necessary to check if all the fields are here and get the default values?
            result = operation[2]
        elif operation[0] == 1:
            result = target_osv.read(cr, uid, operation[1], fields, context=context)
            if not result: result = {}
            result.update(operation[2])
        elif operation[0] == 4:
            result = target_osv.read(cr, uid, operation[1], fields, context=context)
        if result != None:
            results.append(result)
    return results

class account_voucher(osv.osv):
    _inherit = 'account.voucher'
    
    
    def _get_writeoff_amount(self, cr, uid, ids, name, args, context=None):
        if not ids: return {}
        currency_obj = self.pool.get('res.currency')
        res = {}
        debit = credit = 0.0
        for voucher in self.browse(cr, uid, ids, context=context):
            sign = voucher.type == 'payment' and -1 or 1
            for l in voucher.line_dr_ids:
                debit += l.amount
            for l in voucher.line_cr_ids:
                credit += l.amount
            currency = voucher.currency_id or voucher.company_id.currency_id
            tds_amount = 0.0
            if voucher.tds_amount and voucher.tds_amount>0:
                tds_amount = voucher.tds_amount
            res[voucher.id] =  currency_obj.round(cr, uid, currency, voucher.amount + tds_amount - sign * (credit - debit))
        return res
    
    def _cal_associate_payment(self, cr, uid, ids, name, args, context=None):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            for line in voucher.line_cr_ids:
                if line.amount>0:
                    if line.move_line_id and line.move_line_id.move_id:
                        inv_ids = self.pool.get('account.invoice').search(cr, uid, [('move_id','=',line.move_line_id.move_id.id)])
                        for inv in self.pool.get('account.invoice').browse(cr, uid, inv_ids):
                            if inv.case_id:
                                for pay in inv.case_id.associate_payment_lines:
                                    if not pay.invoiced:                                        
                                        res[voucher.id] =  True
            if not res.has_key(voucher.id):
                res[voucher.id] = False  
        return res 
    
    _columns = {
        'tds_amount':fields.float('TDS Amount', digits_compute=dp.get_precision('Account')),
        'tds_account_id':fields.many2one('account.account', 'TDS Account', help="The TDS account used for this invoice TDS Amount."),
        'writeoff_amount': fields.function(_get_writeoff_amount, string='Difference Amount', type='float', readonly=True, help="Computed as the difference between the amount stated in the voucher and the sum of allocation on the voucher lines."),
        'flg_associate_payment':fields.function(_cal_associate_payment, string="Associate Payment Reminder", type="boolean"),
        'consolidated_id':fields.many2many('consolidated.bill','voucher_bill_rel', 'voucher_id', 'bill_id', 'Consolidated Bill No.'),
        'invoice_ids': fields.many2many('account.invoice', 'voucher_invoice_rel', 'voucher_id', 'invoice_id', 'Invoices')
        }
    
    _defaults = {
        'flg_associate_payment':False,
        }
    
    
    
    def proforma_voucher(self, cr, uid, ids, context=None):
        res = super(account_voucher, self).proforma_voucher(cr, uid, ids, context=context)
        for voucher in self.browse(cr, uid, ids, context=context):
            for invoice_obj in voucher.invoice_ids:
                lines = []
                if invoice_obj.state == 'paid':
                    self.pool.get('account.invoice').write(cr, uid, [invoice_obj.id], {'partially_paid': False})
                else:
                    self.pool.get('account.invoice').write(cr, uid, [invoice_obj.id], {'partially_paid': True})
                    
        return res
    
    
    
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        if context is None: context = {}

        res = super(account_voucher, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])

        if context.get('employee_pay', False):
            nodes = doc.xpath("//field[@name='partner_id']")
            for node in nodes:
                node.set('context', "{'employee_pay': True}")
        res['arch'] = etree.tostring(doc)
        return res
    
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
            args += [('partner_id', 'in', partner_ids)]
            
            
        return super(account_voucher, self).search(cr, uid, args, offset, limit, order, context, count)
    
        
    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, tds=0.0, consolidated_id=False, invoice_ids=False, context=None):
        if tds and not type(tds) is dict:
            amount +=tds
        if not journal_id:
            return {}
        if context is None:
            context = {}
        
        if context.get('journal_id_change', False):
            if not (consolidated_id and consolidated_id[0][2]) and not (invoice_ids and invoice_ids[0][2]):
                return {}
        #TODO: comment me and use me directly in the sales/purchases views
        res = self.basic_onchange_partner(cr, uid, ids, partner_id, journal_id, ttype, context=context)
        if ttype in ['sale', 'purchase']:
            return res
        
        if context.get('return_null', False):
            return res 
        ctx = context.copy()
        # not passing the payment_rate currency and the payment_rate in the context but it's ok because they are reset in recompute_payment_rate
        ctx.update({'date': date})
        vals = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, consolidated_id, invoice_ids, context=ctx)
        vals2 = self.recompute_payment_rate(cr, uid, ids, vals, currency_id, date, ttype, journal_id, amount, context=context)
        for key in vals.keys():
            res[key].update(vals[key])
        for key in vals2.keys():
            res[key].update(vals2[key])
        #TODO: can probably be removed now
        #TODO: onchange_partner_id() should not returns [pre_line, line_dr_ids, payment_rate...] for type sale, and not 
        # [pre_line, line_cr_ids, payment_rate...] for type purchase.
        # We should definitively split account.voucher object in two and make distinct on_change functions. In the 
        # meanwhile, bellow lines must be there because the fields aren't present in the view, what crashes if the 
        # onchange returns a value for them
        if ttype == 'sale':
            del(res['value']['line_dr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
        elif ttype == 'purchase':
            del(res['value']['line_cr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
        
        
        return res 
    
    
    
    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, tds=0.0, consolidated_id=False, invoice_ids=False, context=None):
        if context is None:
            context = {}
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        account_id = journal.default_credit_account_id or journal.default_debit_account_id
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id

        vals = {'value':{} }
        if ttype in ('sale', 'purchase'):
            vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
            vals['value'].update({'tax_id':tax_id,'amount': amount})
        currency_id = False
        if journal.currency:
            currency_id = journal.currency.id
        else:
            currency_id = journal.company_id.currency_id.id
        vals['value'].update({'currency_id': currency_id, 'payment_rate_currency_id': currency_id})
        #in case we want to register the payment directly from an invoice, it's confusing to allow to switch the journal 
        #without seeing that the amount is expressed in the journal currency, and not in the invoice currency. So to avoid
        #this common mistake, we simply reset the amount to 0 if the currency is not the invoice currency.
        if context.get('payment_expected_currency') and currency_id != context.get('payment_expected_currency'):
            vals['value']['amount'] = 0
            amount = 0
        if partner_id:
            res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, tds, consolidated_id, invoice_ids, context)
            for key in res.keys():
                vals[key].update(res[key])
        return vals
    
    
    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, consolidated_id=False, invoice_ids=False, context=None):
        """
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        
        def _remove_noise_in_o2m():
            """if the line is partially reconciled, then we must pay attention to display it only once and
                in the good o2m.
                This function returns True if the line is considered as noise and should not be displayed
            """
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False

        if context is None:
            context = {}
            
        context_multi_currency = context.copy()

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')

        #set default values
        default = {
            'value': {'line_dr_ids': [] ,'line_cr_ids': [] ,'pre_line': False,},
        }

        #drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])]) or False
        if line_ids:
            line_pool.unlink(cr, uid, line_ids)

        if not partner_id or not journal_id:
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        currency_id = currency_id or journal.company_id.currency_id.id

        total_credit = 0.0
        total_debit = 0.0
        account_type = 'receivable'
        if ttype == 'payment':
            account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            account_type = 'receivable'
        if not context.get('move_line_ids', False):
            if context.get('type', True) == 'receipt':
                if consolidated_id and consolidated_id[0][2]:
                    ids += move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id),('invoice.consolidated_id', 'in', consolidated_id[0][2])], context=context)   
                  
                if invoice_ids and invoice_ids[0][2]:
                    ids += move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id),('invoice','in', invoice_ids[0][2])], context=context)
                 
                if  not context.get('consolidated_id', False) and not context.get('invoice_ids', False) and not (consolidated_id and consolidated_id[0][2])  and not (invoice_ids and invoice_ids[0][2]):
                    ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)], context=context)
                    
                credit_line_ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id), ('debit','=', 0.00), ('credit','>=', 0.00)], context=context)
                
                ids += credit_line_ids
            else:
                ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)], context=context)
        else:
            ids = context['move_line_ids']
        
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        move_line_found = False

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

        #compute the total debit/credit and look for a matching open amount or invoice
        for line in account_move_lines:
            if _remove_noise_in_o2m():
                continue

            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_line_found = line.id
                    break
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_line_found = line.id
                    break
                #otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit or 0.0
                total_debit += line.debit or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_line_found = line.id
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0

        #voucher line creation
        for line in account_move_lines:

            if _remove_noise_in_o2m():
                continue

            if line.currency_id and currency_id == line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0, context=context_multi_currency)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual), context=context_multi_currency)
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': (move_line_found == line.id) and min(abs(price), amount_unreconciled) or 0.0,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
            }
            #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            if not move_line_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if ttype == 'payment' and len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif ttype == 'receipt' and len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
        return default
         
        
    
    def tds_move_line_get(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None): 
        currency_obj = self.pool.get('res.currency')
        move_line = {}

        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        current_currency_obj = voucher.currency_id or voucher.journal_id.company_id.currency_id

        if not currency_obj.is_zero(cr, uid, current_currency_obj, line_total):
            diff = line_total
            
            sign = voucher.type == 'payment' and -1 or 1
            credit = voucher.type == 'payment' and diff or 0.0
            debit = voucher.type == 'payment' and 0.0 or False
            move_line = {
                'name': 'TDS',
                'account_id': voucher.tds_account_id.id,
                'partner_id': voucher.partner_id.id,
                'date': voucher.date,
                'move_id':move_id,
                'credit': credit,
                'debit': debit,
                'amount_currency': company_currency <> current_currency and (sign * -1 * voucher.tds_amount) or 0.0,
                'currency_id': company_currency <> current_currency and current_currency or False,
                'analytic_account_id': voucher.analytic_id and voucher.analytic_id.id or False,
            }
        return move_line
            
    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, context), context)
            move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)

            # Create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, context)
                
            # Create the TDS line if needed
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)

        return True

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, tds=0.0, consolidated_id=False, invoice_ids=False, context=None):
        if type(tds) == type({}):
            context = tds
            tds = 0.0
        if context is None:
            context = {}
        if context.get('amount_change', True) and context.get('type', True) == 'receipt':
            if not (consolidated_id and consolidated_id[0][2]) and not (invoice_ids and invoice_ids[0][2]):
                return {}
        ctx = context.copy()
        ctx.update({'date': date})
        #read the voucher rate with the right date in the context
        currency_id = currency_id or self.pool.get('res.company').browse(cr, uid, company_id, context=ctx).currency_id.id
        voucher_rate = self.pool.get('res.currency').read(cr, uid, currency_id, ['rate'], context=ctx)['rate']
        ctx.update({
            'voucher_special_currency': payment_rate_currency_id,
            'voucher_special_currency_rate': rate * voucher_rate})
        res = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount+tds, currency_id, ttype, date,consolidated_id, invoice_ids, context=ctx)
        vals = self.onchange_rate(cr, uid, ids, rate, amount+tds, currency_id, payment_rate_currency_id, company_id, context=ctx)
        for key in vals.keys():
            res[key].update(vals[key])
        return res

    def onchange_line_ids(self, cr, uid, ids, line_dr_ids, line_cr_ids, amount, voucher_currency, ttype, tds=0.0, context=None):
        if type(tds) == type({}):
            context = tds
            tds = 0.0
        context = context or {}
        if not line_dr_ids and not line_cr_ids:
            return {'value':{'writeoff_amount': 0.0}}
        line_osv = self.pool.get("account.voucher.line")
        line_dr_ids = resolve_o2m_operations(cr, uid, line_osv, line_dr_ids, ['amount'], context)
        line_cr_ids = resolve_o2m_operations(cr, uid, line_osv, line_cr_ids, ['amount'], context)
        #compute the field is_multi_currency that is used to hide/display options linked to secondary currency on the voucher
        is_multi_currency = False
        #loop on the voucher lines to see if one of these has a secondary currency. If yes, we need to see the options
        for voucher_line in line_dr_ids+line_cr_ids:
            line_id = voucher_line.get('id') and self.pool.get('account.voucher.line').browse(cr, uid, voucher_line['id'], context=context).move_line_id.id or voucher_line.get('move_line_id')
            if line_id and self.pool.get('account.move.line').browse(cr, uid, line_id, context=context).currency_id:
                is_multi_currency = True
                break
        return {'value': {'writeoff_amount': self._compute_writeoff_amount(cr, uid, line_dr_ids, line_cr_ids, amount+tds, ttype), 'is_multi_currency': is_multi_currency}}
        
    def voucher_move_line_create(self, cr, uid, voucher_id, line_total, move_id, company_currency, current_currency, context=None):
        '''
        Create one account move line, on the given account move, per voucher line where amount is not 0.0.
        It returns Tuple with tot_line what is total of difference between debit and credit and
        a list of lists with ids to be reconciled with this format (total_deb_cred,list_of_lists).

        :param voucher_id: Voucher id what we are working with
        :param line_total: Amount of the first line, which correspond to the amount we should totally split among all voucher lines.
        :param move_id: Account move wher those lines will be joined.
        :param company_currency: id of currency of the company to which the voucher belong
        :param current_currency: id of currency of the voucher
        :return: Tuple build as (remaining amount not allocated on voucher lines, list of account_move_line created in this method)
        :rtype: tuple(float, list of int)
        '''
        if context is None:
            context = {}
        move_line_obj = self.pool.get('account.move.line')
        currency_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        tot_line = line_total
        rec_lst_ids = []

        date = self.read(cr, uid, voucher_id, ['date'], context=context)['date']
        ctx = context.copy()
        ctx.update({'date': date})
        voucher = self.pool.get('account.voucher').browse(cr, uid, voucher_id, context=ctx)
        voucher_currency = voucher.journal_id.currency or voucher.company_id.currency_id
        ctx.update({
            'voucher_special_currency_rate': voucher_currency.rate * voucher.payment_rate ,
            'voucher_special_currency': voucher.payment_rate_currency_id and voucher.payment_rate_currency_id.id or False,})
        prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Account')
        for line in voucher.line_ids:
            #create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line was not having debit = credit = 0 (which is a legal value)
            if not line.amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
                continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context, so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(cr, uid, line.untax_amount or line.amount, voucher.id, context=ctx)
            # if the amount encoded in voucher is equal to the amount unreconciled, we need to compute the
            # currency rate difference
            if line.amount == line.amount_unreconciled:
                if not line.move_line_id:
                    raise osv.except_osv(_('Wrong voucher line'),_("The invoice you are willing to pay is not valid anymore."))
                sign = voucher.type in ('payment', 'purchase') and -1 or 1
                currency_rate_difference = sign * (line.move_line_id.amount_residual - amount)
            else:
                currency_rate_difference = 0.0
            move_line = {
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'name': line.name or '/',
                'account_id': line.account_id.id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'currency_id': line.move_line_id and (company_currency <> line.move_line_id.currency_id.id and line.move_line_id.currency_id.id) or False,
                'analytic_account_id': line.account_analytic_id and line.account_analytic_id.id or False,
                'quantity': 1,
                'credit': 0.0,
                'debit': 0.0,
                'date': voucher.date
            }
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'

            if (line.type=='dr'):
                tot_line += amount
                move_line['debit'] = amount
            else:
                tot_line -= amount
                move_line['credit'] = amount

            if voucher.tax_id and voucher.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher.tax_id.id,
                })

            if move_line.get('account_tax_id', False):
                tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                if not (tax_data.base_code_id and tax_data.tax_code_id):
                    raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))

            # compute the amount in foreign currency
            foreign_currency_diff = 0.0
            amount_currency = False
            if line.move_line_id:
                # We want to set it on the account move line as soon as the original line had a foreign currency
                if line.move_line_id.currency_id and line.move_line_id.currency_id.id != company_currency:
                    # we compute the amount in that foreign currency.
                    if line.move_line_id.currency_id.id == current_currency:
                        # if the voucher and the voucher line share the same currency, there is no computation to do
                        sign = (move_line['debit'] - move_line['credit']) < 0 and -1 or 1
                        amount_currency = sign * (line.amount)
                    else:
                        # if the rate is specified on the voucher, it will be used thanks to the special keys in the context
                        # otherwise we use the rates of the system
                        amount_currency = currency_obj.compute(cr, uid, company_currency, line.move_line_id.currency_id.id, move_line['debit']-move_line['credit'], context=ctx)
                if line.amount == line.amount_unreconciled:
                    sign = voucher.type in ('payment', 'purchase') and -1 or 1
                    foreign_currency_diff = sign * line.move_line_id.amount_residual_currency + amount_currency

            move_line['amount_currency'] = amount_currency
            voucher_line = move_line_obj.create(cr, uid, move_line)
            rec_ids = [voucher_line, line.move_line_id.id]
            if not currency_obj.is_zero(cr, uid, voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0],context)
                move_line_obj.create(cr, uid, exch_lines[1], context)
                rec_ids.append(new_id)

            if line.move_line_id and line.move_line_id.currency_id and not currency_obj.is_zero(cr, uid, line.move_line_id.currency_id, foreign_currency_diff):
                # Change difference entry in voucher currency
                move_line_foreign_currency = {
                    'journal_id': line.voucher_id.journal_id.id,
                    'period_id': line.voucher_id.period_id.id,
                    'name': _('change')+': '+(line.name or '/'),
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'partner_id': line.voucher_id.partner_id.id,
                    'currency_id': line.move_line_id.currency_id.id,
                    'amount_currency': -1 * foreign_currency_diff,
                    'quantity': 1,
                    'credit': 0.0,
                    'debit': 0.0,
                    'date': line.voucher_id.date,
                }
                new_id = move_line_obj.create(cr, uid, move_line_foreign_currency, context=context)
                rec_ids.append(new_id)
            if line.move_line_id.id:
                rec_lst_ids.append(rec_ids)
                
        #for TDS Amount
        if voucher.tds_amount and voucher.tds_amount>0:
            tds_amount = voucher.tds_amount
            #create one move line per voucher line where amount is not 0.0
            # AND (second part of the clause) only if the original move line was not having debit = credit = 0 (which is a legal value)
            #if not tds_amount and not (line.move_line_id and not float_compare(line.move_line_id.debit, line.move_line_id.credit, precision_digits=prec) and not float_compare(line.move_line_id.debit, 0.0, precision_digits=prec)):
            #    continue
            # convert the amount set on the voucher line into the currency of the voucher's company
            # this calls res_curreny.compute() with the right context, so that it will take either the rate on the voucher if it is relevant or will use the default behaviour
            amount = self._convert_amount(cr, uid, line.untax_amount or tds_amount, voucher.id, context=ctx)
            
            
            currency_rate_difference = 0.0
            
            credit = voucher.type in ('payment', 'purchase') and tds_amount or 0.0
            if voucher.type in ('payment', 'purchase'):
                debit=0.0
                credit = tds_amount
                line.type = 'cr'
            else:
                debit=tds_amount
                credit = 0.0
                line.type = 'dr'
            move_line = {
                'journal_id': voucher.journal_id.id,
                'period_id': voucher.period_id.id,
                'name': 'TDS',
                'account_id': voucher.tds_account_id.id,
                'move_id': move_id,
                'partner_id': voucher.partner_id.id,
                'currency_id': False,
                'analytic_account_id': False,
                'quantity': 1,
                'credit': credit,
                'debit': debit,
                'date': voucher.date
            }
            if amount < 0:
                amount = -amount
                if line.type == 'dr':
                    line.type = 'cr'
                else:
                    line.type = 'dr'

            if (line.type=='dr'):
                tot_line += amount
                move_line['debit'] = amount
            else:
                tot_line -= amount
                move_line['credit'] = amount

            if voucher.tax_id and voucher.type in ('sale', 'purchase'):
                move_line.update({
                    'account_tax_id': voucher.tax_id.id,
                })

            if move_line.get('account_tax_id', False):
                tax_data = tax_obj.browse(cr, uid, [move_line['account_tax_id']], context=context)[0]
                if not (tax_data.base_code_id and tax_data.tax_code_id):
                    raise osv.except_osv(_('No Account Base Code and Account Tax Code!'),_("You have to configure account base code and account tax code on the '%s' tax!") % (tax_data.name))

            # compute the amount in foreign currency
            #foreign_currency_diff = 0.0
            amount_currency = False
            
            move_line['amount_currency'] = amount_currency
            voucher_line = move_line_obj.create(cr, uid, move_line)

            if not currency_obj.is_zero(cr, uid, voucher.company_id.currency_id, currency_rate_difference):
                # Change difference entry in company currency
                exch_lines = self._get_exchange_lines(cr, uid, line, move_id, currency_rate_difference, company_currency, current_currency, context=context)
                new_id = move_line_obj.create(cr, uid, exch_lines[0],context)
                move_line_obj.create(cr, uid, exch_lines[1], context)

        return (tot_line, rec_lst_ids)


class account_move(osv.osv):
    _inherit = 'account.move'
    
    
    def onchange_date(self, cr, uid, ids, date, period_id, context=None):
        res = {}
        if date and period_id:
            period_obj = self.pool.get('account.period').browse(cr, uid, period_id, context=context)
            if date < period_obj.date_start or  date > period_obj.date_stop:
                warning = {
                   'title': _('Error!'),
                   'message' : 'Date must be in between the selected period dates'
                    }
                return {'value': {'date': False}, 'warning': warning}
        return res
    

account_move()


class account_move_line(osv.osv):
    _inherit = 'account.move.line'

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        result = []
        for line in self.browse(cr, uid, ids, context=context):
            if line.ref:
                result.append((line.id, (line.invoice.legale_number or line.move_id.name) + ' ('+line.ref+')'))
            else:
                result.append((line.id, (line.invoice.legale_number or line.move_id.name)))
        return result
    
    
    _columns = {
        'bank_date': fields.date('Bank Date'),
        'bank_reco': fields.boolean('Reconciled'),
        }
    
account_move_line()


class account_account(osv.osv):
    
    _inherit = 'account.account'
    
    def onchange_parent(self, cr, uid, ids, parent_id, context=None):
        context = context or {}
        val = {'code':False}
        if parent_id:
            code = False
            parent = self.browse(cr, uid, parent_id)
            codeids = self.search(cr, uid, [('parent_id','=',parent.id),('type','!=','view')],order='id desc',limit=1)
            if len(codeids)>0:
                code_obj = self.browse(cr, uid, codeids[0])
                code = int(code_obj.code) + 1
            else:
                code = str(parent.code) + '001'
            val['code']=code
            
        return {'value':val}
    
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', '=ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        accounts = self.search(cr, uid, domain + args, limit=limit, context=context)
        return self.name_get(cr, uid, accounts, context)
     

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('ledger_account_ids', False):
            ledger_account_ids = [account_obj.id for account_obj in self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID, context=context).company_id.ledger_account_ids]
            args += [['id', 'in', ledger_account_ids]]
        if context.get('bank_account_ids', False):
            bank_account_ids = [account_obj.id for account_obj in self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID, context=context).company_id.bank_account_ids]
            args += [['id', 'in', bank_account_ids]]
        return super(account_account, self).search(cr, uid, args, offset, limit, order, context, count)
           
account_account()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: