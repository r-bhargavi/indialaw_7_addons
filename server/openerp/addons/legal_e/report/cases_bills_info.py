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
from datetime import datetime
from openerp.report import report_sxw
from openerp.osv import orm


class cases_bills_extra_info(report_sxw.rml_parse):
    _name = 'report.cases.bills.info'
    total_bill_amt = 0.00
    total_bal_amt = 0.00
    def __init__(self, cr, uid, name, context=None):
        super(cases_bills_extra_info, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_data':self.get_data,
            'get_totals':self.get_totals,
        })        

    
    def filter_string(self, context):
        filters = []
        if context.has_key('client_id') and context['client_id']!=False:
            filters.append(('partner_id','=',context['client_id']))
        if context.has_key('ho_branch_id') and context['ho_branch_id']!=False:
            filters.append(('ho_branch_id','=',context['ho_branch_id']))
        if context.has_key('work_type') and context['work_type']!=False:
            filters.append(('work_type','=',context['work_type']))
        if context.has_key('date_filter') and context['date_filter']!=False:
            if context['date_filter']!='between':
                filters.append(('date_invoice',context['date_filter'],context['from_date'])) 
            else:
                filters.append(('date_invoice','>',context['from_date']))     
                filters.append(('date_invoice','<',context['to_date']))
        return filters    
       
    def get_data(self, data):
        try:
            filters = self.filter_string(data['form'])
            search_ids = self.pool.get('case.sheet').search(self.cr, self.uid, filters, order='name')
            ret_datas = []
            ret_data = {}
            for case in self.pool.get('case.sheet').browse(self.cr, self.uid, search_ids):
                first_parties = ''
                opp_parties = ''
                court = ''
                flg_inv = False
                ret_data = {}
                state_list = {'new':'New','inprogress':'In Progress','cancel':'Cancelled','transfer':'Transferred', 'won':'Won', 'arbitrated':'Arbitrated', 'withdrawn':'With Drawn', 'lost':'Lost', 'inactive':'Inactive', 'done':'Closed', 'hold': 'Hold'}
                work_types = {'civillitigation':'Civil Litigation','criminallitigation':'Criminal Litigation', 'non_litigation':'Non Litigation', 'arbitration':'Arbitration', 'execution':'Execution', 'mediation':'Mediation'}
                for first in case.first_parties:
                    first_parties += (first_parties!='' and ', ' + first.name or first.name)
                for opp in case.opp_parties:
                    opp_parties += (opp_parties!='' and ', ' + opp.name or opp.name)
                if case.work_type in ('civillitigation','criminallitigation', 'execution'):
                    court = (case.court_id and case.court_id.name or '') + (case.court_location_id and ', ' + case.court_location_id.name or '') + (case.court_district_id and ', ' + case.court_district_id.name or '')
                else:
                    court = work_types[case.work_type] + ', ' + case.casetype_id.name
                ret_data.update({
                    'file_no': case.name,
                    'client_name': case.client_id.name,
                    'first_party': first_parties,
                    'opp_party': opp_parties,
                    'assignee': case.assignee_id.name,
                    'case_no': case.reg_number,
                    'total_case_amount': case.bill_type == 'fixed_price' and case.fixed_price or case.total_projected_amount,
                    'court_name': court,
                    'status': state_list[case.state],
                    'legale_number': False,
                    'date_invoice': False,
                    'amount_total': False,
                    'amount_paid': False,
                    'amount_tds': False,
                    'amount_balance': False,
                    'inv_state': False,
                    })
                case_inv_search_ids = self.pool.get('case.sheet.invoice').search(self.cr, self.uid, [('invoice_id','!=',False), ('case_id','=',case.id)],order='invoice_id desc')
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
                            prcnt = (voucher.tds_amount/voucher.amount)*100
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
                if not flg_inv:
                    ret_datas.append(ret_data)
            return ret_datas    
        except NameError:
                raise orm.except_orm(_(''),
                     _('No Data To Generate Report'))                     
        
    def get_totals(self,filt):
        if filt == 'bill':
            return self.total_bill_amt
        if filt == 'balance':
            return self.total_bal_amt    
        return ''
            
report_sxw.report_sxw('report.cases.bills.info', 'case.sheet', 'addons/legal_e/report/cases_bills_info_view.rml', parser=cases_bills_extra_info, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: