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

from datetime import datetime
import time

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class cases_bills_info(osv.osv_memory):

    _name = "cases.bills.info"
    _description = "Cases and Bills Information"
    total_bill_amt =0.00
    total_bal_amt = 0.00
    ho_branch_id = False
    work_type = False
    client_id = False
    parent_id = False

    _columns = {
        'name':fields.many2one('res.partner','Client Name'),
        'ho_branch_id':fields.many2one('ho.branch','Location'),
        'case_id': fields.many2one('case.sheet', 'File Number'),
        'work_type':fields.selection([('civillitigation', 'Civil Litigation'),('criminallitigation', 'Criminal Litigation'), ('non_litigation', 'Non Litigation'), ('arbitration', 'Arbitration'),('execution', 'Execution'),('mediation', 'Mediation')], 'Type of Work'),
        'from_date':fields.date('From date'),
        'to_date':fields.date('To Date'),
        'date_filter':fields.selection([('=','is equal to'),('!=','is not equal to'),('>','greater than'),('<','less than'),('>=','greater than or equal to'),('<=','less than or equal to'),('between','between')],'Bill Date'),
        'state':fields.selection([('open','Pending'),('paid','Closed')],'Bill Status'),
        'invoice_id':fields.many2one('account.invoice','Bill Number'),
        'assignee_id': fields.many2one('hr.employee','Assignee'),
        'other_assignee_id':fields.many2one('res.partner','Other Associate'),
        'division_id':fields.many2one('hr.department', 'Department/Division'),
        'casetype_id': fields.many2one('case.master','Case Type'),
        'contact_partner1_id': fields.many2one('res.partner','Contact Person 1'),
    	'contact_partner2_id': fields.many2one('res.partner','Contact Person 2'),
    	'company_ref_no':fields.char('Client Ref #',size=40),
    	'reg_number':fields.char('Case No.'),
    	'court_district_id': fields.many2one('district.district','Court District'),
    	'court_location_id': fields.many2one('court.location','Court Location'),
    	'court_id': fields.many2one('court.master','Court Name'),
    	'parent_id_manager':fields.many2one('hr.employee', "Manager"),
    	'bill_type':fields.selection([('fixed_price','Fixed Price'),('assignment_wise','Assignment Wise')],'Billing Type'),
    	'first_party_name':fields.char('First Party name'),
    	'oppo_party_name':fields.char('Opposite Party name'),
    	'case_state':fields.selection([('new','New'), ('inprogress','In Progress'), ('cancel','Cancelled'), ('transfer','Transferred'), ('done','Closed'), ('hold','Hold')],'Case State'),
        'case_bills_ids':fields.one2many('case.bills.details','case_bill_id','Rel'),
    }
    _defaults = {
        'from_date':lambda *a: time.strftime('%Y-%m-%d'),
        'to_date':lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def default_get(self, cr, uid, fields_list, context=None):
        if not context:
            context = {}
        self.parent_id = False    
        res = super(cases_bills_info, self).default_get(cr, uid, fields_list, context=context)
        return res
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return ['Cases and Bills Info']
        for task_line in self.browse(cr, uid, ids, context=context):
            res.append((task_line.id,'Cases and Bills Info'))
        return res
            
    def clear_filters_all(self, cr, uid, ids, context=None):
        res={}
        self.parent_id = False
        res['name'] = False
        res['ho_branch_id'] = False
        res['work_type'] = False
        res['from_date'] = time.strftime('%Y-%m-%d')
        res['to_date'] = time.strftime('%Y-%m-%d')
        res['date_filter'] = False
        res['next_from_date'] = time.strftime('%Y-%m-%d')
        res['next_to_date'] = time.strftime('%Y-%m-%d')
        res['state'] = False
        res['case_state'] = False
        res['invoice_id'] = False
        res['case_id'] = False
        res['assignee_id'] = False
        res['other_assignee_id'] = False
        res['division_id'] = False
        res['casetype_id'] = False
        res['contact_partner1_id'] = False
        res['contact_partner2_id'] = False
        res['company_ref_no'] = False
        res['reg_number'] = False
        res['court_district_id'] = False
        res['court_location_id'] = False
        res['court_id'] = False
        res['parent_id_manager'] = False
        res['bill_type'] = False
        res['first_party_name'] = False
        res['oppo_party_name'] = False
        cr.execute('delete from court_diary_line_ids')
        delids = self.pool.get('case.bills.details').search(cr, uid, [('case_bill_id','=',ids[0])])
        if len(delids):
            self.pool.get('case.bills.details').unlink(cr, uid, delids)
        return self.write(cr, uid, ids, res)

    def generate_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        data['client_id'] = context['client_id']
        data['date_filter'] = context['date_filter']
        data['from_date'] = context['from_date']
        data['to_date'] = context['to_date']
        data['ho_branch_id'] = context['ho_branch_id']
        data['work_type'] = context['work_type']
        datas = {
             'ids': [],
             'model': 'case.sheet',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'cases.bills.info',
            'datas': datas,
            'nodestroy': True,
            'name':'Case and Bills Info'
            }
            
    def onchange_location(self, cr, uid, ids, location, context=None):        
        self.ho_branch_id = location
        return True
            
    def onchange_client(self, cr, uid, ids, client, context=None):
        self.client_id = client
        return True   
            
    def onchange_work_type(self, cr, uid, ids, work_type, context=None):
        self.work_type = work_type
        return True     	
            
 
    def filter_string(self,cr, uid,context):
        filters = []
        
        if context.has_key('client_id') and context['client_id']!=False:
            filters.append(('client_id','=',context['client_id']))
        if context.has_key('ho_branch_id') and context['ho_branch_id']!=False:
            filters.append(('ho_branch_id','=',context['ho_branch_id']))
        if context.has_key('work_type') and context['work_type']!=False:
            filters.append(('work_type','=',context['work_type']))
        if context.has_key('case_id') and context['case_id']!=False:
            filters.append(('id','=',context['case_id']))
        if context.has_key('assignee_id') and context['assignee_id']!=False:
            filters.append(('assignee_id','=',context['assignee_id']))
        if context.has_key('other_assignee_id') and context['other_assignee_id']!=False:
            filters.append(('other_assignee_ids.name','=',context['other_assignee_id']))
        if context.has_key('division_id') and context['division_id']!=False:
            filters.append(('division_id','=',context['division_id']))
        if context.has_key('casetype_id') and context['casetype_id']!=False:
            filters.append(('casetype_id','=',context['casetype_id']))
        if context.has_key('contact_partner1_id') and context['contact_partner1_id']!=False:
            filters.append(('contact_partner1_id','=',context['contact_partner1_id']))
        if context.has_key('contact_partner2_id') and context['contact_partner2_id']!=False:
            filters.append(('contact_partner2_id','=',context['contact_partner2_id']))
        if context.has_key('company_ref_no') and context['company_ref_no']!=False:
            filters.append(('company_ref_no','ilike',context['company_ref_no']))
        if context.has_key('reg_number') and context['reg_number']!=False:
            filters.append(('reg_number','ilike',context['reg_number']))
        if context.has_key('court_district_id') and context['court_district_id']!=False:
            filters.append(('court_district_id','=',context['court_district_id']))
        if context.has_key('court_location_id') and context['court_location_id']!=False:
            filters.append(('court_location_id','=',context['court_location_id']))
        if context.has_key('court_id') and context['court_id']!=False:
            filters.append(('court_id','=',context['court_id']))
        if context.has_key('parent_id_manager') and context['parent_id_manager']!=False:
            filters.append(('assignee_id.parent_id','=',context['parent_id_manager']))
        if context.has_key('bill_type') and context['bill_type']!=False:
            filters.append(('bill_type','=',context['bill_type']))
        if context.has_key('first_party_name') and context['first_party_name']!=False:
            filters.append(('first_parties.name','ilike',context['first_party_name']))
        if context.has_key('oppo_party_name') and context['oppo_party_name']!=False:
            filters.append(('opp_parties.name','ilike',context['oppo_party_name']))  
        if context.has_key('case_state') and context['case_state']!=False:
            filters.append(('state','=',context['case_state']))  

        return filters    
        
    def invoice_filter_string(self,cr, uid, context):
        filters = [('invoice_id','!=',False)]
        if context.has_key('date_filter') and context['date_filter']!=False:
            if context['date_filter']!='between':
                filters.append(('invoice_id.date_invoice',context['date_filter'],context['from_date'])) 
            else:
                filters.append(('invoice_id.date_invoice','>',context['from_date']))     
                filters.append(('invoice_id.date_invoice','<',context['to_date']))
        if context.has_key('state') and context['state']!=False:
            filters.append(('invoice_id.state','=',context['state']))
        if context.has_key('invoice_id') and context['invoice_id']!=False:
            inv = self.pool.get('account.invoice').browse(cr, uid, context['invoice_id'])
            if inv :
                filters.append(('invoice_id.legale_number','ilike',inv.legale_number)) 
                
        return filters        
        
       
    def get_data(self,cr, uid, ids, context=None):
        try:
            delids = self.pool.get('case.bills.details').search(cr, uid, [('case_bill_id','=',ids[0])])
            if len(delids):
                self.pool.get('case.bills.details').unlink(cr, uid, delids)
            filters = self.filter_string(cr, uid,context)
            inv_filters = self.invoice_filter_string(cr, uid,context)
            self.cr = cr
            self.uid = uid
            search_ids = self.pool.get('case.sheet').search(self.cr, self.uid, filters, order='name')
            ret_datas = []
            ret_data = {}
            for case in self.pool.get('case.sheet').browse(self.cr, self.uid, search_ids):
                first_parties = ''
                opp_parties = ''
                court = ''
                flg_inv = False
                ret_data = {}
                state_list = {'new':'New','inprogress':'In Progress','cancel':'Cancelled','transfer':'Transferred', 'won':'Won', 'arbitrated':'Arbitrated', 'withdrawn':'With Drawn', 'lost':'Lost', 'inactive':'Inactive', 'done':'Closed', 'hold':'Hold'}
                work_types = {'civillitigation':'Civil Litigation','criminallitigation':'Criminal Litigation', 'non_litigation':'Non Litigation', 'arbitration':'Arbitration', 'execution':'Execution', 'mediation':'Mediation'}
                for first in case.first_parties:
                    first_parties += (first_parties!='' and ', ' + first.name or first.name)
                for opp in case.opp_parties:
                    opp_parties += (opp_parties!='' and ', ' + opp.name or opp.name)
                if case.work_type in ('civillitigation','criminallitigation', 'execution'):
                    court = (case.court_id and case.court_id.name or '') + (case.court_location_id and ', ' + case.court_location_id.name or '') + (case.court_district_id and ', ' + case.court_district_id.name or '')
                else:
                    court = work_types[case.work_type] + ', ' + case.casetype_id.name
                ret_data['file_no'] = case.name
                ret_data['client_name'] = case.client_id.name
                ret_data['first_party'] = first_parties
                ret_data['opp_party'] = opp_parties
                ret_data['assignee'] = case.assignee_id.name
                ret_data['case_no'] = case.reg_number
                ret_data['total_case_amount'] = case.bill_type == 'fixed_price' and case.fixed_price or case.total_projected_amount
                ret_data['court_name'] = court
                ret_data['status'] = state_list[case.state]
                ret_data['legale_number'] = False
                ret_data['date_invoice'] = False
                ret_data['amount_total'] = False
                ret_data['amount_paid'] = False
                ret_data['amount_tds'] = False
                ret_data['amount_balance'] = False
                ret_data['inv_state'] = False
                ret_data['case_bill_id'] = ids[0]
                self.parent_id = ids[0]
                case_inv_search_ids = self.pool.get('case.sheet.invoice').search(self.cr, self.uid, [('case_id','=',case.id)] + inv_filters,order='invoice_id desc')
                for caseinv in self.pool.get('case.sheet.invoice').browse(self.cr, self.uid, case_inv_search_ids):
                    flg_inv = True
                    bill_no = ''
                    total_paid_amt = 0.00
                    total_tds_amt = 0.00
                    distributed_tds_amt = 0.00
                    act_tds = 0.00
                    act_amt = 0.00
                    
                    if caseinv.invoice_id.legale_number:
                        bill_no = caseinv.invoice_id.legale_number
                    else:
                        bill_no = caseinv.invoice_id.number
                    for line in caseinv.invoice_id.payment_ids:
                        vouchers = self.pool.get('account.voucher').search(self.cr, self.uid, [('move_id','=',line.move_id.id),('type','=','receipt')])
                        for voucher in self.pool.get('account.voucher').browse(self.cr, self.uid, vouchers):
                            total_paid_amt += voucher.amount
                            total_tds_amt += voucher.tds_amount
                            prcnt = (voucher.tds_amount/(voucher.tds_amount + voucher.amount))*100
                            for lline in voucher.line_cr_ids:
                                if lline.amount>0.00 and lline.move_line_id.move_id == caseinv.invoice_id.move_id:
                                    distributed_tds_amt = (prcnt*lline.amount)/100
                                    act_tds += distributed_tds_amt
                                    act_amt += lline.amount - distributed_tds_amt
                    ret_data['legale_number'] = bill_no
                    ret_data['date_invoice'] = (caseinv.invoice_id.date_invoice and datetime.strptime(caseinv.invoice_id.date_invoice, '%Y-%m-%d').strftime('%d-%b-%y') or '')
                    ret_data['amount_total'] = caseinv.invoice_id.amount_total
                    ret_data['amount_paid'] = act_amt
                    ret_data['amount_tds'] = act_tds
                    ret_data['amount_balance'] = caseinv.invoice_id.residual
                    ret_data['inv_state'] = (caseinv.invoice_id.state=='open' and 'PENDING' or (caseinv.invoice_id.state=='paid' and 'CLOSED' or ''))
                    self.total_bill_amt += caseinv.invoice_id.amount_total
                    self.total_bal_amt += caseinv.invoice_id.residual
                    ret_datas.append(ret_data)
                    self.pool.get('case.bills.details').create(cr, uid, ret_data)
                if not flg_inv:
                    ret_datas.append(ret_data)
                    self.pool.get('case.bills.details').create(cr, uid, ret_data)
            return ret_datas    
        except NameError:
                raise orm.except_orm(_(''),
                     _('No Data To Generate Report'))  
                     
    def get_ids(self, cr, uid):
        ret = []
        if self.parent_id:
            for line in self.browse(cr, uid, self.parent_id).case_bills_ids:
                ret.append(str(line.id))
        return {"ids":ret}

cases_bills_info()


class cases_bills_details(osv.osv_memory):
    _name = "case.bills.details"
    _order = "file_no"
    _columns = {
        'case_bill_id':fields.many2one('cases.bills.info','Rel'),
        'file_no': fields.char('File No'),
        'client_name': fields.char('Client'),
        'first_party' : fields.char('First party'),
        'opp_party' : fields.char('Opposite party'),
        'assignee' : fields.char('Assignee'),
        'case_no' : fields.char('Reg No'),
        'total_case_amount' : fields.float('Total Case Amount', digits_compute=dp.get_precision('Account')),
        'court_name' : fields.char('Court Name'),
        'status' : fields.char('Case Status'),
        'legale_number' : fields.char('Bill Number'),
        'date_invoice' : fields.char('Bill Date'),
        'amount_total' : fields.float('Bill Amount', digits_compute=dp.get_precision('Account')),
        'amount_paid' : fields.float('Paid Amount', digits_compute=dp.get_precision('Account')),
        'amount_tds' : fields.float('TDS Amount', digits_compute=dp.get_precision('Account')),
        'amount_balance' : fields.float('Balance Amount', digits_compute=dp.get_precision('Account')),
        'inv_state' : fields.char('Invoice State', digits_compute=dp.get_precision('Account')),
    }
    
cases_bills_details()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: