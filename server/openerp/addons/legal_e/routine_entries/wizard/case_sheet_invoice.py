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
from openerp import netsvc
import openerp.exceptions


class case_sheet_invoice(osv.osv):

    _name = "case.sheet.invoice"
    _description = "To Create an Invoice for Case Sheet"

    def _get_total_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for inv in self.browse(cr, uid, ids, context=context):
            amount = 0.00
            for line in inv.invoice_lines_fixed:            
                amount = amount + line.amount + line.out_of_pocket_amount
            for line in inv.invoice_lines_assignment_hourly:            
                if line.amount:
                    amount = amount + line.amount
            for line in inv.invoice_lines_assignment_fixed:            
                if line.amount:
                    amount = amount + line.amount + line.out_of_pocket_amount
            for line in inv.invoice_lines_other_expenses:            
                if line.amount:
                    amount = amount + line.amount
            for line in inv.invoice_lines_court_proceedings_fixed:            
                if line.amount:
                    amount = amount + line.amount
            for line in inv.invoice_lines_court_proceedings_assignment:            
                if line.amount:
                    amount = amount + line.amount
            res[inv.id] = amount
        return res

    _columns = {
        'name':fields.char('Case Invoice Number',size=100),
        'case_id': fields.many2one('case.sheet','File Number'),
        'bill_type':fields.selection([('fixed_price','Fixed Price'),('assignment_wise','Assignment Wise')],'Billing Type', required=False),
        'amount_total_1':fields.function(_get_total_amount,string='Total Amount',type='float'),
        'invoice_lines_fixed':fields.one2many('case.sheet.invoice.line','inv_id_fixed','Fixed Price Stages Details'),
        'invoice_lines_assignment_hourly':fields.one2many('case.sheet.invoice.line','inv_id_assignment_hourly','Hourly Stages Details'),
        'invoice_lines_assignment_fixed':fields.one2many('case.sheet.invoice.line','inv_id_assignment_fixed','Fixed Price Stages Details'),
        'invoice_lines_other_expenses':fields.one2many('case.sheet.invoice.line','inv_id_other_expense','Other Expenses Details'),
        'invoice_lines_out_of_pocket':fields.one2many('case.sheet.invoice.line','inv_id_out_of_pocket','Out of Pocket Expenses Details'),
        'invoice_lines_court_proceedings_fixed':fields.one2many('case.sheet.invoice.line','inv_id_court_proceed_fixed','Fixed Price Court Proceedings Details'),
        'invoice_lines_court_proceedings_assignment':fields.one2many('case.sheet.invoice.line','inv_id_court_proceed_assignment','Assignment Wise Court Proceedings Details'),
        'invoice_lines':fields.one2many('case.sheet.invoice.line','inv_id_bill','Invoice Details'),
        'invoice_id':fields.many2one('account.invoice','Invoice'),
        'subject':fields.text('Subject'),
        'consolidated_id':fields.many2one('consolidated.bill','Consolidated Bill Number'),
        'receivable_account_id':fields.many2one('account.account', 'Receivable Account', domain=[('type','=','receivable')], help="The partner account used for these invoices."),
        'sale_account_id':fields.many2one('account.account', 'Sales Account', domain=[('type','<>','view'), ('type', '<>', 'closed')], help="The income or expense account related to the selected product."),
        'invoice_date':fields.date('Invoiced Date'),
        
        'expense_account_id': fields.many2one('account.account', 'Expense Account', domain=[('type','<>','view'), ('type', '<>', 'closed')], states={'confirm':[('required',True)]}),
    
    }
    
    def get_total_amount(self, cr, uid, ids,context=None):
        res = 0.00
        for obj in self.browse(cr, uid, ids, context=context):
            amount = 0.00
            for line in obj.invoice_lines_fixed:            
                ob = self.pool.get('fixed.price.stages').browse(cr, uid, line.ref_id)
                amount += ob.amount + ob.out_of_pocket_amount
            for line in obj.invoice_lines_assignment_hourly:
                ob = self.pool.get('assignment.wise').browse(cr, uid, line.ref_id)
                amount += line.amount
            for line in obj.invoice_lines_assignment_fixed:            
                ob = self.pool.get('assignment.wise').browse(cr, uid, line.ref_id)
                amount += ob.amount + ob.out_of_pocket_amount
            for line in obj.invoice_lines_other_expenses:    
                if self.pool.get('other.expenses').search(cr, uid, [('id','=',line.ref_id)]):             
                    ob= self.pool.get('other.expenses').browse(cr, uid, line.ref_id)
                    amount += ob.amount
            for line in obj.invoice_lines_court_proceedings_fixed:
                amount += line.amount
            for line in obj.invoice_lines_court_proceedings_assignment:
                amount += line.amount
            return amount    
        return res
    

        
    def dummy(self, cr, uid, ids, context=None):
        return True
    
    def invoice_case_sheet(self, cr, uid, ids, context=None):
        context = context or {}
        line_total = 0.00
        obj = self.browse(cr, uid, ids[0])

        for line in obj.invoice_lines:            
            line_total= line_total + line.amount
        if round(line_total,2) != round(obj.amount_total_1,2):
            raise openerp.exceptions.Warning(_('Total Amount in Billing Particulars is NOT EQUAL to Total Amount!'))
        up_invoice_lines = []
        for line in obj.invoice_lines_fixed: 
            invoice_line = {
                             'name':line.name,
                             'price_unit':line.amount + line.out_of_pocket_amount,
                             'quantity':1.0,
                             'account_id':obj.sale_account_id.id,
                             'account_analytic_id':obj.case_id.project_id.analytic_account_id.id,
                             'office_id': line.office_id.id 
                             }
            up_invoice_lines.append((0,0,invoice_line))
            
        for line in obj.invoice_lines_assignment_fixed: 
            invoice_line = {
                             'name':line.name,
                             'price_unit':line.amount + line.out_of_pocket_amount,
                             'quantity':1.0,
                             'account_id':obj.sale_account_id.id,
                             'account_analytic_id':obj.case_id.project_id.analytic_account_id.id,
                             'office_id': line.office_id.id 
                             }
            up_invoice_lines.append((0,0,invoice_line))
            
            
        for line in obj.invoice_lines_assignment_hourly: 
            invoice_line = {
                             'name':line.name,
                             'price_unit':line.amount + line.out_of_pocket_amount,
                             'quantity':1.0,
                             'account_id':obj.sale_account_id.id,
                             'account_analytic_id':obj.case_id.project_id.analytic_account_id.id,
                             'office_id': line.office_id.id 
                             }
            up_invoice_lines.append((0,0,invoice_line))
            
        for line in obj.invoice_lines_court_proceedings_assignment: 
            invoice_line = {
                             'name':line.name,
                             'price_unit':line.amount + line.out_of_pocket_amount,
                             'quantity':1.0,
                             'account_id':obj.sale_account_id.id,
                             'account_analytic_id':obj.case_id.project_id.analytic_account_id.id,
                             'office_id': line.office_id.id 
                             }
            up_invoice_lines.append((0,0,invoice_line))
            
            
        for line in obj.invoice_lines_other_expenses: 
            invoice_line = {
                             'name':line.name,
                             'price_unit':line.amount,
                             'quantity':1.0,
                             'account_id':obj.expense_account_id.id,
                             'account_analytic_id':obj.case_id.project_id.analytic_account_id.id,
                             'office_id': line.office_id.id 
                             }
            up_invoice_lines.append((0,0,invoice_line))
        
        particular_invoice_lines = []
        for line in obj.invoice_lines: 
            particular_invoice_line = {
                             'name':line.name,
                             'price_unit':line.amount,
                             }
            particular_invoice_lines.append((0,0,particular_invoice_line))
        
        context.update({'type':'out_invoice'})
        journal_id = self.pool.get('account.invoice')._get_journal(cr, uid, context=context)
        invoice = {
                   'partner_id':obj.case_id.client_id.id,
                   'type':'out_invoice',
                   'legale_number':(obj.consolidated_id and obj.consolidated_id.name or obj.case_id.name),
                   'subject_line':obj.subject,
                   'name':obj.case_id.name,
                   'journal_id':journal_id,
                   'invoice_line':up_invoice_lines,
                   'particular_invoice_line_ids': particular_invoice_lines,
                   'account_id':obj.receivable_account_id.id,
                   'case_id':obj.case_id.id,
                   'consolidated_id':(obj.consolidated_id and obj.consolidated_id.id or False),
                   'date_invoice':obj.invoice_date,
                   }
        invoice_id = self.pool.get('account.invoice').create(cr, uid, invoice)
        #Update the Lines as Invoiced
        if invoice_id:
            self.write(cr, uid, ids, {'invoice_id':invoice_id}, context=context)
            for line in obj.invoice_lines_fixed:            
                self.pool.get('fixed.price.stages').write(cr, uid, [line.ref_id],{'invoiced':True})
            for line in obj.invoice_lines_assignment_hourly:
                assign = self.pool.get('assignment.wise').browse(cr, uid, line.ref_id)
                self.pool.get('assignment.wise').write(cr, uid, [line.ref_id],{'invoiced':True, 'billed_hours':(assign.billed_hours + assign.remaining_hours), 'remaining_hours':0.00})
            for line in obj.invoice_lines_assignment_fixed:            
                self.pool.get('assignment.wise').write(cr, uid, [line.ref_id],{'invoiced':True})
            for line in obj.invoice_lines_other_expenses:            
                self.pool.get('other.expenses').write(cr, uid, [line.ref_id],{'invoiced':True})
            for line in obj.invoice_lines_court_proceedings_fixed:
                self.pool.get('court.proceedings').write(cr, uid, [line.ref_id],{'invoiced':True})
            for line in obj.invoice_lines_court_proceedings_assignment:
                self.pool.get('court.proceedings').write(cr, uid, [line.ref_id],{'invoiced':True})
            wf_service = netsvc.LocalService("workflow")
            if obj.consolidated_id:
                wf_service.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
            
            return True    
        return False
        
    def cancel_invoice_case_sheet(self, cr, uid, ids, context=None):
        context = context or {}

        for obj in self.browse(cr, uid, ids):
                
                for line in obj.invoice_lines_fixed:
                    self.pool.get('fixed.price.stages').write(cr, uid, [line.ref_id],{'invoiced':False})
                for line in obj.invoice_lines_assignment_hourly:
                    assign = self.pool.get('assignment.wise').browse(cr, uid, line.ref_id)
                    remain = line.bill_hours
                    if not remain or remain<=0:
                        remain = line.amount/assign.amount
                    remain = remain or 0.00
                    self.pool.get('assignment.wise').write(cr, uid, [line.ref_id],{'invoiced':False, 'billed_hours':(assign.billed_hours - remain), 'remaining_hours':assign.remaining_hours + remain})
                for line in obj.invoice_lines_assignment_fixed:            
                    self.pool.get('assignment.wise').write(cr, uid, [line.ref_id],{'invoiced':False})
                
                for line in obj.invoice_lines_other_expenses:  
                    if line.ref_id:
                        expenses_ids = self.pool.get('other.expenses').search(cr, uid, [('id', '=', line.ref_id)], context=context)
                        if expenses_ids:
                            self.pool.get('other.expenses').write(cr, uid, [line.ref_id],{'invoiced':False})
                for line in obj.invoice_lines_court_proceedings_fixed:
                    self.pool.get('court.proceedings').write(cr, uid, [line.ref_id],{'invoiced':False})
                for line in obj.invoice_lines_court_proceedings_assignment:
                    self.pool.get('court.proceedings').write(cr, uid, [line.ref_id],{'invoiced':False})             
                return True    
        return False
        
    def draft_invoice_case_sheet(self, cr, uid, ids, context=None):
        context = context or {}
        for obj in self.browse(cr, uid, ids):
            for line in obj.invoice_lines_fixed:          
                self.pool.get('fixed.price.stages').write(cr, uid, [line.ref_id],{'invoiced':True})
            for line in obj.invoice_lines_assignment_hourly:
                assign = self.pool.get('assignment.wise').browse(cr, uid, line.ref_id)
                remain = line.bill_hours
                if not remain or remain<=0:
                    remain = line.amount/assign.amount
                remain = remain or 0.00
                self.pool.get('assignment.wise').write(cr, uid, [line.ref_id],{'invoiced':True, 'billed_hours':(assign.billed_hours + assign.remaining_hours), 'remaining_hours':0.00})
            for line in obj.invoice_lines_assignment_fixed:            
                self.pool.get('assignment.wise').write(cr, uid, [line.ref_id],{'invoiced':True})
            for line in obj.invoice_lines_other_expenses:     
                if self.pool.get('other.expenses').search(cr, uid, [('id','=',line.ref_id)]):     
                    self.pool.get('other.expenses').write(cr, uid, [line.ref_id],{'invoiced':True})
            for line in obj.invoice_lines_court_proceedings_fixed:
                self.pool.get('court.proceedings').write(cr, uid, [line.ref_id],{'invoiced':True})
            for line in obj.invoice_lines_court_proceedings_assignment:
                self.pool.get('court.proceedings').write(cr, uid, [line.ref_id],{'invoiced':True})
            return True    
        return False        
    
    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
                for line in obj.invoice_lines_assignment_hourly:
                    assign = self.pool.get('assignment.wise').browse(cr, uid, line.ref_id)
                    remain = line.bill_hours
                    if not remain or remain<=0:
                        remain = line.amount/assign.amount
                    remain = remain or 0.00
                    self.pool.get('assignment.wise').write(cr, uid, [line.ref_id],{'invoiced':False, 'billed_hours':(assign.billed_hours - remain), 'remaining_hours':assign.remaining_hours + remain})
        retvals = super(case_sheet_invoice, self).unlink(cr, uid, ids, context=context)
        return retvals


case_sheet_invoice()

class case_sheet_invoice_line(osv.osv):

    _name = "case.sheet.invoice.line"
    _description = "To Create an Invoice for Case Sheet"

    _columns = {
        'inv_id_bill':fields.many2one('case.sheet.invoice','Case Invoice ID'),
        'inv_id_court_proceed_assignment':fields.many2one('case.sheet.invoice','Case Invoice ID'),
        'inv_id_court_proceed_fixed':fields.many2one('case.sheet.invoice','Case Invoice ID'),
        'inv_id_out_of_pocket':fields.many2one('case.sheet.invoice','Case Invoice ID'),
        'inv_id_other_expense':fields.many2one('case.sheet.invoice','Case Invoice ID'),
        'inv_id_assignment_fixed':fields.many2one('case.sheet.invoice','Case Invoice ID'),
        'inv_id_assignment_hourly':fields.many2one('case.sheet.invoice','Case Invoice ID'),
        'inv_id_fixed':fields.many2one('case.sheet.invoice','Case Invoice ID'),
        'name': fields.char('Description'),
        'amount':fields.float('Amount'),
        'out_of_pocket_amount':fields.float('Out of Pocket Expense'),
        'ref_id':fields.integer('Reference ID'),
        'date':fields.date('Date'),
        'effective':fields.selection([('effective','Effective'),('noeffective','Not Effective')],'Effective?'),
        'bill_hours':fields.float('Billing Hours'),
        'office_id':fields.many2one('ho.branch','Office'), #add office field # Sanal Davis # 27/5/15
    }
    _defaults = {        
    }
    
    def onchange_line_amount(self, cr, uid, ids, invid, context=None):
        context = context or {}
        val = {}
        obj = self.browse(cr, uid, invid)
        line_total = 0.00
        for line in obj.invoice_lines:            
            line_total= line_total + line.amount
        if round(line_total,2) != round(obj.amount_total_1,2):
            val['amount'] = 0.00
            raise openerp.exceptions.Warning(_('Total Amount in Billing Particulars is NOT EQUAL to Total Amount!'))
        
        return {'value':val}

case_sheet_invoice_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: