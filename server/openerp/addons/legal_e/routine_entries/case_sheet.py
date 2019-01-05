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

from datetime import datetime, timedelta
import time

import openerp.exceptions
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)

line_count_slno = 0

_TASK_STATE = [('draft', 'New'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'), ('cancelled', 'Cancelled'), ('hold', 'Hold')]

account_codes = [[4250,205651],[50000,2054228],[10000,2054081],[10000,2054288],[777500,2054059],[17500,2054059],[202013,2054154],[6050100,205597],[180000,2054074],[227500,205599],[37500,2054166],[60000,2054061],[12000,2054089],[50000,2054059],[15000,2054129],[50000,1001],[13467,2054019],[100000,2054065],[250000,2054044],[62500,2054279],[31900,205599],[23180,205602],[100000,2054005],[175000,2054017],[15000,2054272],[6875,205651],[15000,2054069],[495159,2054040],[2040,2054074],[6250,205604],[8000,2054081],[3355340,2054055],[37500,2054159],[120000,2054024],[44250,205597],[50750,205597],[14000,205597],[8750,205597],[50000,2054155],[40000,2054173],[20000,2054191],[22500,2054271],[44500,2054275],[30000,2054139],[50000,2054236],[50000,2054168],[20000,2054174],[20000,2054103],[75400,2054061],[256500,2054323],[50000,2054209],[8000,205526],[20000,2054002],[21000,205651],[20000,2054176],[20000,2054177],[60000,2054051],[15000,2054321],[20000,2054178],[20000,2054197],[20000,2054179],[180000,2054172],[20000,2054180],[3000,2054059],[17000,2054110],[40000,2054093],[20000,2054181],[85000,2054130],[25000,2054003],[5000,2054316],[250000,205553],[50000,1001],[20000,2054182],[80000,2054183],[345000,2054039],[20000,205565],[100000,2054212],[20000,2054117],[500,205572],[215000,2054203],[30000,2054111],[277500,2054234],[20000,2054184],[25000,2054185],[793037,2054019],[35000,2054041],[50000,2054308],[20000,205584],[795860,205586],[20000,2054286],[35000,2054044],[622250,205597],[134000,205599],[60000,205602],[11850,205604],[116000,2054005],[50000,2054277],[20000,2054187],[100000,2054113],[25000,2054188],[20000,2054189],[100000,205611],[20000,2054190],[233000,2054001],[60000,2054200],[50000,2054063],[25000,2054099],[55000,205597],[6250,205604],[33625,205651],[5000,205572],[250000,2054027],[71500,2054039],[12000,2054228],[195000,2054061],[23500,2054139],[150000,2054033],[8000,2054123],[85000,2054101],[30000,2054114],[62000,2054117],[275000,2054019],[52500,205586],[12000,2054286],[655500,205599],[290000,2054001],[56000,2054228],[5000,205651],[30000,205599],[52200,2054228],[62500,2054228],[90000,2054228],[10000,2054089],[6500,2054005],[60000,2054061],[7500,2054123],[89500,205599],[8000,205602],[75000,2054142]]



class court_location(osv.osv):
    _name = 'court.location'
    _columns = {
        'name':fields.char('Location Name',size=1024,required=True),
    }

court_location()

class case_sheet(osv.osv):
    
    _name = 'case.sheet'
    _inherit = ['mail.thread','ir.needaction_mixin']
    _order = 'id desc'
    _description = 'Case Sheet Details'
    _track = {
        'state': {
            'legal_e.mt_casesheet_new': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['new']
        },
    }
    
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('case_sheet', False):
            if self.pool.get('res.users').has_group(cr, uid, 'legal_e.group_legal_e_lawyers') and uid != SUPERUSER_ID:
                args += [('members', 'in', [uid])]
        return super(case_sheet, self).search(cr, uid, args, offset, limit, order, context, count)
    
    
    def update_task_line(self, cr, uid, ids, context=None):
        case_pool = self.pool.get('case.sheet')
        office_pool = self.pool.get('ho.branch')
        fixed_pool = self.pool.get('fixed.price.stages')
        case_tasks_pool = self.pool.get('case.tasks.line')
        task_pool = self.pool.get('task.master')
        case_ids = [13538,13539,13540,13541,13542,13543,13544,13545,13546,13547,13549,13550,13551,13552,13553,13554,13555,13556,13557,13558,13559,13560,13561,13562,13563,13565,13566,13567,13568,13569,13570,13571,13572,13573,13574,13575,13576,13577,13578,13579,13580,13581,13582,13583,13584,13585,13586,13587,13588,13589,13590,13591,13592,13593,13594,13595,13596,13597,13598,13599,13600,13601,13602,13603,13605,13606,13607,13611,13612,13613,13614,13615,13617,13618,13619,13620,13621,13622,13623,13624,13625,13439,13440,13442,13444,13445,13446,13447,13449,13454,13456,13457,13458,13460,13461,13462,13463,13464,13465,13467,13469,13470,13472,13473,13475,13476,13477,13478,13479,13480,13483,13484,13485,13487,13488,13489,13490,13491,13492,13493,13494,13495,13496,13497,13498,13499,13500,13502,13503,13504,13506,13508,13509,13510,13511,13513,13515,13517,13520,13521,13523,13524,13525,13528,13529,13530,13531,13532,13533,13534,13535,13536,13537,13655,13656,13657,13658,13659,13660,13661,13662,13663,13664,13665,13666,13667,13668,13669,13670,13671,13672,13673,13674,13675,13676,13677,13678,13679,13680,13681,13682,13683,13684,13685,13686,13687,13688,13689,13690,13691,13692,13693,13694,13695,13696,13697,13698,13699,13700,13701,13702,13704,13705,13706,13707,13708,13709,13710,13711,13712,13713,13715,13716,13717,13718,13719,13720,13721,13722,13723,13724,13725,13726,13727,13730,13731,13732,13733,13734,13735,13736,13737,13738,13739,13740,13741,13742,13743,13744,13745,13746,13747,13748,13749,13750,13751,13752,13753,13754,13755,13756,13757,13758,13759,13760,13761,13762,13763,13764,13765,13766,13767,13768,13769,13770,13771,13772,13773,13774,13775,13776,13777,13778,13779,13780,13781,13782,13784,13785,13786,13787,13788,13789,13790,13791,13792,13793,13794,13795,13796,13797,13798,13799,13800,13801,13802,13803,13804,13805,13806,13807,13808,13809,13810,13811,13812,13813,13814,13815,13816,13817,13818,13819,13820,13821,13822,13823,13824,13825,13826,13827,13828,13829,13830,13831,13832,13833,13834,13835,13836,13837,13838,13839,13840,13842,13843,13844,13845,13846,13847,13848,13850]
        case_ids = list(set(case_ids))
        case_tasks_ids = case_tasks_pool.search(cr, uid, [('name', '=', 48)], context=context)
        if case_tasks_ids:
            fixed_ids = fixed_pool.search(cr, uid, [('name', 'in', case_tasks_ids),('office_id', '=', 45), ('amount','=', 1825), ('case_id', 'not in', case_ids)], context=context)
            for fixed_line_obj in fixed_pool.browse(cr, uid, fixed_ids, context=context):
                    fixed_pride = fixed_line_obj.case_id.fixed_price
                    tot = 0.0
                    for line_obj in fixed_line_obj.case_id.stage_lines:
                        if line_obj.id not in fixed_ids:
                            tot += line_obj.amount + line_obj.out_of_pocket_amount
    #                 print '--------------->',fixed_pride,tot
                    diff = fixed_pride - tot
                    if diff:
                        fixed_pool.write(cr, uid, [fixed_line_obj.id], {'amount': diff}, context=context)
        
        return True
    
    def account_line_create(self, cr, uid, ids, context=None):
        
        acct_code = {}
        for accts in account_codes:
            if accts[1] in acct_code:
                acct_code[accts[1]] += accts[0]
            else:
                acct_code[accts[1]] = accts[0]
        print acct_code
#         account_codes = []
        for account in acct_code.keys():
            account_ids = self.pool.get('account.account').search(cr, uid, [('code', '=', account)], context=context)
            if account_ids:
#                 print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>',account_ids
                account_obj = self.pool.get('account.account').browse(cr, uid, account_ids[0], context=context)
                field_names = ['credit', 'debit', 'balance']
                context = {'lang': 'en_US', 'tz': 'Asia/Kolkata', 'uid': 1, 'active_model': 'account.chart', 'state': 'all', 'periods':  [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],  'fiscalyear': 2}
                res = self.pool.get('account.account').compute(cr, uid, account_ids, field_names, None, context, '', ())
                if res[account_ids[0]]['balance']-acct_code[account]:
#                     print '<------- '+'['+account_obj.code+']' +account_obj.name + ' ------->',res[account_ids[0]]['debit'],res[account_ids[0]]['credit'],res[account_ids[0]]['balance'], '------', acct_code[account], '-------',res[account_ids[0]]['balance']-acct_code[account]
                    print '<------- '+'['+account_obj.code+']' +account_obj.name + ' ------->',res[account_ids[0]]['balance'], '------', acct_code[account], '-------',res[account_ids[0]]['balance']-acct_code[account]
        
        return True
    
    
    def _get_court_no(self, cr, uid, context=None):
        res = []
        for i in range(50):
            i += 1
            res.append((str(i), str(i)))
        return res
        
    # Starting set bill_state field // Sanal Davis // 5-6-15
    def _get_bill_state(self, cr, uid, ids, field_name, arg, context=None):
        
        res = dict.fromkeys(ids, False)
        for case in self.browse(cr, uid, ids, context=context):
            val = 'not_billed'
            invoiced_state = []
            total_amount = 0.00
            if case.bill_type == 'fixed_price':
                for line in case.stage_lines:
                    if line.invoiced:
                        invoiced_state.append(line.id)
                    total_amount += (line.amount + line.out_of_pocket_amount)
                if case.state in ('new', 'cancel', 'transfer'):
                    val = 'not_billed'
                else:
                    if case.stage_lines and invoiced_state and total_amount and case.fixed_price:
                        if len(case.stage_lines) == len(invoiced_state):
                            if total_amount >= case.fixed_price:
                                val = 'fully_billed'
                            else:
                                val = 'partial_billed'
                        elif invoiced_state and len(case.stage_lines) > len(invoiced_state):
                                val = 'partial_billed'
                        elif not invoiced_state:
                            val = 'not_billed'
            else:
                if case.state == 'done':
                    val = 'fully_billed'
                else:
                    billed = False
                    for line in case.assignment_fixed_lines:
                        if line.invoiced:
                            billed = True
                            
                    for line in case.assignment_hourly_lines:
                        if line.billed_hours:
                            billed = True
                    if billed:
                        val = 'partial_billed'
                    
                    
            res[case.id] = val
            
        return res
    
    
    def _get_unbilled_amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for case_obj in self.browse(cr, uid, ids, context=context):
            unbilled_amount = received_amount = spent_amount = 0.00
            for fixed_obj in case_obj.stage_lines:
                if not fixed_obj.invoiced:
                    unbilled_amount += fixed_obj.amount + fixed_obj.out_of_pocket_amount
                    
            for expense_obj in case_obj.other_expenses_lines:
                if not expense_obj.invoiced and expense_obj.billable == 'bill':
                    unbilled_amount += expense_obj.amount
                    
#             for associate_obj in case_obj.associate_payment_lines:
#                 if not associate_obj.invoiced:
#                     unbilled_amount += associate_obj.amount
                    
            for ass_hour_obj in case_obj.assignment_hourly_lines:
                if not ass_hour_obj.invoiced:
                    unbilled_amount += ass_hour_obj.amount * ass_hour_obj.billed_hours
                    
            for ass_fix_obj in case_obj.assignment_fixed_lines:
                if not ass_fix_obj.invoiced:
                    unbilled_amount += ass_fix_obj.amount +  ass_fix_obj.out_of_pocket_amount
          
            res[case_obj.id] =  unbilled_amount 
        return res
    
    def _get_billed_amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for case_obj in self.browse(cr, uid, ids, context=context):
            billed_amount = received_amount = spent_amount = 0.00
            for fixed_obj in case_obj.stage_lines:
                if fixed_obj.invoiced:
                    billed_amount += fixed_obj.amount + fixed_obj.out_of_pocket_amount
                    
            for expense_obj in case_obj.other_expenses_lines:
                if expense_obj.invoiced and expense_obj.billable == 'bill':
                    billed_amount += expense_obj.amount
                    
#             for associate_obj in case_obj.associate_payment_lines:
#                 if associate_obj.invoiced:
#                     billed_amount += associate_obj.amount
                    
            for ass_hour_obj in case_obj.assignment_hourly_lines:
                    billed_amount += ass_hour_obj.amount * ass_hour_obj.billed_hours
                    
            for ass_fix_obj in case_obj.assignment_fixed_lines:
                    billed_amount += ass_fix_obj.amount * ass_fix_obj.billed_hours
                    
          
            res[case_obj.id] =  billed_amount 
        return res
    
    def _get_received_amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        received_amount = 0.0
        for case_obj in self.browse(cr, uid, ids, context=context):
            received_amount = 0.0
            invoice_ids = self.pool.get('account.invoice').search(cr, SUPERUSER_ID, [('state','not in',['draft','cancel']),('type','in',['out_invoice',]),('case_id', '=', case_obj.id)], context=context)
            for invoice_obj in self.pool.get('account.invoice').browse(cr, SUPERUSER_ID, invoice_ids, context=context):
                paid_amount = invoice_obj.amount_total - invoice_obj.residual
                received_amount += paid_amount
            res[case_obj.id] = received_amount
        return res
    
    def _get_spent_amount(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        spent_amount = 0.0
        account_ids = [account_obj.id for account_obj in self.pool.get('res.users').browse(cr, SUPERUSER_ID, SUPERUSER_ID, context=context).company_id.expense_account_ids]
        for case_obj in self.browse(cr, uid, ids, context=context):
	    spent_amount = 0.0
            line_ids = self.pool.get('account.move.line').search(cr, SUPERUSER_ID, [('account_id', 'in', account_ids),('case_id', '=', case_obj.id),('debit', '!=', False)], context=context)
            for line_obj in self.pool.get('account.move.line').browse(cr, SUPERUSER_ID, line_ids, context=context):
                spent_amount += line_obj.debit
            
#             for associate_obj in case_obj.associate_payment_lines:
#                 if associate_obj.invoiced:
#                     spent_amount += associate_obj.amount
                    
            res[case_obj.id] = spent_amount
        return res
            
   
    def _get_stage_case_ids(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('fixed.price.stages')
        return [line.case_id.id for line in line_obj.browse(cr, uid, ids, context=context)]
    
    def _get_expense_case_ids(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('other.expenses').browse(cr, uid, ids, context=context):
            result[line.case_id.id] = True
        return result.keys()
    
    def _get_assignment_case_ids(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('assignment.wise').browse(cr, uid, ids, context=context):
            if line.case_fixed_id:
                result[line.case_fixed_id.id] = True
            elif line.case_hourly_id:
                result[line.case_hourly_id.id] = True
        return result.keys()
    
    def _get_associate_case_ids(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('associate.payments').browse(cr, uid, ids, context=context):
            result[line.case_id.id] = True
        return result.keys()
    
    def _get_out_standing_amount(self, cr, uid, ids, field_name, args, context=None):
        res={}
        uid = SUPERUSER_ID
        for obj in self.browse(cr, uid, ids):
            outstand = 0.00
            reids = self.pool.get('case.sheet.invoice').search(cr, uid, [('case_id','=',obj.id)])
            for line in self.pool.get('case.sheet.invoice').browse(cr, uid, reids):
                if line.invoice_id and line.invoice_id.state in ('draft','open'):                    
                    outstand += line.invoice_id.residual
            res[obj.id] = outstand        
                    
        return res
    
    def _get_first_opposite_party(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for case_obj in self.browse(cr, uid, ids, context=context):
            res[case_obj.id] = {
                'first_party': '',
                'opposite_party': '',
                
                }
            if case_obj.first_parties:
                type = self.pool.get('first.parties.details').get_selection_value(cr, uid, 'type' , case_obj.first_parties[0].type)
                res[case_obj.id]['first_party'] = case_obj.first_parties[0].name + '(' + type + ')'
                
            if case_obj.opp_parties:
                type = self.pool.get('opp.parties.details').get_selection_value(cr, uid, 'type' , case_obj.opp_parties[0].type)
                res[case_obj.id]['opposite_party'] = case_obj.opp_parties[0].name + '(' + type + ')'
            
        return res
    
    def _get_first_part_case_ids(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('first.parties.details').browse(cr, uid, ids, context=context):
            result[line.party_id.id] = True
        return result.keys()
    
    def _get_opp_part_case_ids(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('opp.parties.details').browse(cr, uid, ids, context=context):
            result[line.party_id.id] = True
        return result.keys()
    
    

   
    _columns = {
    		'name': fields.char('File Number', size=64, required=False, readonly=False, select=True, track_visibility='always'),
    		'date':fields.date('Date' , track_visibility='onchange'),
    		'company_ref_no':fields.char('Client Ref #',size=40, track_visibility='onchange'),
    		'group_val':fields.selection([('individual','INDIVIDUAL'),('proprietary','PROPRIETARY'),('company','COMPANY'),('firm','FIRM'),('llp','LLP'),('trust','TRUST'),('bank','BANK'),('others','OTHERS')],'Group', track_visibility='onchange'),
    		'client_id': fields.many2one('res.partner','Client Name', required=True, track_visibility='onchange'),
    		'contact_partner1_id': fields.many2one('res.partner','Contact Person 1', track_visibility='onchange'),
    		'contact_partner2_id': fields.many2one('res.partner','Contact Person 2', track_visibility='onchange'),
    		'work_type':fields.selection([('civillitigation', 'Civil Litigation'),('criminallitigation', 'Criminal Litigation'), ('non_litigation', 'Non Litigation'), ('arbitration', 'Arbitration'),('execution', 'Execution'),('mediation', 'Mediation')], 'Type of Work', required=True, track_visibility='onchange'),
    		'court_district_id': fields.many2one('district.district','Court District', track_visibility='onchange'),
    		'court_location_id': fields.many2one('court.location','Court Location', track_visibility='onchange'),
    		'court_id': fields.many2one('court.master','Court Name', track_visibility='onchange'),
            'no_court':fields.boolean('No Court'),
    		'arbitrator_id': fields.many2one('arbitrator.master','Arbitrator', track_visibility='onchange'),
    		'mediator_id': fields.many2one('mediator.master','Mediator', track_visibility='onchange'),
    		'assignee_id': fields.many2one('hr.employee','Assignee',required=True, track_visibility='onchange'),
    		'other_assignee_id': fields.many2one('res.partner','External Other Associate', track_visibility='onchange'),
    		'other_assignee_ids':fields.one2many('other.associate','case_id','External Other Associate(s)'),
    		'connected_matter': fields.text('Connected Matter', track_visibility='onchange'),
    		'casetype_id': fields.many2one('case.master','Case Type', required=True, track_visibility='onchange'),
    		'our_client':fields.selection([('first','First Party'),('opposite','Opposite Party')],'Side', track_visibility='onchange'),
    		'lodging_number':fields.char('Lodging Number', track_visibility='onchange'),
    		'lodging_date':fields.date('Lodging Date', track_visibility='onchange'),
    		'reg_number':fields.char('Case No.', track_visibility='onchange'),
    		'reg_date':fields.date('Case Date', track_visibility='onchange'),
    		'tasks_lines': fields.one2many('case.tasks.line', 'case_id', 'Assignee Tasks', ),
    		'associate_tasks_lines': fields.one2many('associate.tasks.line', 'case_id', 'Associate Tasks',),
    		'other_expenses_lines': fields.one2many('other.expenses', 'case_id', 'Other Expenses',track_visibility='onchange'),
    		'client_tasks_lines': fields.one2many('client.tasks.line', 'case_id', 'Client Tasks'),
    		'associate_payment_lines':fields.one2many('associate.payment', 'case_id', 'Associate Payment Lines'),
    		'first_parties':fields.one2many('first.parties.details','party_id','First Party Lines'),
    		'opp_parties':fields.one2many('opp.parties.details','party_id','Opposite Party Lines'),
    		'bill_type':fields.selection([('fixed_price','Fixed Price'),('assignment_wise','Assignment Wise')],'Billing Type', required=False, track_visibility='onchange'),
    		'stage_lines':fields.one2many('fixed.price.stages','case_id','Fixed Price Stages'),
    		'fixed_price':fields.float('Fixed Price Amount', track_visibility='onchange'),
    		'assignment_hourly_lines':fields.one2many('assignment.wise','case_hourly_id','Assignment Wise Hourly Lines'),
    		'assignment_fixed_lines':fields.one2many('assignment.wise','case_fixed_id','Assignment Wise Fixed Lines'),
    		'total_projected_amount':fields.float('Total Projected Amount', track_visibility='onchange'),
    		'assignment_approval_date':fields.date('Approval Date' , track_visibility='onchange'),
    		'effective_court_proceed_amount':fields.float('Effective Court Proceedings Amount', track_visibility='onchange'),
    		'non_effective_court_proceed_amount':fields.float('Non-Effective Court Proceedings Amount', track_visibility='onchange'),
    		'project_id':fields.many2one('project.project','Project ID'),
    		'branch_id':fields.many2one('sale.shop','Branch', required=False),
    		'state': fields.selection([
		    ('new', 'New'),
		    ('inprogress', 'In Progress'),
		    ('cancel', 'Cancelled'),
		    ('transfer','Transferred'),
		    ('won', 'Won'),
		    ('arbitrated', 'Arbitrated'),
		    ('withdrawn', 'With Drawn'),
		    ('lost', 'Lost'),
		    ('inactive', 'Inactive'),
            ('hold', 'Hold'),
		    ('done', 'Closed'),
		    ], 'Status', readonly=True, select=True, track_visibility='onchange'),
		'inward_register': fields.one2many('inward.register','file_number','Inward Register'),
		'outward_register': fields.one2many('outward.register','file_number','Outward Register'),
		'court_proceedings':fields.one2many('court.proceedings','case_id','Court Proceedings'),
		'close_comments':fields.text('Close Comments'),
		'close_date':fields.date('Close Date', track_visibility='onchange'),
		'cancel_comments':fields.text('Cancel Comments'),
		'cancel_date':fields.date('Cancel Date', track_visibility='onchange'),
		'state_id':fields.many2one('res.country.state', string='State', track_visibility='onchange'),
		'zone_id':fields.many2one('state.zone', 'Zone'),
		'district_id':fields.many2one('district.district', 'Assignee District', track_visibility='onchange'),
		'district_id_associate':fields.many2one('district.district', 'Associate District'),
		'location':fields.char('Location'),
		'division_id':fields.many2one('hr.department', 'Department/Division', track_visibility='onchange', ondelete="restrict", required=True),
		'ho_branch_id':fields.many2one('ho.branch','Location', track_visibility='onchange', ondelete="restrict", required=True),
		'parent_id_manager':fields.related('assignee_id', 'parent_id', type='many2one', relation='hr.employee', string="Manager", store=False),
		'transfer_location_id': fields.many2one('ho.branch','Transferred Location'),
		'transfer_file_number': fields.char('Transferred File Number'),
        'transfer_file_number_id': fields.many2one('case.sheet','Transferred File Number'),
		'outstanding_amount':fields.function(_get_out_standing_amount,type='float',string='Out-Standing Amount'),
        'company_id':fields.many2one('res.company','Company'),
        'client_service_executive_id': fields.many2one('hr.employee','Client Service Manager', track_visibility='onchange'),
        'client_service_manager_id': fields.many2one('hr.employee','Client Relationship Manager', track_visibility='onchange'),
        'region': fields.related('state_id', 'region', store=True, type='selection', selection=[('north','North'),('east','East'),('west','West'),('south','South')], string='Region'),
        #Add billed field // Sanal Davis // 5-6-15
                
        'bill_state': fields.function(_get_bill_state, string='Billed', type='selection', selection=[('none','/'), ('not_billed','Not Billed'),('partial_billed','Partially Billed'),('fully_billed','Fully Billed')],
                                        store = {
                                            'case.sheet': (lambda self, cr,uid,ids,c: ids, ['stage_lines','fixed_price', 'bill_type', 'assignment_fixed_lines', 'assignment_hourly_lines', 'state'], 10),
                                            'fixed.price.stages': (_get_stage_case_ids, ['amount', 'state', 'invoiced'], 10),
                                            'assignment.wise': (_get_assignment_case_ids, ['amount', 'billed_hours', 'remaining_hours','hours_spent', 'invoiced', 'state'], 10),
                                          }),
        'lot_name': fields.char('Lot Number', size=64, readonly=True, track_visibility='onchange'),
        'show_billing': fields.boolean('Show Billing'),
        'estimated_time': fields.integer('Estimated Time'),
        'estimated_month': fields.integer('Estimated Months'),
        'estimated_hearing': fields.integer('Estimated Hearings'),
        'refered_by': fields.selection([('employee', 'Employee'), ('partner', 'Partner')], 'Refered By'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'employee_partner_id': fields.many2one('hr.employee', 'Partner1'),
        
        'arbitration_amount': fields.float('Arbitration Fee', track_visibility='onchange'),
        'billed_amount': fields.function(_get_billed_amount, type='float', string='Billed Amount'),
        'spent_amount': fields.function(_get_spent_amount, type='float', string='Spent Amount'),
        'received_amount': fields.function(_get_received_amount, type='float', string='Received Amount'),
        'opposite_party': fields.function(_get_first_opposite_party, type='char', string='Opposite Party', multi="party", store={
                                            'case.sheet': (lambda self, cr, uid, ids, c={}: ids, ['opp_parties'], 10),
                                            'opp.parties.details': (_get_opp_part_case_ids, ['name', 'sl_no'], 10),
                                            }),
        'first_party': fields.function(_get_first_opposite_party, type='char', string='First Party', multi="party", store={
                                            'case.sheet': (lambda self, cr, uid, ids, c={}: ids, ['first_parties'], 10),
                                            'first.parties.details': (_get_first_part_case_ids, ['name', 'sl_no'], 10),
                                            }),
                
        'members': fields.many2many('res.users', 'case_user_rel', 'case_id', 'uid', 'Case Members'),
        
        'active': fields.boolean('Active'),
        'assignment_history': fields.one2many('case.assignment.history','case_id','Assignment History'),
        'court_no':  fields.selection(_get_court_no, 'Court No.', track_visibility='onchange'),
        
        'unbilled_amount': fields.function(_get_unbilled_amount, type='float', string='Unbilled Amount'),
        
        }
    _defaults = {
    	'date':lambda *a: time.strftime('%Y-%m-%d'),
#     	'lodging_date':lambda *a: time.strftime('%Y-%m-%d'),
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=c),
    	'state':'new',
    	'name': lambda obj, cr, uid, context: '/',
        'active': True,
    }
    
#     def _check_fixed_price_amount(self, cr, uid, ids, context=None):
#         for case_obj in self.browse(cr, uid, ids, context=context):
#             total_amount = 0.0
#             for line_obj in case_obj.stage_lines:
#                 total_amount += line_obj.amount + line_obj.out_of_pocket_amount
#             if total_amount > case_obj.fixed_price:
#                 return False
#         return True
    
    def _check_fixed_price_amount(self, cr, uid, ids, context=None):
        for case_obj in self.browse(cr, uid, ids, context=context):
            total_amount = 0.0
            if case_obj.show_billing and case_obj.fixed_price and case_obj.bill_type == 'fixed_price':
                if case_obj.stage_lines:
                    for line_obj in case_obj.stage_lines:
                        total_amount += line_obj.amount + line_obj.out_of_pocket_amount
                    if total_amount != case_obj.fixed_price:
                        return False
                else:
                    return False
        return True
    
    _constraints = [
        (_check_fixed_price_amount, '\nError!\n\nFixed price stages amount total do not exceed the fixed price amount / Please enter tasks details in fixed price stages', ['fixed_price', 'stage_lines']),
#         (_check_stage_lines, '\nError!\n\nFixed price stages amount total do not exceed the fixed price amount / Please enter tasks details in fixed price stages', ['fixed_price', 'stage_lines']),
        
    ]
    
    
    
    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        
        res = super(case_sheet,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        return res
    
    
    def button_refresh(self, cr, uid, ids, context=None):
        return True
    
    def case_user_access(self, cr, uid, ids, context=None):
        cr.execute("select id,project_id from case_sheet;")
        case_ids = map(lambda x: x, cr.fetchall())
        length = len(case_ids)
        i=1
        for data in case_ids:
            if data[1]:
                cr.execute('select uid from project_user_rel where project_id=%s;',(data[1],))
                user_ids = map(lambda x: x[0], cr.fetchall())
                for user in user_ids:
                    cr.execute('insert into case_user_rel values (%s,%s);',(data[0],user))
            _logger.info('Processing %s/%s'%(i,length))
            i += 1
        return True
    
    
    def update_user_access_in_case_sheet(self, cr, uid, ids, context=None):
        dept_pool = self.pool.get('hr.department')
        employee_pool = self.pool.get('hr.employee')
        cr.execute("select id,project_id, division_id,client_service_manager_id,client_service_executive_id,assignee_id from case_sheet where state not in ('draft','done','cancel','transfer');")
        case_ids = map(lambda x: x, cr.fetchall())
        length = len(case_ids)
        i=1
        for data in case_ids:
            employee_ids = []
            employee_ids.append(data[3])
            employee_ids.append(data[4])
            employee_ids.append(data[5])
            
            cr.execute('select assign_to from case_tasks_line where case_id=%s;',(data[0],))
            employee_ids += map(lambda x: x[0], cr.fetchall())
            cr.execute('select assign_to_in_associate from associate_tasks_line where case_id=%s;',(data[0],))
            employee_ids += map(lambda x: x[0], cr.fetchall())
            cr.execute('select assign_to_in_client from client_tasks_line where case_id=%s;',(data[0],))
            employee_ids += map(lambda x: x[0], cr.fetchall())
            
            div_obj  = dept_pool.browse(cr, uid, data[2], context=context)
            if div_obj.employee_ids:
                employee_ids += [emp.id for emp in div_obj.employee_ids]
            if div_obj.manager_id:
                employee_ids.append(div_obj.manager_id.id)
            parent_ids = dept_pool.get_parent_records(cr, uid, div_obj, [],context=context)
            for dep_obj in dept_pool.browse(cr, uid, parent_ids, context=context):
                if dep_obj.manager_id:
                    employee_ids.append(dep_obj.manager_id.id)
            
            employee_ids=list(set(employee_ids))
            if None in employee_ids:
                employee_ids.remove(None)
            if False in employee_ids:
                employee_ids.remove(False)
            cr.execute('delete from project_user_rel where project_id=%s;',(data[1],))
            cr.execute('select id from hr_employee where id in %s;',(tuple(employee_ids),))
            employee_ids = map(lambda x: x[0], cr.fetchall())
            user_ids = [emp.user_id.id for emp in employee_pool.browse(cr, uid, employee_ids, context=context) if emp and emp.user_id]
            user_ids = list(set(user_ids))
            if data[1]:
                for user in user_ids:
                    cr.execute('insert into project_user_rel values (%s,%s);',(data[1],user))
            _logger.info('Processing %s/%s'%(i,length))
            i += 1
                
        return True
    
    
    def update_tasks_date(self, cr, uid, ids, context=None):
        
        cr.execute('select id,start_date,task_id,(select state from project_task as pt where ct.task_id=id) from case_tasks_line as ct where ct.days=0;')
        lines = map(lambda x: x, cr.fetchall())
        cr.execute('select id,start_date,task_id,(select state from project_task as pt where at.task_id=id) from associate_tasks_line as at where at.days=0;')
        lines += map(lambda x: x, cr.fetchall())
        cr.execute('select id,start_date,task_id,(select state from project_task as pt where cl.task_id=id) from client_tasks_line as cl where cl.days=0;')
        lines += map(lambda x: x, cr.fetchall())
        
        for data in lines:
            if data[3] != 'done':
                return_date = (datetime.strptime(data[1], '%Y-%m-%d') + timedelta(days=730)).strftime('%Y-%m-%d')
                return_date = self.pool.get('hr.holidays.public').get_next_working_day(cr, uid, return_date)
                ret = str(return_date.strftime('%Y-%m-%d'))
                cr.execute('update case_tasks_line set planned_completion_date=%s,days=%s where id=%s;',(ret, 730, data[0]))
                cr.execute('update project_task set date_deadline=%s,planned_hours=%s,date_end=%s where id=%s;',(ret, 730*8, return_date, data[2]))
        
        return True
    
    def get_selection_value(self, cr, uid, field, field_id):
        res = ''
        if not field_id:
            return res
        fields_get_result = self.fields_get(cr, uid, [field,])
        if fields_get_result:
            selection = fields_get_result[field]['selection']
            if selection:
                for key_value in selection:
                    if field_id == key_value[0]:
                        res = key_value[1]
        return res
    
    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        if context is None:
            context = {}
        res = super(case_sheet, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        if context.get('exported', False) and res and ids:
            type = False
            if isinstance(ids, int):
                type = res['work_type']
            elif isinstance(ids, list):
                type = res[0]['work_type']
            if type:
                work_type = self.get_selection_value(cr, uid, 'work_type' , type).encode('utf8', 'ignore')
                if isinstance(ids, int):
                    res['work_type'] = work_type
                elif isinstance(ids, list):
                    res[0]['work_type'] = work_type
        return res

    
    #Starting // Automatically load work_type using division_id // Sanal Davis // 5-6-15
    def onchange_division_id(self, cr, uid, ids, division_id, context=None):
        work_type = False
        if division_id:
            department = self.pool.get('hr.department').browse(cr, uid, division_id, context=context)
            work_type = (department.work_type or False)
        return {'value': {'work_type' : work_type}}
    
    #Load Client Relationship Manager using Client Service Executive
    def onchange_service_manager(self, cr, uid, ids, client_service_executive_id, context=None):
        client_service_manager_id = False
        if client_service_executive_id:
            employee = self.pool.get('hr.employee').browse(cr, uid, client_service_executive_id, context=context)
            client_service_manager_id = (employee.parent_id and employee.parent_id.id or False)
        return {'value': {'client_service_manager_id' : client_service_manager_id}}
    
    #Set District As Null when Change the State
    def onchange_state(self, cr, uid, ids, state_id, context=None):
        return {'value':{ 'district_id' : False}}
    
    def update_assignment_hours(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for case in self.browse(cr, uid, ids, context=context):
            for line in case.assignment_hourly_lines:
                if line.hours_spent>0:
                    remaining_hours = line.remaining_hours + line.hours_spent
                    self.pool.get('assignment.wise').write(cr, uid, [line.id], {'remaining_hours':remaining_hours,'hours_spent':0})
        return True
    
    def default_get(self, cr, uid, fields_list, context=None):
        if not context:
            context = {}
        global line_count_slno
        line_count_slno =0
        res = super(case_sheet, self).default_get(cr, uid, fields_list, context=context)
        return res
        
    def onchange_bill_type(self, cr, uid, ids, bill_type, casetype_id, context=None):
        val = {}
        if not casetype_id:
            warning = {
                       'title': _('Error!'),
                       'message' : _('Please select Case Type first before selecting the Billing Type')
                    }
            val['bill_type'] = False
            return {'value': val, 'warning': warning}  
        elif bill_type == 'fixed_price':
            fixed_price = self.pool.get('case.master').browse(cr, uid, casetype_id, context=context).prefixed_price
            val = {'fixed_price':fixed_price}
        return {'value':val}
        
    def onchange_client(self, cr, uid, ids, client_id, our_client, context=None):
        val = {'first_parties' : [], 'opp_parties': []}
        if client_id:
            client = self.pool.get('res.partner').browse(cr, uid, client_id)        
            if our_client == 'first':      
                val['first_parties'] = [(0, 0, {'type':'claimaints','name':client.name,})]
            else:
                val['opp_parties'] = [(0, 0, {'type':'respondant', 'name':client.name,})]
            val['client_service_manager_id'] = client.client_manager_id and client.client_manager_id.id or False
        return {'value':val} 
    
    
    def onchange_our_client(self, cr, uid, ids, our_client, client_id, context=None):
        val = {'first_parties' : [], 'opp_parties': []}
        if client_id and our_client:
            client = self.pool.get('res.partner').browse(cr, uid, client_id) 
            if our_client == 'first':      
                val['first_parties'] = [(0, 0, {'type':'claimaints','name':client.name,})]
            else:
                val['opp_parties'] = [(0, 0, {'type':'respondant', 'name':client.name,})]
        return {'value':val} 
    
    
    def onchange_cnt(self, cr, uid, ids, recep_date, count,target_field, context=None):
        return_date = (datetime.strptime(recep_date, '%Y-%m-%d') + timedelta(days=count)).strftime('%Y-%m-%d')
        val = {
            target_field: str(return_date)
        }
        return {'value': val}
        
    def onchange_ho_branch(self, cr, uid, ids, ho_branch, context=None):
        val = {
            'division_id': False,
            'assignee_id': False,
            }
#         if ho_branch:
#             obj = self.pool.get('ho.branch').browse(cr, uid, ho_branch)
#             state_id = obj.state_id.id
#             val = {
#                 'state_id': state_id
#             }
#         else:
#             val = {'state_id':False}    
        return {'value': val}
    
    
    def hold_case_sheet(self, cr, uid, ids, context=None):
        for case_obj in self.browse(cr, uid, ids, context=context):
            type_ids = self.pool.get('project.task.type').search(cr, uid, [('state', '=', 'hold')], context=context)
            if type_ids:
                cr.execute("update project_task set state='hold', stage_id=%s  where project_id=%s and state in ('draft','pending', 'open');",(type_ids[0], case_obj.project_id.id))
        return self.write(cr, uid, ids, {'state': 'hold'}, context=context)
    
    def reopen_case_sheet(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
            if obj.project_id:
                self.write(cr, uid, [obj.id], {'state':'inprogress'})
                type_ids = self.pool.get('project.task.type').search(cr, uid, [('state', '=', 'open')], context=context)
                if type_ids:
                    cr.execute("update project_task set state='open', stage_id=%s  where project_id=%s and state in ('hold');",(type_ids[0], obj.project_id.id))
            else:
                self.write(cr, uid, [obj.id], {'state':'new'})
        return True 
    
    def confirm_casesheet(self, cr, uid, ids, context=None):
        casesheet = self.browse(cr, uid, ids[0])
        casesheet_name = casesheet.name or ''
        date_today = time.strftime('%Y-%m-%d')
        if casesheet.name == '/':
            branch = casesheet.ho_branch_id
            state_code = casesheet.state_id.code
            obj_sequence = self.pool.get('ir.sequence')
            seqid = False
    #             if not branch.sequence_id:
    #                 seqid = self.pool.get('ho.branch').create_sequence(cr, uid, {'name':branch.name})
    #                 self.pool.get('ho.branch').write(cr, uid, [branch.id], {'sequence_id':seqid})
    #             new_seq = obj_sequence.next_by_id(cr, uid, (seqid and seqid or branch.sequence_id.id), context=context)
    #             vals['name'] = branch.code+'/'+state_code + '/'+self.pool.get('res.partner').browse(cr, uid, vals['client_id']).client_data_id+new_seq or '/'
            
            
            if not branch.sequence_id:
                seqid = self.pool.get('ho.branch').create_sequence(cr, uid, {'name':branch.name})
                self.pool.get('ho.branch').write(cr, uid, [branch.id], {'sequence_id':seqid})
            new_seq = obj_sequence.next_by_id(cr, uid, (seqid and seqid or branch.sequence_id.id), context=context)
            casesheet_name = branch.code+'/'+ casesheet.client_id.client_data_id + new_seq or '/'
            self.write(cr, uid, ids, {'name': casesheet_name, 'date': date_today}, context=context)
        
        
        type_ids = []
        task_type_pool = self.pool.get('project.task.type')
        project_pool = self.pool.get('project.project')
        phase_pool = self.pool.get('project.phase')
        task_pool = self.pool.get('project.task')
        dept_pool = self.pool.get('hr.department')
        user_pool = self.pool.get('res.users')
        csm = user_pool.has_group(cr, uid, 'legal_e.group_legal_e_client_service_manager')
        csm_super_id = uid
        if csm:
            csm_super_id = SUPERUSER_ID
        analy_ids = task_type_pool.search(cr, uid, [('name','=','New')])
        if len(analy_ids)>0:
            type_ids.append(analy_ids[0])
        else:
            analy_id = task_type_pool.create(cr, uid, {'name':'New','state':'draft','sequence':1})
            type_ids.append(analy_id)
        work_ids = task_type_pool.search(cr, uid, [('name','=','In Progress')])
        if len(work_ids)>0:
            type_ids.append(work_ids[0])
        else:
            work_id = task_type_pool.create(cr, uid, {'name':'In Progress','state':'open','sequence':2})
            type_ids.append(work_id)
            
        hold_ids = task_type_pool.search(cr, uid, [('name','=','Hold')])
        if len(hold_ids)>0:
            type_ids.append(hold_ids[0])
        else:
            hold_id = task_type_pool.create(cr, uid, {'name':'Hold','state':'pending','sequence':3})
            type_ids.append(hold_id)
            
        pending_ids = task_type_pool.search(cr, uid, [('name','=','Pending')])
        if len(pending_ids)>0:
            type_ids.append(pending_ids[0])
        else:
            pending_id = task_type_pool.create(cr, uid, {'name':'Pending','state':'pending','sequence':5})
            type_ids.append(pending_id)
            
        done_ids = task_type_pool.search(cr, uid, [('name','=','Completed')])
        if len(done_ids)>0:
            type_ids.append(done_ids[0])
        else:
            done_id = task_type_pool.create(cr, uid, {'name':'Completed','state':'done','sequence':4})
            type_ids.append(done_id)
        tot = 0.0
        for bill in casesheet.stage_lines:
            tot += bill.amount + bill.out_of_pocket_amount
        
        if tot != casesheet.fixed_price:
            raise openerp.exceptions.Warning(_('Fixed price amount must be equal to the billing stage line total amount .'))
        
        members = []
        if casesheet.client_service_executive_id:
            members.append(casesheet.client_service_executive_id.user_id.id)
        if casesheet.client_service_manager_id:
            members.append(casesheet.client_service_manager_id.user_id.id)
        if casesheet.division_id.employee_ids:
            if casesheet.division_id.manager_id:
                members.append(casesheet.division_id.manager_id.user_id.id)
            for empl in casesheet.division_id.employee_ids:
                if empl.user_id:
                    members.append(empl.user_id.id)
        parent_ids = dept_pool.get_parent_records(cr, uid, casesheet.division_id, [],context=context)
        for dep_obj in dept_pool.browse(cr, uid, parent_ids, context=context):
            if dep_obj.manager_id:
                members.append(dep_obj.manager_id.user_id.id)
        
        members = list(set(members))
        
        #Create a New Project
        if not casesheet.project_id:
            
            project_id = project_pool.create(cr, uid, {'name':casesheet_name,'use_tasks':True,'use_phases':True,'use_timesheets':True,'privacy_visibility':'employees','partner_id':casesheet.client_id.id,'user_id':casesheet.assignee_id.user_id.id, 'type_ids': [(6, 0, type_ids)],'members':[(6, 0, members)]})
        
        else:
            project_id = casesheet.project_id.id
            try:
                project_pool.write(cr, csm_super_id, [project_id], {'name':casesheet_name,'user_id':casesheet.assignee_id.user_id.id, 'members':[(6, 0, members)]}, context=context)
            except Exception:
                project_pool.write(cr, csm_super_id, [project_id], {'name':casesheet_name,'members':[(6, 0, members)]}, context=context)
                self.pool.get('account.analytic.account').write(cr, uid, [casesheet.project_id.analytic_account_id.id], {'user_id':casesheet.assignee_id.user_id.id}, context=context)
            
            
            
        self.write(cr, uid, ids, {'members':[(6, 0, members)]}, context=context)
        #Create Assignee Project Phases & Tasks
        i = 0
        for line in casesheet.tasks_lines:
            if not line.task_id:
                phase_id=False
                if line.phase_name:
                    phase_ids = phase_pool.search(cr, uid, [('name','=',line.phase_name.name),('project_id','=',project_id)])
                    if len(phase_ids)<=0:                    
                        phase_id=phase_pool.create(cr, uid, {'name':line.phase_name.name,'project_id':project_id,'product_uom':6,'duration':(line.days or 0)})
                    else:
                        phase_id = phase_ids[0]
                        phase = phase_pool.browse(cr, uid, phase_id)
                        duration = (line.days or 0) + (phase.duration or 0)
                        phase_pool.write(cr, uid, [phase_id],{'duration':duration})
        
                assigned = self.pool.get('hr.employee').browse(cr, uid, line.assign_to.id)
                project = project_pool.browse(cr, uid, project_id)
                if not assigned.user_id.id in project.members:
                    project_pool.write(cr, csm_super_id, [project.id],{'members':[(4, assigned.user_id.id)]})
                    self.write(cr, uid, ids,{'members':[(4, assigned.user_id.id)]})
                
                task_vals = {'project_id':project_id,'lot_name': casesheet.lot_name, 'phase_id':phase_id,'name':line.name.id,'task_for':'employee','date_deadline':line.planned_completion_date,'assignee_id':line.assign_to  and line.assign_to.id or casesheet.assignee_id.id, 'sequence':line.slno,'date_start':line.start_date,'date_end':line.planned_completion_date,'planned_hours':line.days*8,'remaining_hours':line.days*8}
                if i == 0:
                    task_type_ids = self.pool.get('project.task.type').search(cr, uid, [('state','=','open')],order='sequence')
                    task_vals.update({'state': 'open', 'stage_id': task_type_ids[0]})
                    i += 1
                task_id = task_pool.create(cr, uid, task_vals)
                
                if line.start_date == date_today:
                    self.pool.get('case.tasks.line').write(cr, uid, [line.id], {'task_id':task_id})
                else:
                    return_date = (datetime.strptime(date_today, '%Y-%m-%d') + timedelta(days=line.days)).strftime('%Y-%m-%d')
                    return_date = str(self.pool.get('hr.holidays.public').get_next_working_day(cr, uid, return_date))
                    self.pool.get('case.tasks.line').write(cr, uid, [line.id], {'task_id':task_id, 'start_date': date_today, 'planned_completion_date': return_date}, context=context)
        
        #Create Associate Project Phases & Tasks
        for line in casesheet.associate_tasks_lines:
            if not line.task_id:
                phase_id=False
                if line.phase_name:
                    phase_ids = phase_pool.search(cr, uid, [('name','=',line.phase_name.name),('project_id','=',project_id)])
                    if len(phase_ids)<=0:                    
                        phase_id=phase_pool.create(cr, uid, {'name':line.phase_name.name,'project_id':project_id,'product_uom':6,'duration':(line.days or 0)})
                    else:
                        phase_id = phase_ids[0]
                        phase = phase_pool.browse(cr, uid, phase_id)
                        duration = (line.days or 0) + (phase.duration or 0)
                        phase_pool.write(cr, uid, [phase_id],{'duration':duration})
                if not line.task_id:    
                    task_id = task_pool.create(cr, uid, {'project_id':project_id,'lot_name': casesheet.lot_name,'phase_id':phase_id,'name':line.name.id,'task_for':'associate','date_deadline':line.planned_completion_date,'other_assignee_id':(line.assign_to_in_associate and line.assign_to_in_associate.id or (casesheet.other_assignee_id and casesheet.other_assignee_id.id or False)), 'sequence':line.slno,'date_start':line.start_date,'date_end':line.planned_completion_date,'planned_hours':line.days*8,'remaining_hours':line.days*8})
                    if line.start_date == date_today:
                        self.pool.get('associate.tasks.line').write(cr, uid, [line.id], {'task_id':task_id})
                    else:
                        return_date = (datetime.strptime(date_today, '%Y-%m-%d') + timedelta(days=line.days)).strftime('%Y-%m-%d')
                        return_date = str(self.pool.get('hr.holidays.public').get_next_working_day(cr, uid, return_date))
                        self.pool.get('associate.tasks.line').write(cr, uid, [line.id], {'task_id':task_id, 'start_date': date_today, 'planned_completion_date': return_date}, context=context)
        
        #Create Client Project Phases & Tasks
        for line in casesheet.client_tasks_lines:
            if not line.task_id:
                    phase_id=False
                    if line.phase_name:
                        phase_ids = phase_pool.search(cr, uid, [('name','=',line.phase_name.name),('project_id','=',project_id)])
                        if len(phase_ids)<=0:                    
                            phase_id=phase_pool.create(cr, uid, {'name':line.phase_name.name,'project_id':project_id,'product_uom':6,'duration':(line.days or 0)})
                        else:
                            phase_id = phase_ids[0]
                            phase = phase_pool.browse(cr, uid, phase_id)
                            duration = (line.days or 0) + (phase.duration or 0)
                            phase_pool.write(cr, uid, [phase_id],{'duration':duration})
                    if not line.task_id:        
                        task_id = task_pool.create(cr, uid, {'project_id':project_id,'lot_name': casesheet.lot_name,'phase_id':phase_id,'name':line.name.id,'task_for':'customer','date_deadline':line.planned_completion_date,'client_id':line.assign_to_in_client and line.assign_to_in_client.id or casesheet.client_id.id, 'sequence':line.slno,'date_start':line.start_date,'date_end':line.planned_completion_date,'planned_hours':line.days*8,'remaining_hours':line.days*8})
                        if line.start_date == date_today:
                            self.pool.get('client.tasks.line').write(cr, uid, [line.id], {'task_id':task_id})
                        else:
                            return_date = (datetime.strptime(date_today, '%Y-%m-%d') + timedelta(days=line.days)).strftime('%Y-%m-%d')
                            return_date = str(self.pool.get('hr.holidays.public').get_next_working_day(cr, uid, return_date))
                            self.pool.get('client.tasks.line').write(cr, uid, [line.id], {'task_id':task_id, 'start_date': date_today, 'planned_completion_date': return_date}, context=context)

        return self.write(cr, uid, ids, {'state':'inprogress','project_id':project_id})
    
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(case_sheet, self).write(cr, uid, ids, vals, context=context)
#         for case_obj in self.browse(cr, uid, ids, context=context):
#             if  case_obj.division_id.manager_id.id != case_obj.assignee_id.id:
#                 raise openerp.exceptions.Warning(_('Please enter the department head as assignee in casesheet.'))
        
        if vals.get('fixed_price', False):
            for case_obj in self.browse(cr, uid, ids, context=context):
                if case_obj.state != 'new':
                    if not self.pool.get('res.users').has_group(cr, uid, 'legal_e.group_case_sheet_operation_manager'):
                        raise osv.except_osv(_('Warning!'), _('You are not permitted to modifie the Fixed Price Amount.Please contact case sheet operations manager.'))
        
        return res
    
    
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        employee_obj = self.pool.get('res.partner').browse(cr, uid, vals['client_id'])
        if not vals.get('contact_partner1_id', False):
            if employee_obj.child_ids:
                for item in employee_obj.child_ids:
                    vals['contact_partner1_id'] = item.id
                    break
        
        if vals.has_key('tasks_lines') and len(vals['tasks_lines'])<=0:
            raise openerp.exceptions.Warning(_('Please enter the Assignee Tasks Details.'))
        vals.update({'show_billing': True})
        
#         if vals.get('division_id', False) and vals.get('assignee_id', False):
#             department = self.pool.get('hr.department').browse(cr, uid, vals['division_id'], context=context)
#             if department.manager_id.id != vals['assignee_id']:
#                 raise openerp.exceptions.Warning(_('Please enter the department head as assignee in casesheet.'))
            
        retvals = super(case_sheet, self).create(cr, uid, vals, context=context)
        if context.get('case_copy', False):
            case_obj = self.browse(cr, uid, retvals, context=context)
            for line in case_obj.tasks_lines:
                for bill in case_obj.stage_lines:
                    if bill.name.name == line.name:
                        self.pool.get('fixed.price.stages').write(cr, uid, [bill.id], {'name': line.id}, context=context)
#                         bill.write({'name': line.id})
        return retvals
    
    def update_casesheet(self, cr, uid, ids, context=None):
        case_ids = self.search(cr, uid, [('lot_name','=', 'NS13')], context=context)
        for case_obj in  self.browse(cr, uid, case_ids, context=context):
            for line in case_obj.tasks_lines:
                for bill in case_obj.stage_lines:
                    if bill.name.name == line.name:
                        bill.write({'name': line.id})
        return True
    
    def update_project(self, cr, uid, ids, context=None):
        project_ids = self.pool.get('project.project').search(cr, uid, [('name', '=', '/')], context=context)
        for project_id in project_ids:
            case_ids = self.search(cr, uid, [('project_id','=', project_id)], context=context)
            for case_obj in self.browse(cr, uid, case_ids, context=context):
                self.pool.get('project.project').write(cr, uid, [project_id], {'name': case_obj.name}, context=context)
                
        return True
        
    def copy(self, cr, uid, ids, default=None, context=None):
        if context is None:
            context = {}
        context.update({'case_copy': True})
        default = default or {}
        default.update({
            'state':'new',
            'name':'/',
            'date':time.strftime('%Y-%m-%d'),
            'project_id':False,
            'court_proceedings': [],
            'inward_register': [],
            'outward_register': [],
            'assignment_history': [],
            'show_billing': False,
            'active': True,
        })
    
        if not context.get('bulk_case', False):
                default.update({
                    'lot_name': False,
                })
        
        retval = super(case_sheet, self).copy(cr, uid, ids, default, context)
        return retval
        
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
#         unlink_ids = []
#         raise openerp.exceptions.Warning(_('You cannot delete a Case Sheet.'))
#         osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        
        for case_obj in self.browse(cr, uid, ids, context=context):
            if case_obj.project_id:
                task_ids = self.pool.get('project.task').search(cr, uid, [('project_id', '=', case_obj.project_id.id)], context=context)
                if task_ids:
                    self.pool.get('project.task').unlink(cr, uid, task_ids, context=context)
                self.pool.get('project.project').unlink(cr, uid, [case_obj.project_id.id], context=context)
            
        res = super(case_sheet, self).unlink(cr, uid, ids, context=context)
        return res
        
    
    def view_court_proceedings(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'legal_e', 'action_court_proceedings')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        proceed_ids = []
        for case_obj in self.browse(cr, uid, ids, context=context):
            proceed_ids += [proceed.id for proceed in case_obj.court_proceedings]
        #choose the view_mode accordingly
        if proceed_ids:
            result['domain'] = "[('id','in',["+','.join(map(str, proceed_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'legal_e', 'court_proceedings_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = False
            result['context'] = {
                'default_case_id': ids[0],
                } 
        return result
    
    def project_tree_view(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'project', 'act_project_project_2_project_task_all')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['context'] = {
            'search_default_project_id': [obj.project_id.id], 
            'default_project_id': obj.project_id.id, 
            'active_test': False 
            }
        return result
        
        
    def onchange_client_id(self, cr, uid, ids, part, context=None):
        if not part:
            return {'value': {'contact_partner1_id': False, 'contact_partner2_id': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        addr = self.pool.get('res.partner').search(cr, uid, [('parent_id','=',part.id),('type','=','contact')])
        val = {
            'contact_partner1_id': (addr and len(addr)>0 and addr[0] or False),
            'contact_partner2_id': (addr and len(addr)>1 and addr[1] or False),
        }
        return {'value': val}
    
    def onchange_work_type(self, cr, uid, ids, worktype, context=None):
        if not worktype:
            return {'value': {'casetype_id':False}}
        return {'value': {'casetype_id':False}}
    
    def onchange_case_type(self, cr, uid, ids, casetype, context=None):
        if not casetype:
            return {'value': {'no_court':False}}
        no_court = self.pool.get('case.master').browse(cr, uid, casetype, context=context).no_court
        return {'value': {'no_court': no_court}}
        
    def save_tasks_as_template(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        tasksids = self.pool.get('case.tasks.line').search(cr, uid, [('case_id','=',ids[0])])
        for task in self.pool.get('case.tasks.line').browse(cr, uid, tasksids):
            pid = self.pool.get('task.template').create(cr, uid, {'name':obj.work_type,'casetype_id':obj.casetype_id.id, 'tasks_lines':[(0, 0, {'name':task.name.id,'slno':task.slno,'days':task.days,'phase_name':task.phase_name.id})]})
        return True
        
    def close_case_sheet(self, cr, uid, ids, context=None):
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'wizard_case_close_id')
        except ValueError, e:
            view_id = False
        return {
            'name':_("Close Case"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'case.close',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'case_id': ids
            }
        }
        
          
        
    def cancel_case_sheet(self, cr, uid, ids, context=None):
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'wizard_case_cancel_id')
        except ValueError, e:
            view_id = False
        return {
            'name':_("Cancel Case Sheet"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'case.cancel',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'case_id': ids
            }
        }  
        #return self.write(cr, uid, ids, {'state':'cancel'})
        
    def transfer_case_sheet(self, cr, uid, ids, context=None):
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'wizard_case_transfer_id')
        except ValueError, e:
            view_id = False
        return {
            'name':_("Transfer Case Sheet"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'case.transfer',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'case_id': ids
            }
        }
        
    def onchange_assignee(self, cr, uid, ids, worktype, casetype, date, assignee_id, division_id, context=None):
        val = {}
        #Add if statement for removing error. // Sanal Davis //8-6-15
        if assignee_id:
            case = False
            if ids:
                case = self.pool.get('case.sheet').browse(cr, uid, ids[0])
            tempids = self.pool.get('task.template').search(cr, uid, [('name','=',worktype),('casetype_id','=',casetype)])
            #Starting #Take Office Value # Sanal Davis # 27/5/15 
            employee_pool = self.pool.get('hr.employee')
            employee = employee_pool.browse(cr,uid,assignee_id)
            # Ending
            temp_list = []
            if not date:
                date = time.strftime('%Y-%m-%d')
            for tempmain in self.pool.get('task.template').browse(cr, uid, tempids):
                for temp in tempmain.tasks_lines:
                    return_date = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=temp.days)).strftime('%Y-%m-%d')
                    return_date = self.pool.get('hr.holidays.public').get_next_working_day(cr, uid, return_date)            
                    #Add office in task lines # Sanal Davis #27/5/15
                    temp_list.append({'slno':temp.slno,'name':temp.name.id,'days':temp.days,'planned_completion_date':str(return_date),'phase_name':temp.phase_name.id,'start_date': date,'state':'New','assign_to':assignee_id})
            val['tasks_lines']= temp_list
            if not division_id:
                if assignee_id:
                    division = self.pool.get('hr.employee').read(cr, uid, assignee_id,['department_id'])
                    if division.has_key('department_id') and division['department_id']:
                        division_id = division['department_id'][0]
                val['division_id'] = division_id
            if case and case.project_id:
                val['project_id.user_id'] = case.assignee_id.user_id.id
                self.update_project_details(cr, uid, ids, assignee_id, division_id, context=context)
        return {'value': val}
    
    def update_project_details(self, cr, uid, ids, assignee_id, division_id, context=None):
        if ids:
            case = self.pool.get('case.sheet').browse(cr, uid, ids[0])
            assignee = self.pool.get('hr.employee').browse(cr, uid, assignee_id)
            members = []
            if assignee and assignee.department_id:
                emplids = self.pool.get('hr.employee').search(cr, uid, [('department_id','=',assignee.department_id.id)])
                for empl in self.pool.get('hr.employee').browse(cr, uid, emplids):
                    if empl.user_id:
                        members.append(empl.user_id.id)
                        self.pool.get('project.project').write(cr, uid, [case.project_id.id], {'user_id':assignee.user_id.id, 'members':[(4, empl.user_id.id)]})
                        self.write(cr, uid, [case.id], {'members':[(4, empl.user_id.id)]})
        return True    
        
    def invoice_case_sheet(self, cr, uid, ids, context=None):
        case = self.browse(cr, uid, ids[0])
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'wizard_case_sheet_inv_id')
        except ValueError, e:
            view_id = False
        res = {}
        res.update({'case_id':case.id})
        res.update({'name':"Invoice For "+case.name})        
        res.update({'bill_type':case.bill_type})
        subject = ''
        oppo = False
        first = False
        if case.work_type != 'non_litigation':
            if case.court_id:
                subject = case.court_id.name + (case.court_location_id and ', ' + case.court_location_id.name or '')
            if case.reg_number:
                subject += '\n'+'Case No. : '+case.reg_number
                
            for fp in case.first_parties:
                first = (first and first+', '+fp.name or '\n'+fp.name)
                
              
            if first:
                subject +=first
                oppo=False    
                for op in case.opp_parties:
                    oppo = (oppo and oppo+', '+op.name or '\n \tV/S \n'+op.name)
        if oppo:
            subject +=oppo
        res.update({'subject':subject})
        valslist = []
        valid = False
        
        flg_fixed_fixed_price_stage = True
        flg_fixed_other_exp_billable = True
        flg_assign_hourly_stage = True
        flg_assign_fixed_price_stage = True
        flg_assign_other_exp_billable = True
        flg_assign_court_proceed_billable = True
        other_expenses = False
       
        
        if context.has_key('flg_fixed_fixed_price_stage'):
            flg_fixed_fixed_price_stage = context['flg_fixed_fixed_price_stage']
        if context.has_key('flg_fixed_other_exp_billable'):
            flg_fixed_other_exp_billable = context['flg_fixed_other_exp_billable']
        if context.has_key('flg_assign_hourly_stage'):
            flg_assign_hourly_stage = context['flg_assign_hourly_stage']
        if context.has_key('flg_assign_fixed_price_stage'):
            flg_assign_fixed_price_stage = context['flg_assign_fixed_price_stage']
        if context.has_key('flg_assign_other_exp_billable'):
            flg_assign_other_exp_billable = context['flg_assign_other_exp_billable']
        if context.has_key('flg_assign_court_proceed_billable'):
            flg_assign_court_proceed_billable = context['flg_assign_court_proceed_billable']
            
        if case.bill_type == 'fixed_price' and flg_fixed_other_exp_billable:
            other_expenses = True
        elif case.bill_type == 'assignment_wise' and flg_assign_other_exp_billable:
            other_expenses = True
        # Billing Type is Fixed Price    
        if case.bill_type == 'fixed_price':
            if flg_fixed_fixed_price_stage:
                valslist = []
                
                for line in case.stage_lines:
                    fixed_price_exist_ids = self.pool.get('case.sheet.invoice').search(cr, uid,[('invoice_lines_fixed.ref_id','=',line.id), ('invoice_id','!=',False)])
                    if not line.invoiced and line.state == 'Completed' and not len(fixed_price_exist_ids):
                        valid = True
                        valslist.append((0, 0, {'name':line.name.name.name,'amount':line.amount,'ref_id':line.id, 'out_of_pocket_amount':line.out_of_pocket_amount, 'office_id':line.office_id.id}))
                        #added office field in above statement # Sanal Davis # 27/5/15
                res.update({'invoice_lines_fixed':valslist})
        else:
                valslist = []
                if flg_assign_hourly_stage:
                    for line in case.assignment_hourly_lines:
                        already_added_hours = 0.00
                        assign_hour_exist_ids = self.pool.get('case.sheet.invoice').search(cr, uid,[('invoice_lines_assignment_hourly.ref_id','=',line.id), ('invoice_id','!=',False)])
                        for assign_hour in self.pool.get('case.sheet.invoice').browse(cr, uid, assign_hour_exist_ids):
                            for lin in assign_hour.invoice_lines_assignment_hourly:                                
                                remain = lin.bill_hours
                                if not remain or remain<=0:
                                    remain = lin.amount/line.amount
                                    remain = remain or 0.00
                            already_added_hours += remain
                        if not line.invoiced and (line.remaining_hours - already_added_hours)>0:
                            valid = True
                            valslist.append((0, 0, {'name':line.description,'amount':(line.amount*line.remaining_hours), 'ref_id': line.id, 'bill_hours':line.remaining_hours,'office_id':line.office_id and line.office_id.id or False}))
                    res.update({'invoice_lines_assignment_hourly':valslist})
                if flg_assign_fixed_price_stage:
                    valslist = []
                    for line in case.assignment_fixed_lines:
                        assign_fixed_exist_ids = self.pool.get('case.sheet.invoice').search(cr, uid,[('invoice_lines_assignment_fixed.ref_id','=',line.id), ('invoice_id','!=',False)])                
                        if not line.invoiced and line.state == 'Completed' and not len(assign_fixed_exist_ids):
                            valslist.append((0, 0, {'name':line.name.name.name,'amount':line.amount,'ref_id':line.id, 'out_of_pocket_amount':line.out_of_pocket_amount,'office_id':line.office_id and line.office_id.id or False}))
                            valid = True
                            
                    res.update({'invoice_lines_assignment_fixed':valslist})
                
                # Court Proceedings
                if flg_assign_court_proceed_billable:
                    valslist = []
                    for line in case.court_proceedings:
                        court_exist_ids = self.pool.get('case.sheet.invoice').search(cr, uid,[('invoice_lines_court_proceedings_assignment.ref_id','=',line.id), ('invoice_id','!=',False)])       
                        if not line.invoiced and line.billable == 'bill' and not len(court_exist_ids):
                            valid = True
                            valslist.append((0, 0, {'effective':line.effective,'name':line.name,'amount':line.effective == 'effective' and case.effective_court_proceed_amount or case.non_effective_court_proceed_amount, 'date':line.proceed_date, 'ref_id': line.id, 'office_id':case.ho_branch_id.id}))
                    res.update({'invoice_lines_court_proceedings_assignment':valslist})
        #Other Expenses
        if other_expenses:
            valslist = []
            for line in case.other_expenses_lines:
                other_expense_exist_ids = self.pool.get('case.sheet.invoice').search(cr, uid,[('invoice_lines_other_expenses.ref_id','=',line.id), ('invoice_id','!=',False)])                    
                if not line.invoiced and line.billable == 'bill' and not len(other_expense_exist_ids):
                    valid = True
                    valslist.append((0, 0, {'name':line.name,'amount':line.amount,'ref_id':line.id, 'office_id':case.ho_branch_id.id}))
            res.update({'invoice_lines_other_expenses':valslist})
        
        if not valid and not context.has_key('consolidated_id'):
            raise osv.except_osv(_('Warning'),_('Nothing to Invoice'))
        if context.has_key('consolidated_id') and context['consolidated_id']:
            res.update({'consolidated_id':context['consolidated_id']})    
        invid = self.pool.get('case.sheet.invoice').create(cr, uid, res)
        return {
            'name':_("Invoice Case Sheet"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'case.sheet.invoice',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
            'res_id': invid,
            'valid': valid
            }

        
    def view_related_invoices(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])        
        sear = self.pool.get('case.sheet.invoice').search(cr, uid, [('case_id','=',obj.id),('invoice_id','!=',False)],context=context)
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'invoice_form')
        except ValueError, e:
            view_id = False
        lst = []
        for dt in self.pool.get('case.sheet.invoice').read(cr, uid, sear,['invoice_id']):
            lst.append(dt['invoice_id'][0])
        return {
                'name': _('Customer Invoice'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'domain': "[('type','=','out_invoice'),('id','in',("+str(lst)+"))]",
                'view_id': False,
                'context':{'form_view_ref':'account.invoice_form'},
        }
    # Starting // Sanal Davis // 4-6-15    
    def view_related_expenses(self, cr, uid, ids, context=None):
        '''
            View related expenses from case sheet 
        '''
        obj = self.browse(cr, uid, ids[0])        
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'view_expenses_form_inherit')
        except ValueError, e:
            view_id = False
        return {
                'name': _('Expense'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'hr.expense.expense',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'domain': "[('case_id','=',"+str(obj.id)+")]",
                'context':{'case_id':obj.id},
        }
    # Sanal Davis // 9-6-15    
    def view_related_petty_cash(self, cr, uid, ids, context=None):
        '''
            View related petty cash from case sheet 
        '''
        obj = self.browse(cr, uid, ids[0])
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'view_move_line_tree_legal_e_inherit')
        except ValueError, e:
            view_id = False
        return {
                'name': _('Petty Cash'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'account.move.line',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'domain': "[('case_id','=',"+str(obj.id)+")]",
                'context': {'search_default_case_id':[obj.id], 'default_case_id': obj.id},
        }
        
        # Ending
case_sheet()


class case_assignment_history(osv.osv):
    _name = 'case.assignment.history'
    _order = 'date'
    _description = 'Case Sheet Assignment History'
    _columns = {
        'date': fields.date('Date'),
        'name': fields.text('Description'),
        'case_id': fields.many2one('case.sheet','Case Sheet'),
            
    }
    
    _defaults = {
        'date':time.strftime('%Y-%m-%d'),
        }
    
case_assignment_history()


#Assignee Tasks
class case_tasks_line(osv.osv):
    _name = 'case.tasks.line'
    _order = 'slno,days'
    _description = 'Tasks Assignment for a Case Sheet'
    
    def default_get(self, cr, uid, fields_list, context=None):
        if not context:
            context = {}
        global line_count_slno
        line_count_slno +=1
        res = super(case_tasks_line, self).default_get(cr, uid, fields_list, context=context)
        return res        
    
    def onchange_cnt(self, cr, uid, ids, count,target_field, recep_date, context=None):
        return_date = (datetime.strptime(recep_date, '%Y-%m-%d') + timedelta(days=count)).strftime('%Y-%m-%d')
        return_date = self.pool.get('hr.holidays.public').get_next_working_day(cr, uid, return_date)
        val = {
            target_field: str(return_date)
        }
        return {'value': val}
        
    def update_days(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
            days = (datetime.strptime(obj.planned_completion_date, '%Y-%m-%d') - datetime.strptime(obj.start_date, '%Y-%m-%d')).days
            self.write(cr, uid, [obj.id], {'days':days})
        return True
        
    def _get_default_assign_to(self, cr, uid, context=None):
        ret = False
        if context.has_key('assignee_id') and context['assignee_id']:
            return context['assignee_id']
        return ret    
        
    def _set_color_state(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            if line.planned_completion_date < time.strftime('%Y-%m-%d'):
                res[line.id]='before'
            else:
                res[line.id]= 'after'    
        return res
        
    def _get_state_task(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for task in self.browse(cr, SUPERUSER_ID, ids):
            stage = task.task_id and task.task_id.stage_id.name or 'New'
            res[task.id] = stage
        return res
        
    _columns = {
        'case_id': fields.many2one('case.sheet','Tasks Assignment Reference'),
        'name': fields.many2one('task.master', 'Task Name', required=True),
        'start_date': fields.date('Start Date'),
        'planned_completion_date': fields.date('End Date'),
        'days': fields.integer('Days'),
        'slno':fields.integer('Sl no'),
        'assignee_id': fields.many2one('hr.employee','Assignee'),
        'phase_name':fields.many2one('phase.master','Phase Name'),
        'task_id':fields.many2one('project.task','Task ID'),
        'assign_to':fields.many2one('hr.employee','Assign To'),  
        'state':fields.function(_get_state_task,type='char',string="Status"),
        'color_state':fields.function(_set_color_state,string='Color State',type='char'),
        'old_id':fields.many2one('case.tasks.line','Old ID'),
        'office_id':fields.many2one('ho.branch','Office'), #add office field # Sanal Davis #27/5/15
    }
    _defaults = {
        'assign_to': lambda s, cr, uid, c:s._get_default_assign_to(cr, uid, c),
        'planned_completion_date':lambda s, cr, uid, c: (datetime.strptime(str(s.pool.get('hr.holidays.public').get_next_working_day(cr, uid, time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'),
        'start_date':lambda s, cr, uid, c: (datetime.strptime(str(s.pool.get('hr.holidays.public').get_next_working_day(cr, uid, time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'),
        'state':'New',
    }
    
    
    
    def _check_slno_unique(self, cr, uid, ids, context=None):
        for task_obj in self.browse(cr, uid, ids, context=context):
            task_ids = self.search(cr, uid, [('slno', '=', task_obj.slno), ('case_id', '=', task_obj.case_id.id),('id', '<>', task_obj.id)], context=context)
            if task_ids:
                return False
        return True
    
    _constraints = [
        (_check_slno_unique, "\nError!\n\n'Sl no' must be unique", ['case_id', 'slno']),
    ]
#     _sql_constraints = [
#         ('case_id_sl_no_uniq', 'unique(case_id, slno)', "\nError!\n\n'Sl no' must be unique"),
#         ]
    
    # Starting Sanal Davis  #27/5/15
    def onchange_office(self, cr, uid, ids, assign_to, context=None):
        '''
        This function writes the office field value
        '''
        employee_pool = self.pool.get('hr.employee')
        employee = employee_pool.browse(cr, uid, assign_to, context=context)
        if assign_to:
            office_id = employee.ho_branch_id.id or False   
        else:
            office_id = False
        return {'value': {'office_id': office_id}}
    # Ending
    
    def copy_data(self, cr, uid, ids, default=None, context=None):
        default = default or {}
        start_date = time.strftime('%Y-%m-%d')
        data_obj  = self.browse(cr, uid, ids, context=context)
        return_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=data_obj.days)).strftime('%Y-%m-%d')
        return_date = self.pool.get('hr.holidays.public').get_next_working_day(cr, uid, return_date)
        default.update({
            'state':'New',
            'task_id':False,
            'start_date': start_date,
            'planned_completion_date': return_date,
            })
        return super(case_tasks_line, self).copy_data(cr, uid, ids, default, context)
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        for task_line in self.browse(cr, uid, ids, context=context):
            res.append((task_line.id,task_line.name.name))
        return res
            
    
    def check_for_holiday(self, cr, uid, ids, plandate, count, targetfield, recep_date, context=None):
        vals = {}
        vals['planned_completion_date'] = plandate
        year = time.strftime('%Y')
        holiids = self.pool.get('hr.holidays.public').search(cr, uid, [('year','=',year)])
        public_holidays = []
        for holi in self.pool.get('hr.holidays.public').browse(cr, uid, holiids):
            for line in holi.line_ids:
                public_holidays.append(line.date)
        if len(plandate)>10:
            plandate = plandate[:10]
        if datetime.strptime(plandate, '%Y-%m-%d').weekday() == 6 or (len(public_holidays)>0 and plandate in public_holidays):
            vals['planned_completion_date'] = time.strftime('%Y-%m-%d')
            warning = {
                       'title': _('Error!'),
                       'message' : _('Selected Day is a Holiday, Please select another Day!')
                    }
            ret = self.onchange_cnt(cr, uid, ids, count,targetfield, recep_date, context=context)
            return {'value': ret['value'], 'warning': warning}  
        return {'value':vals}
    
    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.task_id:
                self.pool.get('project.task').unlink(cr, uid, [obj.task_id.id], context=context)    
        retvals = super(case_tasks_line, self).unlink(cr, uid, ids, context=context)
        global line_count_slno
        return retvals
        
    def create(self, cr, uid, vals, context=None): 
        if context is None:
            context = {}
        retvals = super(case_tasks_line, self).create(cr, uid, vals, context=context)         
        for line in self.browse(cr, SUPERUSER_ID, [retvals], context=context):
            if line.case_id and line.case_id.state != 'new':
                self.pool.get('case.sheet').confirm_casesheet(cr, uid, [line.case_id.id])
        vals['task_new_id'] = retvals
        vals = self.pool.get('assignment.wise').update_related_task_for_cost_Details(cr, uid, vals, context)           
        vals = self.pool.get('fixed.price.stages').update_related_task_for_cost_Details(cr, uid, vals, context)
        
        return retvals
        
    def write(self, cr, uid, ids, vals, context=None):
        retvals = super(case_tasks_line, self).write(cr, uid, ids, vals, context=context)
        user_pool = self.pool.get('res.users')
        csm = user_pool.has_group(cr, uid, 'legal_e.group_legal_e_client_service_manager')
        csm_super_id = uid
        if csm:
            csm_super_id = SUPERUSER_ID
        for line in self.browse(cr, uid, ids, context=context):
            assigned = self.pool.get('hr.employee').browse(cr, uid, line.assign_to.id)
            if line.case_id and line.case_id.project_id:
                project = self.pool.get('project.project').browse(cr, uid, line.case_id.project_id.id)
                if not assigned.user_id.id in project.members:
                    self.pool.get('project.project').write(cr, csm_super_id, [project.id],{'members':[(4, assigned.user_id.id)]})
                    self.pool.get('case.sheet').write(cr, uid, [line.case_id.id],{'members':[(4, assigned.user_id.id)]})
                res={}
                if vals.has_key('planned_completion_date'):
                    res['date_deadline'] = vals['planned_completion_date']
                    if vals['planned_completion_date'] >= time.strftime('%Y-%m-%d'):
                        task_type_ids = self.pool.get('project.task.type').search(cr, uid, [('state','=','draft')])
                        if task_type_ids:
                            res['stage_id'] = task_type_ids[0]
                        res['state'] = 'draft'
                    else:
                        task_type_ids = self.pool.get('project.task.type').search(cr, uid, [('state','=','pending')])
                        if task_type_ids:
                            res['stage_id'] = task_type_ids[0]
                        res['state'] = 'pending'
                    res['planned_hours'] = line.days*8
                    res['date_end'] = vals['planned_completion_date']
                if vals.has_key('assign_to'):
                    res['assignee_id'] = vals['assign_to']
                if line.task_id and line.task_id.state != 'done':
                    self.pool.get('project.task').write(cr, uid, [line.task_id.id],res)
                    
                if vals.get('state', False) == 'Completed':
                    tasks_ids = self.search(cr, uid, [('case_id', '=', line.case_id.id), ('id', '<>', line.id)],context=context)
                    test = {}
                    for task_obj in self.browse(cr, uid, tasks_ids, context=context):
                        if task_obj.state in ('Pending', 'New', 'In Progress'):
                            test.update({int(task_obj.slno): task_obj})
                    key = test.keys()
                    key.sort()
                    
                    if key:
                        task_type_ids = self.pool.get('project.task.type').search(cr, uid, [('state','=','open')],order='sequence')
                        if task_type_ids and test[key[0]].task_id.state not in ('pending', 'done', 'cancelled'):
                            self.pool.get('project.task').write(cr, uid, [test[key[0]].task_id.id], {'stage_id': task_type_ids[0], 'state': 'open'})
    #                         res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'email_template_assignee_task')
    #                         res_id = res and res[1] or False
    #                         if test[key[0]].task_id.assignee_id and test[key[0]].task_id.assignee_id.work_email:
    #                             self.pool.get('email.template').send_mail(cr, uid, res_id, test[key[0]].task_id.id, force_send=True, context=context)
                
            
        return retvals
          

case_tasks_line()

#Other Associates
class other_associate(osv.osv):
    _name='other.associate'
    _description = 'Other Associate'
    _columns = {
        'case_id':fields.many2one('case.sheet','File Number'),
        'name':fields.many2one('res.partner','Associate'),
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        for line in self.browse(cr, uid, ids, context=context):
            res.append((line.id,line.name.name))
        return res
    
other_associate()

#Associate Tasks
class associate_tasks_line(osv.osv):
    _name = 'associate.tasks.line'
    _order = 'slno,days'
    _description = 'Assciate Tasks for a Case Sheet'
    
    def default_get(self, cr, uid, fields_list, context=None):
        if not context:
            context = {}
        global line_count_slno
        line_count_slno +=1
        res = super(associate_tasks_line, self).default_get(cr, uid, fields_list, context=context)
        return res        
    
    def onchange_cnt(self, cr, uid, ids, count,target_field, recep_date, context=None):
        return_date = (datetime.strptime(recep_date, '%Y-%m-%d') + timedelta(days=count)).strftime('%Y-%m-%d')
        return_date = self.pool.get('hr.holidays.public').get_next_working_day(cr, uid, return_date)
        val = {
            target_field: str(return_date)
        }
        return {'value': val}
        
    def _get_default_assign_to(self, cr, uid, context=None):
        ret = False
        if context.has_key('associate_id') and context['associate_id'] and len(context['associate_id'])>0:
            if context['associate_id'][0][0] == 0:
                return context['associate_id'][0][2]['name']
            elif context['associate_id'][0][0] == 4:
                obj = self.pool.get('other.associate').browse(cr, uid, context['associate_id'][0][1])
                return obj.name.id
            
        return ret
        
    def _set_color_state(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            if line.planned_completion_date < time.strftime('%Y-%m-%d'):
                res[line.id]='before'
            else:
                res[line.id]= 'after'    
        return res
        
    def _get_state_task(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for task in self.browse(cr, uid, ids):
            stage = task.task_id and task.task_id.stage_id.name or 'New'
            res[task.id] = stage
        return res
        
    _columns = {
        'case_id': fields.many2one('case.sheet','Associate Tasks Assignment Reference'),
        'name': fields.many2one('task.master', 'Task Name', required=True),
        'start_date':fields.date('Start Date'),
        'planned_completion_date': fields.date('Task Date'),
        'days': fields.integer('Days'),
        'slno':fields.integer('Sl no'),
        'associate_id': fields.many2one('hr.employee','Associate'),
        'phase_name':fields.many2one('phase.master','Phase Name'),
        'assign_to_in_associate':fields.many2one('res.partner','Assign To'),
        'task_id':fields.many2one('project.task','Task ID'),
        'state':fields.function(_get_state_task,type='char',string="Status"),
        'color_state':fields.function(_set_color_state,string='Color State',type='char'),
        'old_id':fields.many2one('associate.tasks.line','Old ID'),
    }
    _defaults = {
        'assign_to_in_associate': lambda s, cr, uid, c:s._get_default_assign_to(cr, uid, c),
        'planned_completion_date':lambda s, cr, uid, c: (datetime.strptime(str(s.pool.get('hr.holidays.public').get_next_working_day(cr, uid, time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'),
        'start_date':lambda s, cr, uid, c: (datetime.strptime(str(s.pool.get('hr.holidays.public').get_next_working_day(cr, uid, time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'),
        'state':'New',
    }
    
    
    def copy_data(self, cr, uid, ids, default=None, context=None):
        default = default or {}
        start_date = time.strftime('%Y-%m-%d')
        data_obj  = self.browse(cr, uid, ids, context=context)
        return_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=data_obj.days)).strftime('%Y-%m-%d')
        return_date = self.pool.get('hr.holidays.public').get_next_working_day(cr, uid, return_date)
        default.update({
            'state':'New',
            'task_id':False,
            'start_date': start_date,
            'planned_completion_date': return_date,
            })
        return super(associate_tasks_line, self).copy_data(cr, uid, ids, default, context)
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        for task_line in self.browse(cr, uid, ids, context=context):
            res.append((task_line.id,task_line.name.name))
        return res
    
    def check_for_holiday(self, cr, uid, ids, plandate, count, targetfield, recep_date, context=None):
        vals = {}
        vals['planned_completion_date'] = plandate
        year = time.strftime('%Y')
        holiids = self.pool.get('hr.holidays.public').search(cr, uid, [('year','=',year)])
        public_holidays = []
        for holi in self.pool.get('hr.holidays.public').browse(cr, uid, holiids):
            for line in holi.line_ids:
                public_holidays.append(line.date)
        if len(plandate)>10:
            plandate = plandate[:10]        
        if datetime.strptime(plandate, '%Y-%m-%d').weekday() == 6 or (len(public_holidays)>0 and plandate in public_holidays):
            vals['planned_completion_date'] = time.strftime('%Y-%m-%d')
            warning = {
                       'title': _('Error!'),
                       'message' : _('Selected Day is a Holiday, Please select another Day!')
                    }
            ret = self.onchange_cnt(cr, uid, ids, count,targetfield, recep_date, context=context)
            return {'value': ret['value'], 'warning': warning}  
        return {'value':vals}
    
    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.task_id:
                self.pool.get('project.task').unlink(cr, uid, [obj.task_id.id], context=context)
        retvals = super(associate_tasks_line, self).unlink(cr, uid, ids, context=context)
        global line_count_slno
        return retvals 
            
    def create(self, cr, uid, vals, context=None): 
        if context is None:
            context = {}
        retvals = super(associate_tasks_line, self).create(cr, uid, vals, context=context)    
        casesheet = self.pool.get('case.sheet').browse(cr, uid, vals['case_id'], context=context)
        if casesheet.project_id:
            for line in casesheet.associate_tasks_lines:
                phase_id=False
                if line.phase_name:
                    phase_ids = self.pool.get('project.phase').search(cr, uid, [('name','=',line.phase_name.name),('project_id','=',casesheet.project_id.id)])
                    if len(phase_ids)<=0:                    
                        phase_id=self.pool.get('project.phase').create(cr, uid, {'name':line.phase_name.name,'project_id':casesheet.project_id.id, 'product_uom':6,'duration':(line.days or 0)})
                    else:
                        phase_id = phase_ids[0]
                        phase = self.pool.get('project.phase').browse(cr, uid, phase_id)
                        duration = (line.days or 0) + (phase.duration or 0)
                        self.pool.get('project.phase').write(cr, uid, [phase_id],{'duration':duration})
                if not line.task_id:    
                    task_id = self.pool.get('project.task').create(cr, uid, {'project_id':casesheet.project_id.id,'phase_id':phase_id,'name':line.name.id,'task_for':'associate','other_assignee_id':line.assign_to_in_associate.id,'date_deadline':line.planned_completion_date, 'sequence':line.slno,'date_start':line.start_date,'date_end':line.planned_completion_date,'planned_hours':line.days*8})
                    self.pool.get('associate.tasks.line').write(cr, uid, [line.id], {'task_id':task_id})
        
        return retvals
        
    def write(self, cr, uid, ids, vals, context=None):
        retvals = super(associate_tasks_line, self).write(cr, uid, ids, vals, context=context)
        line = self.browse(cr, uid, ids[0])
        res={}
        if vals.has_key('planned_completion_date'):
            res['date_deadline'] = vals['planned_completion_date']
            if vals['planned_completion_date'] >= time.strftime('%Y-%m-%d'):
                task_type_ids = self.pool.get('project.task.type').search(cr, uid, [('state','=','draft')])
                if task_type_ids:
                    res['stage_id'] = task_type_ids[0]
                res['state'] = 'draft'
            else:
                task_type_ids = self.pool.get('project.task.type').search(cr, uid, [('state','=','pending')])
                if task_type_ids:
                    res['stage_id'] = task_type_ids[0]
                res['state'] = 'pending'
            
            res['planned_hours'] = line.days*8
            res['date_end'] = vals['planned_completion_date']
        if vals.has_key('assign_to_in_associate'):
            res['other_assignee_id'] = vals['assign_to_in_associate']
        if line.task_id:
            self.pool.get('project.task').write(cr, uid, [line.task_id.id],res)
            
        
        return retvals

associate_tasks_line()


#Client Tasks
class client_tasks_line(osv.osv):
    _name = 'client.tasks.line'
    _order = 'slno,days'
    _description = 'Tasks Assignment for a Case Sheet'
    
    def default_get(self, cr, uid, fields_list, context=None):
        if not context:
            context = {}
        global line_count_slno
        line_count_slno +=1
        res = super(client_tasks_line, self).default_get(cr, uid, fields_list, context=context)
        return res        
    
    def onchange_cnt(self, cr, uid, ids, count,target_field, recep_date, context=None):
        return_date = (datetime.strptime(recep_date, '%Y-%m-%d') + timedelta(days=count)).strftime('%Y-%m-%d')
        return_date = self.pool.get('hr.holidays.public').get_next_working_day(cr, uid, return_date)
        val = {
            target_field: str(return_date)
        }
        return {'value': val}
        
    def _get_default_assign_to(self, cr, uid, context=None):
        ret = False
        if context.has_key('client_id') and context['client_id']:
            return context['client_id']
        return ret
        
    def _set_color_state(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for line in self.browse(cr, uid, ids):
            if line.planned_completion_date < time.strftime('%Y-%m-%d'):
                res[line.id]='before'
            else:
                res[line.id]= 'after'    
        return res
        
    def _get_state_task(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for task in self.browse(cr, uid, ids):
            stage = task.task_id and task.task_id.stage_id.name or 'New'
            res[task.id] = stage
        return res
        
    _columns = {
        'case_id': fields.many2one('case.sheet','Tasks Assignment Reference'),
        'name': fields.many2one('task.master', 'Task Name', required=True),
        'start_date':fields.date('Start Date'),
        'planned_completion_date': fields.date('Task Date'),
        'days': fields.integer('Days'),
        'slno':fields.integer('Sl no'),
        'assignee_id': fields.many2one('hr.employee','Assignee'),
        'phase_name':fields.many2one('phase.master','Phase Name'),
        'assign_to_in_client':fields.many2one('res.partner','Assign To'),
        'task_id':fields.many2one('project.task','Task ID'),
        'state':fields.function(_get_state_task,type='char',string="Status"),
        'color_state':fields.function(_set_color_state,string='Color State',type='char'),
        'old_id':fields.many2one('client.tasks.line','Old ID'),
    }
    _defaults = {
        'assign_to_in_client': lambda s, cr, uid, c:s._get_default_assign_to(cr, uid, c),
        'planned_completion_date':lambda s, cr, uid, c: (datetime.strptime(str(s.pool.get('hr.holidays.public').get_next_working_day(cr, uid, time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'),
        'start_date':lambda s, cr, uid, c: (datetime.strptime(str(s.pool.get('hr.holidays.public').get_next_working_day(cr, uid, time.strftime('%Y-%m-%d')))[:10], '%Y-%m-%d')).strftime('%Y-%m-%d'),
        'state':'New',
        
    }
    
    
    def copy_data(self, cr, uid, ids, default=None, context=None):
        default = default or {}
        start_date = time.strftime('%Y-%m-%d')
        data_obj  = self.browse(cr, uid, ids, context=context)
        return_date = (datetime.strptime(start_date, '%Y-%m-%d') + timedelta(days=data_obj.days)).strftime('%Y-%m-%d')
        return_date = self.pool.get('hr.holidays.public').get_next_working_day(cr, uid, return_date)
        default.update({
            'state':'New',
            'task_id':False,
            'start_date': start_date,
            'planned_completion_date': return_date,
            })
        return super(client_tasks_line, self).copy_data(cr, uid, ids, default, context)
    
    def check_for_holiday(self, cr, uid, ids, plandate, count, targetfield, recep_date, context=None):
        vals = {}
        vals['planned_completion_date'] = plandate
        year = time.strftime('%Y')
        holiids = self.pool.get('hr.holidays.public').search(cr, uid, [('year','=',year)])
        public_holidays = []
        for holi in self.pool.get('hr.holidays.public').browse(cr, uid, holiids):
            for line in holi.line_ids:
                public_holidays.append(line.date)
        if len(plandate)>10:
            plandate = plandate[:10]
        if datetime.strptime(plandate, '%Y-%m-%d').weekday() == 6 or (len(public_holidays)>0 and plandate in public_holidays):
            vals['planned_completion_date'] = time.strftime('%Y-%m-%d')
            warning = {
                       'title': _('Error!'),
                       'message' : _('Selected Day is a Holiday, Please select another Day!')
                    }
            ret = self.onchange_cnt(cr, uid, ids, count,targetfield, recep_date, context=context)
            return {'value': ret['value'], 'warning': warning}  
        return {'value':vals}
    
    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.task_id:
                self.pool.get('project.task').unlink(cr, uid, [obj.task_id.id], context=context)
        retvals = super(client_tasks_line, self).unlink(cr, uid, ids, context=context)
        global line_count_slno
        return retvals         
            
    def create(self, cr, uid, vals, context=None): 
        if context is None:
            context = {}
        retvals = super(client_tasks_line, self).create(cr, uid, vals, context=context)    
        casesheet = self.pool.get('case.sheet').browse(cr, uid, vals['case_id'], context=context)
        if casesheet.project_id:
            for line in casesheet.client_tasks_lines:
                phase_id=False
                if line.phase_name:
                    phase_ids = self.pool.get('project.phase').search(cr, uid, [('name','=',line.phase_name.name),('project_id','=',casesheet.project_id.id)])
                    if len(phase_ids)<=0:                    
                        phase_id=self.pool.get('project.phase').create(cr, uid, {'name':line.phase_name.name,'project_id':casesheet.project_id.id, 'product_uom':6,'duration':(line.days or 0)})
                    else:
                        phase_id = phase_ids[0]
                        phase = self.pool.get('project.phase').browse(cr, uid, phase_id)
                        duration = (line.days or 0) + (phase.duration or 0)
                        self.pool.get('project.phase').write(cr, uid, [phase_id],{'duration':duration})
                if not line.task_id:    
                    task_id = self.pool.get('project.task').create(cr, uid, {'project_id':casesheet.project_id.id,'phase_id':phase_id,'name':line.name.id,'task_for':'customer','date_deadline':line.planned_completion_date,'client_id':line.assign_to_in_client.id, 'sequence':line.slno,'date_start':line.start_date,'date_end':line.planned_completion_date,'planned_hours':line.days*8})
                    self.pool.get('client.tasks.line').write(cr, uid, [line.id], {'task_id':task_id})
        
        return retvals        
        
    def write(self, cr, uid, ids, vals, context=None):
        retvals = super(client_tasks_line, self).write(cr, uid, ids, vals, context=context)
        line = self.browse(cr, uid, ids[0])
        res={}
        if vals.has_key('planned_completion_date'):
            res['date_deadline'] = vals['planned_completion_date']
            
            if vals['planned_completion_date'] >= time.strftime('%Y-%m-%d'):
                task_type_ids = self.pool.get('project.task.type').search(cr, uid, [('state','=','draft')])
                if task_type_ids:
                    res['stage_id'] = task_type_ids[0]
                res['state'] = 'draft'
            else:
                task_type_ids = self.pool.get('project.task.type').search(cr, uid, [('state','=','pending')])
                if task_type_ids:
                    res['stage_id'] = task_type_ids[0]
                res['state'] = 'pending'
            
            
            res['planned_hours'] = line.days*8
            res['date_end'] = vals['planned_completion_date']
        if vals.has_key('assign_to_in_client'):
            res['client_id'] = vals['assign_to_in_client']
        if line.task_id:
            self.pool.get('project.task').write(cr, uid, [line.task_id.id],res)
            
       
        return retvals

client_tasks_line()


class associate_payment(osv.osv):
    _name = 'associate.payment'
    _columns = {
    	'case_id':fields.many2one('case.sheet','File Number'),
        'name':fields.many2one('associate.tasks.line','Task Related', required=True),
        'date': fields.date('Date'),
        'description':fields.char('Description',size=1024),
        'amount':fields.float('Amount', required=True),
        'invoiced':fields.boolean('Invoiced', readonly=True),
        'state':fields.related('name','state',type='selection',selection=[('New','New'),('In Progress','In Progress'),('Hold','Hold'),('Pending','Pending'),('Completed','Completed'),('Invoiced','Invoiced')],string="Status"),
        'invoice_id':fields.many2one('account.invoice', 'Invoice ID'),
        'associate_id':fields.many2one('other.associate','Associate'),
        'po_id':fields.many2one('purchase.order','Purchase Order'),
        'old_id':fields.many2one('associate.payment','Old ID'),
    }
    
    def copy_data(self, cr, uid, ids, default=None, context=None):
        default = default or {}
        default.update({
            'invoiced':False
        })
        return super(associate_payment, self).copy_data(cr, uid, ids, default, context)
        
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        for line in self.browse(cr, uid, ids, context=context):
            res.append((line.id,line.name.name))
        return res

    
    def view_invoice_task(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'invoice_supplier_form')
        except ValueError, e:
            view_id = False
        return {
            'name': _('Supplier Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': obj.invoice_id.id,
        }
                
            
                
    def invoice_associate_task(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.associate_id:
                partner_id = line.associate_id.name
                acc_id = partner_id.property_account_payable.id
                name=line.name.name.name
                if line.name.name.product_id:
                    name= line.name.name.name
                vals = {
                    'partner_id': partner_id.id,
                    'account_id':acc_id,
                    'type':'in_invoice',
                    'origin': line.case_id.name,
                    'case_id': line.case_id.id,
#                     'date_invoice': 
                    'invoice_line':[(0, 0, {
                        'name': line.description and line.description or 'Payment for the Task ' + name, 
                        'quantity':1.00,
                        'price_unit':line.amount,
                        'type':'in_invoice',
                        'account_analytic_id': line.case_id.project_id.analytic_account_id.id,
                        })]
                    }
                inv_id = self.pool.get('account.invoice').create(cr, uid, vals, context=context)
                self.write(cr, uid, [line.id], {'invoiced':True,'invoice_id':inv_id})        
        return True   
    
associate_payment()    

class task_template_line(osv.osv):
    _name = 'task.template.line'
    _columns = {
    	'template_id':fields.many2one('task.template','Template Reference'),
        'name':fields.many2one('task.master', 'Task', required=True),
        'days': fields.integer('Days'),
        'slno':fields.integer('Sl no'),
        'phase_name':fields.many2one('phase.master','Phase Name'),
        'type':fields.selection([('assignee','Assignee'),('associate','Associate'),('client','Client')],'Task For'),
    }

class task_template(osv.osv):
    _name = 'task.template'
    _columns = {
        'name':fields.selection([('civillitigation', 'Civil Litigation'),('criminallitigation', 'Criminal Litigation'), ('non_litigation', 'Non Litigation'), ('arbitration', 'Arbitration'),('execution', 'Execution'),('mediation', 'Mediation')], 'Type of Work', required=True),
        'casetype_id': fields.many2one('case.master','Case Type', required=True),
        'tasks_lines':fields.one2many('task.template.line','template_id','Task Template Lines'),
    }
    
    
#     def create(self, cr, uid, vals, context=None):
#         retids = self.search(cr, uid, [('name','=',vals['name']),('casetype_id','=',vals['casetype_id'])])        
#         if len(retids)>0:
#             lineids = self.pool.get('task.template.line').search(cr, uid, [('name','=',vals['tasks_lines'][0][2]['name']),('template_id','=',retids[0])]) 
#             if len(lineids)>0:
#                 self.pool.get('task.template.line').write(cr, uid, [lineids[0]], {'days':vals['tasks_lines'][0][2]['days'],'slno':vals['tasks_lines'][0][2]['slno'],'phase_name':vals['tasks_lines'][0][2]['phase_name']})
#             else:
#                 self.pool.get('task.template.line').create(cr, uid, {'template_id':retids[0],'name':vals['tasks_lines'][0][2]['name'],'phase_name':vals['tasks_lines'][0][2]['phase_name'],'slno':vals['tasks_lines'][0][2]['slno'],'days':vals['tasks_lines'][0][2]['days']})
#             return retids[0]
#         else:
#             retvals = super(task_template, self).create(cr, uid, vals, context=context)
#             return retvals
    
task_template()

class case_task_line(osv.osv):
    _name = 'case.task.line'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Task Assignment for a Case Sheet'
    
    def _get_task_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            #we may not know the level of the parent at the time of computation, so we
            # can't simply do res[account.id] = account.parent_id.level + 1
            amount = 0.0
            if line.amount:
                amount = line.amount * line.hours_spent
            res[line.id] = amount
        return res
        
    _columns = {
        'case_id': fields.many2one('case.sheet', 'Task Assignment Reference'),
        'name': fields.many2one('task.master', 'Task Name', required=True),
        'start_date': fields.date('Start Date',required=True),
        'plan_completion_date': fields.date('Planned Completion Date'),        
        'state': fields.selection([('new','New'),('inprogress','InProgress'),('completedduebill','Completed & Due for Billing'),('billed','Bill Generated'),('paid','Paid'),('done','Closed')],'Status', required=True),
        'assignee_id': fields.many2one('hr.employee', 'Assignee', required=True),
        'hours_spent': fields.float('Spent Hours',readonly=True),
        'activity_lines': fields.one2many('task.activity.line', 'task_id', 'Activity Assignment Lines'),
        'amount':fields.function(_get_task_amount, string='Amount', method=True, type='float'),
        'meeting_id':fields.many2one('crm.meeting','Meeting'),
        }
    _defaults = {
    	'state':'new',
    }   
   
    def default_get(self, cr, uid, fields_list, context=None):
        if not context:
            context = {}
        res = super(case_task_line, self).default_get(cr, uid, fields_list, context=context) 
        if context.has_key('assignee_id'):
            res.update({'assignee_id':context['assignee_id']})
        return res
    
    
    def create(self, cr, uid, vals, context=None):
        retvals = super(case_task_line, self).create(cr, uid, vals, context=context)
        line = self.browse(cr, uid, retvals)
        #To Create a Meeting in CRM Meetings
        meeting_obj = self.pool.get('crm.meeting')
        start_dt = datetime.strptime(line.start_date, '%Y-%m-%d')
        end_dt = (datetime.strptime(line.start_date, '%Y-%m-%d') + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')        
        duration = 1
        if line.plan_completion_date:
            end_dt = datetime.strptime(line.plan_completion_date, '%Y-%m-%d')
            duration = (end_dt - start_dt).days * 24
        meeting_vals = {
                    'name': line.name.name,
                    'user_id': (line.assignee_id.user_id.id or False),
                    'date': line.start_date,
                    'date_deadline': end_dt,
                    'duration':duration,
                    'state': 'open',            # to block that meeting date in the calendar
                }
        meeting_obj.create(cr, uid, meeting_vals)
        if line.assignee_id.user_id and line.assignee_id.user_id.partner_id:
            post_values =  {
                'partner_ids': [line.assignee_id.user_id.partner_id.id],
                'subject': '%s Task Assigned for you for the Case %s' % (line.name.name,line.case_id.name),                
                'body': '"%s" Task Assigned for you for the Case "%s" and the Start Date is %s.' % (line.name.name, line.case_id.name, line.start_date),
                }
            subtype = 'mail.mt_comment'
            self.message_post(cr, uid, [line.id], type='comment', subtype=subtype, context=context, **post_values)
        
        self.pool.get('tm.line').create(cr, uid, {'case_id':vals['case_id'],'task_id':retvals,'assignee_id':vals['assignee_id'],'hours_spent':(vals.has_key('hours_spent') and vals['hours_spent'] or False),'name':line.name.id})
        
        return retvals

    def write(self, cr, uid, ids, vals, context=None):
        retvals = super(case_task_line, self).write(cr, uid, ids, vals, context=context)
        line = self.browse(cr, uid, ids)[0]
        tmlines = self.pool.get('tm.line').search(cr, uid, [('task_id','=',ids)])
        for tmline in self.pool.get('tm.line').browse(cr, uid, tmlines):
            self.pool.get('tm.line').write(cr, uid, [tmline.id], {'hours_spent':line.hours_spent, 'state':line.state})
        return retvals
        
case_task_line()

class tm_line_invoice(osv.osv):
    _name = 'tm.line.invoice'
    
    _columns = {
        'tm_line_id': fields.many2one('tm.line', 'Task Assignment Reference'),
        'name':fields.many2one('account.invoice','Invoice ID', select=True),
        'hours':fields.float('Billed Hours'),
        }
        
tm_line_invoice()

class tm_line(osv.osv):
    _name = 'tm.line'
    _description = 'Time and Material Amount for a Task'
    
    def _get_task_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            amount = 0.0
            if line.case_id.tm_per_hour:
                amount = line.case_id.tm_per_hour * line.hours_spent
                res[line.id] = amount
        return res
        
    def _get_hours_spent(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            work_ids = self.pool.get('project.task.work').search(cr,uid,[('task_id','=',line.name.task_id.id)])
            hours = 0.0
            for wline in self.pool.get('project.task.work').browse(cr, uid, work_ids):
                hours += wline.hours
            res[line.id] = hours
        return res
        
    def _get_remaining_hours(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        hours = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            hours = (line.hours_spent or 0.0) - (line.billed_hours or 0.0)
            res[line.id] = hours
        return res        
        
    def _get_invoiced_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
             
        for line in self.browse(cr, uid, ids, context=context): 
            total = 0.0  
            for invid in line.invoice_ids:
                inv = self.pool.get('account.invoice').browse(cr,uid,invid.name.id)
                total += inv.amount_total
            res[line.id] = total    
        return res
        
    def _get_invoiced_balance(self, cr, uid, ids, field_name, arg, context=None):
        res = {}          
        
        for line in self.browse(cr, uid, ids, context=context):  
            residual = 0.0          
            for invid in line.invoice_ids:
                inv = self.pool.get('account.invoice').browse(cr,uid,invid.name.id)
                residual += inv.residual 
            res[line.id] = residual
        return res
        
    def _get_invoiced_state(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            state = False
            if line.invoice_id:
                states = {'draft':'Draft','proforma':'Pro-forma','proforma2':'Pro-forma','open':'Open','paid':'Paid','cancel':'Cancelled'}
                inv = self.pool.get('account.invoice').browse(cr,uid,line.invoice_id.id)
                state = states[inv.state]
            res[line.id] = state
        return res
        
    def view_invoice_task(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])        
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'invoice_form')
        except ValueError, e:
            view_id = False
        if len(obj.invoice_ids)==1:
            return {
                'name': _('Customer Invoice'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': obj.invoice_ids[0].name.id,
            }
        else:
            lst = []
            for dt in obj.invoice_ids:
                lst.append(dt.name.id)
            return {
                'name': _('Customer Invoice'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'domain': "[('id','in',("+str(lst)+"))]",
                'view_id': False,
                'context':{},
            }            
        
    def view_case_sheet(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'case_sheet_form')
        except ValueError, e:
            view_id = False
        return {
            'name': _('Case Sheet'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'case.sheet',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': obj.case_id.id,
        }
        
    _columns = {
        'case_id': fields.many2one('case.sheet', 'Case Sheet No.'),
        'name':fields.many2one('case.tasks.line','Task Related', required=True,readonly=False,),
        'hours_spent': fields.function(_get_hours_spent,string='Total Hours', method=True, type='float'),
        'hours_planned': fields.float('Initially Planned Hour(s)',readonly=True),
        'amount':fields.function(_get_task_amount, string='Amount', method=True, type='float'),
        'out_of_pocket_amount': fields.float('Out of Pocket Expense'),
        'state': fields.selection([('New','New'),('In Progress','In Progress'),('Hold','Hold'),('Pending','Pending'),('Completed','Completed'),('Invoiced','Invoiced')],'Status', readonly=True),
        'invoiced':fields.boolean('Invoiced'),
        'invoice_ids':fields.one2many('tm.line.invoice', 'tm_line_id', 'Invoice IDs'),
        'inv_total_amt':fields.function(_get_invoiced_total,string='Total INV Amt',type='float',readonly=True),
        'inv_balance_amt':fields.function(_get_invoiced_balance,string='Balance INV Amt',type='float',readonly=True),
        'billed_hours': fields.float('Billed Hours'),
        'remaining_hours': fields.function(_get_remaining_hours,string='Hours to Bill', method=True, type='float'),
        }
    _defaults = {
    	'state':'New',    	
    }        
        
    def invoice_task(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            partner_id = line.case_id.client_id.id
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            acc_id = p.property_account_receivable.id
            context.update({'type':'out_invoice'})
            pettyids = self.pool.get('account.account').search(cr, uid, [('name','=','PETTYCASH')])
            pettycash_acc_id = False
            if pettyids and len(pettyids) >0:
                pettycash_acc_id = pettyids[0] 
            product_id=False
            prod_acc_id = False
            diff = line.hours_spent - (line.billed_hours or 0.0)
            diff_hours = (line.billed_hours or 0.0) + diff
            if line.name.name.product_id:
                product_id = line.name.name.product_id.id
                if line.name.name.product_id.property_account_income:
                    prod_acc_id = line.name.name.product_id.property_account_income.id
            inv_id = self.pool.get('account.invoice').create(cr, uid, {'partner_id':partner_id,'account_id':acc_id,'invoice_line':[(0, 0, {'product_id':product_id,'name': 'Professional Charges', 'quantity':diff,'price_unit':line.case_id.tm_per_hour,'type':'out_invoice','account_id':prod_acc_id}),(0, 0, {'product_id':False,'name': 'Out of Pocket Expenses', 'quantity':1,'price_unit':line.out_of_pocket_amount,'type':'out_invoice','account_id':pettycash_acc_id})]},context)
            self.write(cr, uid, [line.id], {'invoiced':True,'billed_hours':diff_hours,'invoice_ids':[(0, 0, {'tm_line_id':line.id,'name': inv_id,'hours':diff})]})
        return True        
        
tm_line()


class assignment_wise_invoice(osv.osv):
    _name = 'assignment.wise.invoice'
    
    _columns = {
        'assignment_wise_id': fields.many2one('assignment.wise', 'Assignment Wise ID'),
        'name':fields.many2one('account.invoice','Invoice ID', select=True),
        'hours':fields.float('Billed Hours'),
        }
        
assignment_wise_invoice()

class assignment_wise(osv.osv):
    _name = 'assignment.wise'
    _description = 'Time and Material Amount for a Task'
        
    def _get_task_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            amount = 0.0
            if line.case_hourly_id.tm_per_hour:
                amount = line.case_hourly_id.tm_per_hour * line.hours_spent
                res[line.id] = amount
        return res
        
    def _get_hours_spent(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            work_ids = self.pool.get('project.task.work').search(cr,uid,[('task_id','=',line.name.task_id.id)])
            hours = 0.0
            for wline in self.pool.get('project.task.work').browse(cr, uid, work_ids):
                hours += wline.hours
            res[line.id] = hours
        return res
        
    def _get_remaining_hours(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        hours = 0.0
        for line in self.browse(cr, uid, ids, context=context):
            hours = (line.hours_spent or 0.0) - (line.billed_hours or 0.0)
            res[line.id] = hours
        return res        
        
    def _get_invoiced_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
             
        for line in self.browse(cr, uid, ids, context=context): 
            total = 0.0  
            for invid in line.invoice_ids:
                inv = self.pool.get('account.invoice').browse(cr,uid,invid.name.id)
                total += inv.amount_total
            res[line.id] = total    
        return res
        
    def _get_invoiced_balance(self, cr, uid, ids, field_name, arg, context=None):
        res = {}          
        
        for line in self.browse(cr, uid, ids, context=context):  
            residual = 0.0          
            for invid in line.invoice_ids:
                inv = self.pool.get('account.invoice').browse(cr,uid,invid.name.id)
                residual += inv.residual 
            res[line.id] = residual
        return res
        
    def _get_invoiced_state(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            state = False
            if line.invoice_id:
                states = {'draft':'Draft','proforma':'Pro-forma','proforma2':'Pro-forma','open':'Open','paid':'Paid','cancel':'Cancelled'}
                inv = self.pool.get('account.invoice').browse(cr,uid,line.invoice_id.id)
                state = states[inv.state]
            res[line.id] = state
        return res
        
    def view_invoice_task(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])        
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'invoice_form')
        except ValueError, e:
            view_id = False
        if len(obj.invoice_ids)==1:
            return {
                'name': _('Customer Invoice'),
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'current',
                'res_id': obj.invoice_ids[0].name.id,
            }
        else:
            lst = []
            for dt in obj.invoice_ids:
                lst.append(dt.name.id)
            return {
                'name': _('Customer Invoice'),
                'view_type': 'form',
                "view_mode": 'tree,form',
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'domain': "[('id','in',("+str(lst)+"))]",
                'view_id': False,
                'context':{},
            }            
        
    def view_case_sheet(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'case_sheet_form')
        except ValueError, e:
            view_id = False
        return {
            'name': _('Case Sheet'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'case.sheet',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': obj.case_hourly_id.id,
        }
        
    def onchange_type(self, cr, uid, ids, typeval, context=None):
        vals = {}
        if typeval != 'hour_wise': 
            vals['billed_hours'] = False
            vals['remaining_hours'] = False
            vals['hours_spent'] = False
        return {'value':vals}
        
    _columns = {
        'case_hourly_id': fields.many2one('case.sheet', 'Case Sheet No.'),
        'case_fixed_id': fields.many2one('case.sheet', 'Case Sheet No.'),
        'name':fields.many2one('case.tasks.line','Task Related', required=False,readonly=False,),
        'description':fields.char('Description',size=1024),
        'type':fields.selection([('task_wise','Fixed'),('hour_wise','Hourly')],'Type'),
        'hours_spent': fields.float('Hours Spent',),
        'hours_planned': fields.float('Initially Planned Hour(s)',readonly=True),
        'amount':fields.float('Amount'),
        'out_of_pocket_amount': fields.float('Out of Pocket Expense'),
        'state':fields.related('name','state',type='selection',selection=[('New','New'),('In Progress','In Progress'),('Hold','Hold'),('Pending','Pending'),('Completed','Completed'),('Invoiced','Invoiced')],string="Status"),
        'invoiced':fields.boolean('Invoiced'),
        'invoice_ids':fields.one2many('assignment.wise.invoice', 'assignment_wise_id', 'Invoice IDs'),
        'inv_total_amt':fields.function(_get_invoiced_total,string='Total INV Amt',type='float',readonly=True),
        'inv_balance_amt':fields.function(_get_invoiced_balance,string='Balance INV Amt',type='float',readonly=True),
        'billed_hours': fields.float('Total Invoiced Hours'),
        'remaining_hours': fields.float('To be Invoiced Hours'),
        'old_id':fields.many2one('assignment.wise','Old ID'),
        'office_id':fields.many2one('ho.branch','Office'),
        }
        
        
    def copy_data(self, cr, uid, ids, default=None, context=None):
        default = default or {}
        default.update({
            'state':'New',
            'invoiced':False,
            'invoice_ids':[],
            'remaining_hours':0.00,
            'billed_hours':0.00,
            'hours_spent':0.00
        })
        return super(assignment_wise, self).copy_data(cr, uid, ids, default, context)
        
    _defaults = {
    	'state':'New',
    	'type':lambda s, cr, uid, c: c.has_key('type') and c['type'] or False,
    }
    
    def update_assignment_hours(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            if line.hours_spent>0:
                line.remaining_hours = line.remaining_hours + line.hours_spent
        return True
        
    def invoice_task(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            partner_id = line.case_id.client_id.id
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            acc_id = p.property_account_receivable.id
            context.update({'type':'out_invoice'})
            pettyids = self.pool.get('account.account').search(cr, uid, [('name','=','PETTYCASH')])
            pettycash_acc_id = False
            if pettyids and len(pettyids) >0:
                pettycash_acc_id = pettyids[0] 
            product_id=False
            prod_acc_id = False
            
            diff = line.hours_spent - (line.billed_hours or 0.0)
            diff_hours = (line.billed_hours or 0.0) + diff
            if line.name.name.product_id:
                product_id = line.name.name.product_id.id
                
                if line.name.name.product_id.property_account_income:
                    prod_acc_id = line.name.name.product_id.property_account_income.id
            inv_id = self.pool.get('account.invoice').create(cr, uid, {'partner_id':partner_id,'account_id':acc_id,'invoice_line':[(0, 0, {'product_id':product_id,'name': (line.description and line.description or 'Professional Charges'), 'quantity':diff,'price_unit':line.amount,'type':'out_invoice','account_id':prod_acc_id}),(0, 0, {'product_id':False,'name': 'Out of Pocket Expenses', 'quantity':1,'price_unit':line.out_of_pocket_amount,'type':'out_invoice','account_id':pettycash_acc_id})]},context)
            self.write(cr, uid, [line.id], {'invoiced':True,'billed_hours':(line.type=='hour_wise' and diff_hours or 0),'invoice_ids':[(0, 0, {'assignment_wise_id':line.id,'name': inv_id,'hours':(line.type=='hour_wise' and diff or 0)})]})
        return True
    
    def create(self, cr, uid, vals, context=None):
        if vals.has_key('amount') and vals['amount']<=0:
            raise openerp.exceptions.Warning(_('Amount is missing for a Billing Stage line.'))
        vals = self.update_related_task_for_cost_Details(cr, uid, vals, context)    
        retvals = super(assignment_wise, self).create(cr, uid, vals, context=context)
        return retvals            
        
   
        
    def update_related_task_for_cost_Details(self, cr, uid, vals, context=None):
        if vals.has_key('case_fixed_id') and vals['case_fixed_id']:
            retids = self.pool.get('case.tasks.line').search(cr, uid, [('case_id','=',vals['case_fixed_id']),('id','=',vals['name'])])
            if not retids and vals['name']:
                line = self.pool.get('case.tasks.line').browse(cr, uid, vals['name'])
                serids = self.pool.get('case.tasks.line').search(cr, uid, [('case_id','=',vals['case_fixed_id']),('name','=',line.name.id)])
                if len(serids):
                    vals['name'] = serids[0]
                    
        if vals.has_key('case_id') and vals['case_id'] and vals.has_key('task_new_id') and vals['task_new_id']:
            task = self.pool.get('case.tasks.line').browse(cr, uid, vals['task_new_id'])
            retids = self.search(cr, uid, [('case_fixed_id','=',task.case_id.id),('name','!=',task.id)])
            if retids:
                for line in self.browse(cr, uid, retids):
                    if line.name.case_id.id != task.case_id.id and line.name.name.id == task.name.id:
                        self.write(cr, uid, [line.id],{'name':task.id})
        return vals
        
    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.invoiced:
                raise osv.except_osv(_('Error!'),_('You cannot delete an Invoiced Line!'))
                return False   
        return super(assignment_wise, self).unlink(cr, uid, ids, context=context)
        
assignment_wise()

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    
    def _particular_amount_all(self, cr, uid, ids, name, args, context=None):
        res = {}
        
        for invoice in self.browse(cr, uid, ids, context=context):
            total = 0 
            for line in invoice.particular_invoice_line_ids:
                total += line.price_unit
            res[invoice.id] = total
        return res
    
    def _get_invoice_line(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('particular.account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
    
    _columns = {
                'account_id': fields.many2one('account.account', 'Account', required=False, readonly=True, states={'draft':[('readonly',False)]}, help="The partner account used for this invoice."),
                'office_id': fields.many2one('hr.office', 'Office'),
                'ho_branch_id':fields.many2one('ho.branch','HO Branch'),
                #Add particular invoice ilne # Sanal Davis # 27/5/15
                'particular_invoice_line_ids': fields.one2many('particular.account.invoice.line', 'invoice_id', 'Particular Invoice Lines', readonly=True, states={'draft':[('readonly',False)], 'open':[('readonly',False)]}),
                'particular_amount_untaxed': fields.function(_particular_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
                    store={
                    'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['particular_invoice_line_ids'], 20),
                    'particular.account.invoice.line': (_get_invoice_line, ['price_unit','name','invoice_id'], 20),
                    }),
                'case_id':fields.many2one('case.sheet','Case Sheet'),
                }
    
    def create(self, cr, uid, vals, context=None):
        hr_employee_pool = self.pool.get('hr.employee')
        employee_id = hr_employee_pool.search(cr, uid, [('user_id', '=', uid)], context=context)
        employee_obj = hr_employee_pool.browse(cr, uid, employee_id, context=context)
        if vals:
            if vals.get('office_id', False):
                vals['office_id'] = employee_obj[0].office_id.id
            if vals.get('ho_branch_id', False):
                vals['ho_branch_id'] = employee_obj[0].ho_branch_id.id
        order =  super(account_invoice, self).create(cr, uid, vals, context=context)
        return order
    
    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.case_id:
                case_sheet = self.pool.get('case.sheet').browse(cr, uid, obj.case_id.id, context=context)
                for line in case_sheet.associate_payment_lines:
                    if line.invoice_id and line.invoice_id.id == obj.id:
                        self.pool.get('associate.payment').write(cr, uid, [line.id], {'invoiced':False,'invoice_id':False})        
        return super(account_invoice, self).unlink(cr, uid, ids, context=context)
    
    def action_cancel(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.case_id:
                case_sheet = self.pool.get('case.sheet').browse(cr, uid, obj.case_id.id, context=context)
                for line in case_sheet.associate_payment_lines:
                    if line.invoice_id and line.invoice_id.id == obj.id:
                        self.pool.get('associate.payment').write(cr, uid, [line.id], {'invoiced':False, 'invoice_id':False})        
        return super(account_invoice, self).action_cancel(cr, uid, ids, context=context)
    
    def invoice_validate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        
        invoice_objs = self.browse(cr, uid, ids, context=context)
        for invoice_obj in invoice_objs:
            if invoice_obj.case_id:
                assert len(ids) == 1, 'This option should only be used for a single id at a time.'
                ir_model_data = self.pool.get('ir.model.data')
                try:
                    template_id = ir_model_data.get_object_reference(cr, uid, 'legal_e', 'email_template_validate_invoice')[1]
                except ValueError:
                    template_id = False
                try:
                    compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
                except ValueError:
                    compose_form_id = False
                ctx = dict(context)
                ctx.update({
                    'default_model': 'account.invoice',
                    'default_res_id': ids[0],
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id,
                    'default_composition_mode': 'comment',
                    'mark_invoice_as_sent': True,
                    })
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'mail.compose.message',
                    'views': [(compose_form_id, 'form')],
                    'view_id': compose_form_id,
                    'target': 'new',
                    'context': ctx,
                    }
        
        return True
    
account_invoice()

#Starting #create new model particular_account_invoice_line # Sanal Davis # 27/5/15 
class particular_account_invoice_line(osv.osv):
    _name = 'particular.account.invoice.line'
    _description = 'Paricular account line for a account line creation'
    _columns = {
                'name': fields.text('Description', required=True),
                'price_unit': fields.float('Price'),
                'invoice_id': fields.many2one('account.invoice', 'Invoice Reference', ondelete='cascade', select=True),
                }
    
particular_account_invoice_line()
# Ending

class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'
    
    _columns = {
                'account_id': fields.many2one('account.account', 'Account', domain=[('type','<>','view'), ('type', '<>', 'closed')], help="The income or expense account related to the selected product."),
                #Add Office in account_invoice_line
                'office_id':fields.many2one('ho.branch','Office'),
                }
    
account_invoice_line()

class task_activity_line(osv.osv):
    _name = 'task.activity.line'
    _columns = {
        'task_id': fields.many2one('case.task.line', 'Activity Assignment Reference'),
        'name': fields.char('Next Activity', required=True),
        'action_date': fields.datetime('Next Action Date',required=True),
        'completion_date': fields.date('Completion Date'),
        'state': fields.selection([('new','New'),('inprogress','InProgress'),('done','Completed')],'Status'),
        }
    _defaults = {
    	'state':'new',
    	
    }
task_activity_line()


class court_proceedings_stage(osv.osv):
    _name = 'court.proceedings.stage'
    _description = 'Court Proceedings Stage'
    _columns = {
        'name': fields.char('Name', required=True),
        'sequence': fields.integer('Sequence', required=True),
        }
    
    _order = 'sequence'

court_proceedings_stage()


class court_proceedings(osv.osv):
    _name = 'court.proceedings'
    _rec_name = 'parties_desc'
    _inherit = ['mail.thread','ir.needaction_mixin']
    
    def get_proceed_date(self, cr, uid, context=None):
        proceed_date = time.strftime('%Y-%m-%d')
        if context.has_key('case_id') and context['case_id']:
            ids = self.search(cr, uid, [('case_id','=',context['case_id'])],order='id desc',limit=1)        
            for rec in self.browse(cr, uid, ids):
                proceed_date = (rec.next_proceed_date and rec.next_proceed_date or time.strftime('%Y-%m-%d'))
        return proceed_date
    
    def _check_next_proceed_date(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0])
        if obj.proceed_date and obj.next_proceed_date:
            if (datetime.strptime(obj.next_proceed_date, '%Y-%m-%d')-datetime.strptime(obj.proceed_date, '%Y-%m-%d')).days <= 0:
                return False
        return True
    
    def check_proceed_date(self, cr, uid, ids, context=None):
        case = []
        proceed_ids =  self.search(cr, uid, [], context=context)
        for obj in self.browse(cr, uid, proceed_ids):
            proceed_ids1 = self.search(cr, uid, [('proceed_date', '=', obj.proceed_date), ('case_id', '=', obj.case_id.id), ('id', '<>', obj.id)], context=context)
            if proceed_ids1:
                case.append(obj.case_id.name)
        case = list(set(case))
        return True
    
    def _check_proceed_date(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
            proceed_ids = self.search(cr, uid, [('proceed_date', '=', obj.proceed_date), ('case_id', '=', obj.case_id.id), ('id', '<>', obj.id)], context=context)
            if proceed_ids:
                return False
        return True
    

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('case.sheet').browse(cr, uid, ids, context=context):
            for court in line.court_proceedings:
                result[court.id] = True
        return result.keys()

    def _get_location(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('case.sheet').browse(cr, uid, ids, context=context):
            for court in line.court_proceedings:
                result[court.id] = line.ho_branch_id.id
        return result.keys()

    def _get_case_name(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('case.sheet').browse(cr, uid, ids, context=context):
            for court in line.court_proceedings:
                result[court.id] = line.name
        return result.keys()
        
    def run_scheduler_mail_remind_proceed(self, cr, uid, context=None):
        mailids = []
        cr.execute('select current_date')
        current_date = cr.fetchone()[0]
        searids = self.search(cr, uid, [('case_id.state','in',('new','inprogress')),('next_proceed_date','=',current_date)])
        for line in self.browse(cr, uid, searids, context=context):
            #Mail To Assignee            
            mail_temp_id = self.pool.get('email.template').search(cr, uid, [('name','=','Court Proceedings Reminder for Assignee')])
            temp_obj = self.pool.get('email.template').browse(cr, uid, mail_temp_id[0])            
            if line.case_id and line.case_id.assignee_id and line.case_id.assignee_id.work_email:
                self.pool.get('email.template').send_mail(cr, uid, temp_obj.id, line.id, force_send=True, context=context)
                
            
            if line.case_id and line.case_id.project_id:
                team_email_to = False
                team_email_to = ', '.join([member.partner_id.email if member.partner_id.email else '' for member in line.case_id.project_id.members])  
                
                if team_email_to:
                    if line.case_id.assignee_id.work_email:
                        team_email_to=team_email_to.replace(line.case_id.assignee_id.work_email,'')
                    context['email_to'] = team_email_to
                    self.pool.get('email.template').send_mail(cr, uid, temp_obj.id, line.id, force_send=True, context=context)
                
            #Mail to Other Associates    
            asso_mail_temp_id = self.pool.get('email.template').search(cr, uid, [('name','=','Court Proceedings Reminder for Other Associate')])
            asso_temp_obj = self.pool.get('email.template').browse(cr, uid, asso_mail_temp_id[0]) 
            email_to = ', '.join([associate.name.email if associate.name.email else '' for associate in line.case_id.other_assignee_ids])   
            for associate in line.case_id.other_assignee_ids:                
                if associate.name.email:                    
                    mailids.append(associate.name.email)
            if len(mailids):
                context['email_to'] = email_to
                self.pool.get('email.template').send_mail(cr, uid, asso_temp_obj.id, line.id, force_send=True, context=context)
        return True
    
    
    def _parties_desc(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pro in self.browse(cr, uid, ids, context=context):
            parties_name = ''
            if pro.case_id:
                for line in pro.case_id.first_parties:
                    parties_name +=  "'" +line.name + "'"
                    break
                if parties_name:
                    for line in pro.case_id.opp_parties:
                        parties_name +=  '     Vs      ' + "'" + line.name + "'"
                        break
            res[pro.id] = parties_name
        return res
    
    _columns = {
        'case_id': fields.many2one('case.sheet', 'File Number'),
        'name': fields.text('Court Process', required=True, track_visibility='onchange'),
        'proceed_date': fields.date('Proceed Date',required=True, track_visibility='onchange'),
        'flg_next_date':fields.boolean('Next Date?', track_visibility='onchange'),
        'next_proceed_date':fields.date('Next Proceed Date', track_visibility='onchange'),
        'client_id':fields.related('case_id','client_id',type='many2one',relation='res.partner',string='Client',
            store={
                'court.proceedings': (lambda self, cr, uid, ids, c={}: ids, ['case_id'], 10),
                'case.sheet': (_get_order, ['client_id'], 10),
            }),
        'tasks_lines':fields.related('case_id','tasks_lines',type='one2many',relation='case.tasks.line',string='Assignee Tasks'),
        'associate_tasks_lines':fields.related('case_id', 'associate_tasks_lines', type='one2many', relation='associate.tasks.line', string='Associate Tasks'),
        'client_tasks_lines': fields.related('case_id', 'client_tasks_lines',type='one2many',relation='client.tasks.line',string='Client Tasks'),
        'court_proceedings':fields.related('case_id', 'court_proceedings', type='one2many', relation='court.proceedings', string='Proceedings History'),
        'billable':fields.selection([('bill','Billable'),('nobill','Non-Billable')],'Billable', track_visibility='onchange'),
        'effective':fields.selection([('effective','Effective'),('noeffective','Non-Effective')],'Effective', track_visibility='onchange'),
        'invoiced':fields.boolean('Invoiced ?', track_visibility='onchange'),
        'ho_branch_id':fields.related('case_id','ho_branch_id',type='many2one',relation='ho.branch',string='Location',
            store={
                'court.proceedings': (lambda self, cr, uid, ids, c={}: ids, ['case_id'], 10),
                'case.sheet': (_get_location, ['ho_branch_id'], 10),
            }),
        'file_number':fields.related('case_id','name',type='char',string='File Number',
            store={
                'court.proceedings': (lambda self, cr, uid, ids, c={}: ids, ['case_id'], 10),
                'case.sheet': (_get_case_name, ['name'], 10),
            }),
        'old_id':fields.many2one('court.proceedings','Old ID'), 
        
        'parties_desc': fields.function(_parties_desc, string='Parties', type='char'),
        'court_id':fields.related('case_id', 'court_id', type='many2one', relation='court.master', string='Court'),
        'stage_id': fields.many2one('court.proceedings.stage', 'Stage', track_visibility='onchange'),
        'time_sheet_ids': fields.one2many('hr.analytic.timesheet', 'court_proceed_id', 'Timesheet Activities'),
        'date_missing': fields.boolean('Date Missing'),
        'checked': fields.boolean('Checked'),
        'closed': fields.boolean('Closed'),
        
        'not_fully_billed':  fields.boolean('Not Fully Billed'),
        }
    _defaults = {
        'proceed_date':lambda s, cr, uid,c: s.get_proceed_date(cr, uid, c),
        'next_proceed_date':lambda *a: False,
        'flg_next_date':True,
    }
    _order = 'proceed_date asc'
    _constraints = [
        (_check_next_proceed_date, 'Error! Next Proceed Date Should be Greater Than Proceed Date!', ['next_proceed_date']),
        (_check_proceed_date, 'You can not have 2 proceedings that overlaps on same day!', ['proceed_date'])
        ]
    
    def check_issues(self, cr, uid, ids, context=None):
        proceeding_ids =  self.search(cr, uid, [('checked', '=', True),('case_id.state', 'not in', ('new','done','cancel','transfer', 'hold'))], context=context)
        case_ids = [proce_obj.case_id.id for proce_obj in self.browse(cr, uid, proceeding_ids, context=context)]
        case_ids = list(set(case_ids))
#         case_ids = [19228,916]
        for case_id in case_ids:
            proc_ids =  self.search(cr, uid, [('case_id', '=', case_id),('next_proceed_date', '!=', False)], order='next_proceed_date desc', context=context)
            if proc_ids:
                proceed_obj = self.browse(cr, uid, proc_ids[0], context=context)
                res_ids = self.search(cr, uid, [('case_id', '=', case_id),('proceed_date', '=', proceed_obj.next_proceed_date)], context=context)
#                 import pdb
#                 pdb.set_trace()
                if not res_ids:
                    if proceed_obj.next_proceed_date < time.strftime('%Y-%m-%d') and not proceed_obj.date_missing:
                        self.write(cr, uid, [proceed_obj.id], {'checked': False, 'date_missing': False}, context=context)
                else:
                    prod_obj = self.browse(cr, uid, res_ids[0], context=context)
                    if not prod_obj.next_proceed_date and prod_obj.stage_id.id == 53:
                        self.write(cr, uid, [proceed_obj.id], {'checked': False, 'date_missing': False}, context=context)
        return True
    
    
    def check_fully_billed(self, cr, uid, context=None):
        invoice_pool = self.pool.get('account.invoice')
        proceeding_ids =  self.search(cr, uid, [('date_missing', '=', False),('case_id.state', 'not in', ('new','done','cancel','transfer', 'hold'))], context=context)
        case_ids = [proce_obj.case_id.id for proce_obj in self.browse(cr, uid, proceeding_ids, context=context) if proce_obj.case_id.billed_amount > proce_obj.case_id.received_amount]
        case_ids = list(set(case_ids))
        for case_id in case_ids:
            payment_due = False
            invoice_ids = invoice_pool.search(cr, uid, [('case_id', '=', case_id), ('state', '=', 'open')], order='date_invoice asc', context=context)
            if invoice_ids:
                invoice_obj = invoice_pool.browse(cr, uid, invoice_ids[0], context=context)
                due_date = (datetime.strptime(invoice_obj.date_invoice, '%Y-%m-%d') + timedelta(days=60)).strftime('%Y-%m-%d')
                if due_date <= time.strftime('%Y-%m-%d'):
                    payment_due = True
            if payment_due:
                
                proc_ids =  self.search(cr, uid, [('case_id', '=', case_id),('next_proceed_date', '!=', False),('name', '!=', 'Missing Dates(System generated message)')], order='next_proceed_date desc', context=context)
                if proc_ids:
                    proceed_obj = self.browse(cr, uid, proc_ids[0], context=context)
                    res_ids = self.search(cr, uid, [('case_id', '=', case_id),('proceed_date', '=', proceed_obj.next_proceed_date)], context=context)
                    if not res_ids:
                        if proceed_obj.next_proceed_date > time.strftime('%Y-%m-%d'):
                            self.write(cr, uid, [proceed_obj.id], {'not_fully_billed': True}, context=context)
                    proc_ids.remove(proc_ids[0])
                    if proc_ids:
                        cr.execute('update court_proceedings set not_fully_billed =False where id in %s',(tuple(proc_ids),))
                    
                    
        proceeding_ids = [proce_obj.id for proce_obj in self.browse(cr, uid, proceeding_ids, context=context) if proce_obj.case_id.billed_amount == proce_obj.case_id.received_amount]
#         proceeding_ids +=  self.search(cr, uid, [('date_missing', '=', True),('not_fully_billed', '=', True)], context=context)
        proceeding_ids = list(set(proceeding_ids))
        self.write(cr, uid, proceeding_ids, {'not_fully_billed': False}, context=context)
        
        return True
    
    
    def missing_date_scheduler(self, cr, uid, context=None):
        proceeding_ids =  self.search(cr, uid, [('case_id.work_type','!=', 'non_litigation'),('case_id.state', 'not in', ('new','done','cancel','transfer', 'hold')),('case_id.division_id.exclude_dashboard', '=', False)], context=context)
        case_ids = [proce_obj.case_id.id for proce_obj in self.browse(cr, uid, proceeding_ids, context=context)]
        case_ids = list(set(case_ids))
        for case_id in case_ids:
            proc_ids =  self.search(cr, uid, [('case_id', '=', case_id),('next_proceed_date', '!=', False)], order='next_proceed_date desc', context=context)
            if proc_ids:
                proceed_obj = self.browse(cr, uid, proc_ids[0], context=context)
                res_ids = self.search(cr, uid, [('case_id', '=', case_id),('proceed_date', '=', proceed_obj.next_proceed_date)], context=context)
                if not res_ids:
                    if proceed_obj.next_proceed_date < time.strftime('%Y-%m-%d'):
                        self.write(cr, uid, [proceed_obj.id], {'date_missing': True, 'checked': True}, context=context)
                        
            miss_procee_ids =  self.search(cr, uid, [('case_id', '=', case_id),('next_proceed_date', '=', False),('flg_next_date', '=', False)], context=context)   
            for procee_obj in self.browse(cr, uid, miss_procee_ids, context=context):
                date = (datetime.strptime(procee_obj.proceed_date, '%Y-%m-%d') + timedelta(days=90)).strftime('%Y-%m-%d')
                if date < time.strftime('%Y-%m-%d'):
                    self.write(cr, uid, [procee_obj.id], {'date_missing': True, 'checked': True}, context=context)
            
            miss_ids =  self.search(cr, uid, [('case_id', '=', case_id), ('next_proceed_date', '=', False), ('flg_next_date', '=', True)], context=context)   
            for procee_obj in self.browse(cr, uid, miss_ids, context=context):
                if procee_obj.proceed_date < time.strftime('%Y-%m-%d'):
                    self.write(cr, uid, [procee_obj.id], {'date_missing': True, 'checked': True}, context=context)
            
            miss_date_ids =  self.search(cr, uid, [('case_id', '=', case_id),('date_missing', '=', True)], context=context)
            for procee_obj in self.browse(cr, uid, miss_date_ids, context=context):
                pro_ids = self.search(cr, uid, [('case_id', '=', case_id),('proceed_date', '=', procee_obj.next_proceed_date)], context=context)
                if pro_ids:
                    self.write(cr, uid, [procee_obj.id], {'date_missing': False, 'checked': True}, context=context)
                    
        casesheet_ids = self.pool.get('case.sheet').search(cr, uid, [('work_type','!=', 'non_litigation'), ('court_id','!=', False), ('court_proceedings', '=', False),('state', 'not in', ('draft','done','cancel','transfer', 'hold')),('division_id.exclude_dashboard', '=', False)], context=context)
        case_ids = [case_obj.id for case_obj in self.pool.get('case.sheet').browse(cr, uid, casesheet_ids, context=context) if (datetime.strptime(case_obj.date, '%Y-%m-%d') + timedelta(days=180)).strftime('%Y-%m-%d') < time.strftime('%Y-%m-%d')]
        for case_id in case_ids:
            vals = {
                'case_id': case_id,
                'proceed_date': time.strftime('%Y-%m-%d'),
                'name': 'Missing Dates(System generated message)',
                'checked': True,
                'date_missing': True,
                }
            self.create(cr, uid, vals, context=context)
        proceed_stage_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.proceed_stage_id.id
        proceeding_ids =  self.search(cr, uid, ['|',('case_id.state', 'in', ('new','done','cancel','transfer', 'hold')),('stage_id', '=', proceed_stage_id)], context=context)
        self.write(cr, uid, proceeding_ids, {'checked': True, 'date_missing': False}, context=context)
         
        return True 
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('order_by_next_proceed_date', False):
            order = 'next_proceed_date asc'
        return super(court_proceedings, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def button_refresh(self, cr, uid, ids, context=None):
        return True
        
    def onchange_case_id(self, cr, uid, ids, case_id, context=None):
        if context is None:
            context = {}
        res = {}
        if case_id:
            context['case_id'] = case_id
            res['proceed_date'] = self.get_proceed_date(cr, uid, context=context)
        return {'value':res}
    
    def onchange_caseid(self, cr, uid, ids, case_id, context=None):
        res={}
        return {'value':res}
   
    def default_get(self, cr, uid, fields_list, context=None):
        if not context:
            context = {}
        res = super(court_proceedings, self).default_get(cr, uid, fields_list, context=context) 
        if context.has_key('case_id'):        
            proceed_date = time.strftime('%Y-%m-%d')
            proceed_id = self.search(cr, uid, [('case_id','=',context['case_id'])],limit=1, order='id desc', context=context)
            if proceed_id:
                proceed_date = self.browse(cr, uid, proceed_id, context=context)[0].next_proceed_date
            
            res.update({'proceed_date':proceed_date})
        return res
        
    def onchange_flg_next_date(self, cr, uid, ids, flg_next_date, context=None):
        res={}
        res['next_proceed_date'] = False   
        return {'value':res}
        
    def create(self, cr, uid, vals, context=None):
        if not vals.get('flg_next_date', False):
            vals['next_proceed_date'] = False
            
        
        if vals.get('proceed_date', False):
            ids = self.search(cr, uid, [('case_id','=',vals['case_id'])],order='id desc',limit=1)
            proceed_date = False     
            for rec in self.browse(cr, uid, ids):
                proceed_date = rec.next_proceed_date 
            if proceed_date and vals['proceed_date'] != proceed_date:
                vals['proceed_date'] = proceed_date
        
        if vals.get('case_id', False):
            proc_ids =  self.search(cr, uid, [('case_id', '=', vals['case_id']),('next_proceed_date', '!=', False)], order='next_proceed_date desc', context=context)
            if proc_ids:
                proceed_obj = self.browse(cr, uid, proc_ids[0], context=context)
                if proceed_obj.next_proceed_date == vals['proceed_date'] and proceed_obj.date_missing:
                    self.write(cr, uid, [proceed_obj.id], {'date_missing': False}, context=context)
        
                
        if vals.get('stage_id', False):
            proceed_stage_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.proceed_stage_id.id
            if vals['stage_id'] == proceed_stage_id:
                vals.update({'date_missing': False, 'checked': True, 'closed': True})
            else:
                vals.update({'date_missing': False, 'checked': False, 'closed': False})
                    
        retvals = super(court_proceedings, self).create(cr, uid, vals, context=context)
        return retvals
        

    def write(self, cr, uid, ids, vals, context=None):
        if vals.has_key('flg_next_date'):
            if not vals['flg_next_date']:
                vals['next_proceed_date'] = False
        if vals.get('next_proceed_date', False) or vals.get('proceed_date', False) or vals.get('name', False) or vals.get('case_id', False):
            vals.update({'date_missing': False, 'checked': False, 'closed': False})
        if vals.get('proceed_date', False):
            proceed_date = False
            for rec in self.browse(cr, uid, ids):
                proceed_ids = self.search(cr, uid, [('case_id','=',rec.case_id.id),('id', '!=', rec.id)],order='id desc',limit=1)
                for procee_obj in self.browse(cr, uid, proceed_ids):   
                    proceed_date = procee_obj.next_proceed_date 
            if proceed_date and vals['proceed_date'] != proceed_date:
                vals['proceed_date'] = proceed_date
        
        if vals.get('stage_id', False):
            proceed_stage_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.proceed_stage_id.id
            if vals['stage_id'] == proceed_stage_id:
                vals.update({'date_missing': False, 'checked': True, 'closed': True})
            else:
                vals.update({'date_missing': False, 'checked': False, 'closed': False})
        retvals = super(court_proceedings, self).write(cr, uid, ids, vals, context=context)
        return retvals
    
    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            proceed_ids = self.search(cr, uid, [('case_id', '=', obj.case_id.id),('id', '!=', ids[0])], context=context)
            self.write(cr, uid, proceed_ids, {'checked': False}, context=context)
        return super(court_proceedings, self).unlink(cr, uid, ids, context=context)
    
    
    def copy_data(self, cr, uid, ids, default=None, context=None):
        default = default or {}
        if context is None:
            context = {}
        case_id = self.browse(cr, uid, ids, context=context).case_id.id
        context['case_id'] = case_id
        
        default.update({
#             'next_proceed_date':False,
            'checked': False,
            'date_missing': False,
            'case_id' : False,
#             'proceed_date': self.get_proceed_date(cr, uid, context=context)
            })
        return super(court_proceedings, self).copy_data(cr, uid, ids, default, context)
        
        
court_proceedings()

class first_parties_details(osv.osv):
    _name = 'first.parties.details'
    
    _columns = {
        'sl_no': fields.integer('Sl no'),
        'party_id': fields.many2one('case.sheet', 'First Parties Reference'),
        'name': fields.char('Party Name', required=True),
        'type': fields.selection([('plaintiff','PLAINTIFF'),('petitioner','PETITIONER'),('applicant','APPLICANT'),('appellant','APPELLANT'),('caveator','CAVEATOR'),('intervener','INTERVENER'),('claimaints','CLAIMANTS')],'Type',required=True),
        }
    _order = 'sl_no'
    
    def get_selection_value(self, cr, uid, field, field_id):
        res = ''
        if not field_id:
            return res
        fields_get_result = self.fields_get(cr, uid, [field,])
        if fields_get_result:
            selection = fields_get_result[field]['selection']
            if selection:
                for key_value in selection:
                    if field_id == key_value[0]:
                        res = key_value[1]
        return res
first_parties_details()

class opp_parties_details(osv.osv):
    _name = 'opp.parties.details'
    
    _columns = {
        'sl_no': fields.integer('Sl no'),
        'party_id': fields.many2one('case.sheet', 'Opposite Parties Reference'),
        'name': fields.char('Party Name'),
        'type': fields.selection([('defendant','DEFENDANT'),('respondant','RESPONDENT'),('oopparty','OPP PARTY'),('accused','ACCUSED'),('caveatee','CAVEATEE')],'Type'),
        }    
        
        
    _order = 'sl_no'
    
    def get_selection_value(self, cr, uid, field, field_id):
        res = ''
        if not field_id:
            return res
        fields_get_result = self.fields_get(cr, uid, [field,])
        if fields_get_result:
            selection = fields_get_result[field]['selection']
            if selection:
                for key_value in selection:
                    if field_id == key_value[0]:
                        res = key_value[1]
        return res
    
opp_parties_details()


class opp_parties(osv.osv):
    _name = 'opp.parties'
    _columns = {
        'name': fields.char('Name', required=True),
        'email': fields.char('Email',size=240),
        'phone': fields.char('Phone',size=32),
        'mobile': fields.char('Mobile',size=32),
        } 
        
opp_parties()

class fixed_price_stages(osv.osv):
    _name = 'fixed.price.stages'
    _order = 'case_id desc'
        
    def _get_invoiced_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}        
        for line in self.browse(cr, uid, ids, context=context):
            total = 0.0
            if line.invoice_id:
                inv = self.pool.get('account.invoice').browse(cr,uid,line.invoice_id.id)
                total = inv.amount_total
            res[line.id] = total    
        return res
        
    def _get_invoiced_balance(self, cr, uid, ids, field_name, arg, context=None):
        res = {}          
        for line in self.browse(cr, uid, ids, context=context):
            residual = 0.0
            if line.invoice_id:
                inv = self.pool.get('account.invoice').browse(cr,uid,line.invoice_id.id)
                residual = inv.residual 
            res[line.id] = residual
        return res
        
    def _get_invoiced_state(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            state = False
            if line.invoice_id:
                states = {'draft':'Draft','proforma':'Pro-forma','proforma2':'Pro-forma','open':'Open','paid':'Paid','cancel':'Cancelled'}
                inv = self.pool.get('account.invoice').browse(cr,uid,line.invoice_id.id)
                state = states[inv.state]
            res[line.id] = state
        return res
        
    def view_invoice_task(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'invoice_form')
        except ValueError, e:
            view_id = False
        return {
            'name': _('Customer Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': obj.invoice_id.id,
        }        
        
    def view_case_sheet(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids[0])
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'case_sheet_form')
        except ValueError, e:
            view_id = False
        return {
            'name': _('Case Sheet'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'case.sheet',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': obj.case_id.id,
        }
    
    _columns = {
        'case_id': fields.many2one('case.sheet', 'File Number'),
        'name':fields.many2one('case.tasks.line','Task Related', required=True,readonly=False,),
        'description':fields.char('Description',size=1024),
        'assignee_id': fields.many2one('hr.employee', 'Assignee'),
        'percent_amount':fields.float('Amount in %', digits_compute=dp.get_precision('Account')),
        'amount': fields.float('Amount', digits_compute=dp.get_precision('Account')),
        'out_of_pocket_amount': fields.float('Out of Pocket Expense'),
        'state':fields.related('name','state',type='selection',selection=[('New','New'),('In Progress','In Progress'),('Hold','Hold'),('Pending','Pending'),('Completed','Completed'),('Invoiced','Invoiced')],string="Status"),
        'invoiced':fields.boolean('Invoiced'),
        'invoice_id':fields.many2one('account.invoice','Invoice ID'),
        'inv_state': fields.function(_get_invoiced_state,string='INV Status', type='char', readonly=True),
        'inv_total_amt':fields.function(_get_invoiced_total,string='Total INV Amt',type='float',readonly=True),
        'inv_balance_amt':fields.function(_get_invoiced_balance,string='Balance INV Amt',type='float',readonly=True),
        'old_id':fields.many2one('fixed.price.stages','Old ID'),
        'office_id':fields.many2one('ho.branch','Office'), #add office field # Sanal Davis # 27/5/15 
        }
    _defaults = {
    	'state':'New',    	
    }
    
    # Starting Sanal Davis 27/5/15
    def onchange_office(self, cr, uid, ids, name, context=None):
        '''
        This function writes the office field value
        '''
        case_tasks_line_pool = self.pool.get('case.tasks.line')
        case_tasks_line = case_tasks_line_pool.browse(cr, uid, name, context=context)
        if name:
            office_id = case_tasks_line.office_id.id or False   
        else:
            office_id = False
        return {'value': {'office_id': office_id}}
    # Ending
    
    def copy_data(self, cr, uid, ids, default=None, context=None):
        default = default or {}
        default.update({
            'state':'New',
            'invoiced':False,
            'invoice_id':False
        })
        return super(fixed_price_stages, self).copy_data(cr, uid, ids, default, context)
        
        
    def update_related_task_for_cost_Details(self, cr, uid, vals, context=None):
        if vals.has_key('case_id') and vals['case_id'] and vals.has_key('task_new_id') and vals['task_new_id']:
            task = self.pool.get('case.tasks.line').browse(cr, uid, vals['task_new_id'])
            retids = self.search(cr, uid, [('case_id','=',task.case_id.id),('name','!=',task.id)])
            if retids:
                for line in self.browse(cr, uid, retids):
                    if line.name.case_id.id != task.case_id.id and line.name.name.id == task.name.id:
                        self.write(cr, uid, [line.id],{'name':task.id})
        return vals
    
    def check_task_in_assignee_tasks(self, cr, uid, ids, taskid, context=None):
        assignids = []
        for line in context['assignee_task_lines']:
            assignids.append(line[2]['name'])
        if taskid not in assignids:
            warning = {
                       'title': _('Error!'),
                       'message' : _('Selected Task is not Present in Assignee Tasks.')
                    }
            return {'value': {'name':False}, 'warning': warning}  
        return {'value': {'name':taskid}}  
    
    def invoice_stage(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            partner_id = line.case_id.client_id.id
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            acc_id = p.property_account_receivable.id
            context.update({'type':'out_invoice'})
            pettyids = self.pool.get('account.account').search(cr, uid, [('name','=','PETTYCASH')])
            pettycash_acc_id = False
            if pettyids and len(pettyids) >0:
                pettycash_acc_id = pettyids[0]                
            product_id=False
            prod_acc_id = False
            if line.name.name.product_id:
                product_id = line.name.name.product_id.id
                if line.name.name.product_id.property_account_income:
                    prod_acc_id = line.name.name.product_id.property_account_income.id
                
            inv_id = self.pool.get('account.invoice').create(cr, uid, {'partner_id':partner_id,'account_id':acc_id,'invoice_line':[(0, 0, {'product_id':product_id,'name':(line.description and line.description or 'Professional Charges'), 'quantity':1.0,'price_unit':line.amount,'type':'out_invoice','account_id':prod_acc_id}), (0, 0, {'name':'Out of Pocket Expenses', 'quantity':1.0,'price_unit':line.out_of_pocket_amount,'type':'out_invoice','account_id':pettycash_acc_id})]})
            self.write(cr, uid, [line.id], {'invoiced':True,'invoice_id':inv_id})
        return True
        
    def onchange_percent(self, cr, uid, ids, percent, fixed_price, casetype_id, bill_type,amount_pre, context=None):
        if fixed_price:
            amount = (float(fixed_price)*percent)/100
            return {'value':{'amount':amount}}
        else:
            raise osv.except_osv(_('Error!'),_('Enter the Fixed Price Amount First!'))
        return {'value':{'amount':0,'percent_amount':0}}
        
    def onchange_amount(self, cr, uid, ids, amount,fixed_price, casetype_id, bill_type,percent_pre, context=None):
        if fixed_price:
            return {'value':{}}
        else:
            raise osv.except_osv(_('Error!'),_('Enter the Fixed Price Amount First!'))
        return {'value':{'percent_amount':0,'amount':0}}
    
    
    def write(self, cr, uid, ids, vals, context=None):
        if context is None:
            context = {}
        if not context.get('case_copy', False):
            if vals.get('amount', False) or vals.get('out_of_pocket_amount', False) or vals.get('office_id', False) or vals.get('description', False) or vals.get('name', False):
                for data_obj in self.browse(cr, uid, ids, context=context):
                    if data_obj.case_id.state != 'new' and  not self.pool.get('res.users').has_group(cr, uid, 'legal_e.group_case_sheet_operation_manager'):
                        raise osv.except_osv(_('Warning!'), _('You are not permitted to modifie this record. Contact case sheet operations manager.'))
        res = super(fixed_price_stages, self).write(cr, uid, ids, vals, context=context)
        return res
    
    
    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.invoiced and obj.state == 'Completed':
                raise osv.except_osv(_('Error!'),_('You cannot delete an Invoiced Line!'))
                return False
            if obj.case_id.state != 'new' and  not self.pool.get('res.users').has_group(cr, uid, 'legal_e.group_case_sheet_operation_manager'):
                raise osv.except_osv(_('Warning!'), _('You are not permitted to delete this record. Contact case sheet operations manager.'))
        
        return super(fixed_price_stages, self).unlink(cr, uid, ids, context=context)
        
fixed_price_stages()


class project(osv.osv):
    _inherit = 'project.project'
    
    def set_done(self, cr, uid, ids, context=None):
        
        if not context.get('case_close', False):
            for project_id in ids:
                sheet_ids = self.pool.get('case.sheet').search(cr, uid, [('project_id', '=', project_id)], context=context)
                for sheet_id in sheet_ids:
                    state = self.pool.get('case.sheet').browse(cr, uid, sheet_id, context=context).state
                    if state == 'inprogress':
                        raise openerp.exceptions.Warning(_('You cannot close the project!\n\n Please close the case sheet before closing the project.'))
        res = super(project, self).set_done(cr, uid, ids, context=context)
        return res
    
project()


class project_task_type(osv.osv):
    _inherit = 'project.task.type'
    _columns = {
        'state': fields.selection(_TASK_STATE, 'Related Status', required=True,
                        help="The status of your document is automatically changed regarding the selected stage. " \
                            "For example, if a stage is related to the status 'Close', when your document reaches this stage, it is automatically closed."),
        }

project_task_type()

class project_task_history(osv.osv):
    _inherit = 'project.task.history'
    _columns = {
       'state': fields.selection([('draft', 'New'), ('cancelled', 'Cancelled'),('open', 'In Progress'),('pending', 'Pending'), ('done', 'Done'),('hold', 'Hold')], 'Status'),
        }

project_task_history()

        
class project_task(osv.osv):
    _inherit = 'project.task'
    _order = 'due_days desc'
    _track = {
        'state': {
            'protsk.mt_task_state': lambda self, cr, uid, obj, ctx=None: obj['state'] in ['draft','open','pending','done','cancelled']
        },
    }
 
    def _get_assigned_to(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            assigned_to = False
            if line.task_for == 'employee':
                if line.assignee_id:
                    assigned_to = line.assignee_id.name
            if line.task_for == 'associate':
                if line.other_assignee_id:
                    assigned_to = line.other_assignee_id.name
            if line.task_for == 'customer':
                if line.client_id:
                    assigned_to = line.client_id.name
            res[line.id] = assigned_to
        return res
        
    def _get_manager_user(self, cr, uid, ids, context=None):
        res = {}
        for project in self.browse(cr, uid, ids, context=context):
            manager = False
            if project:
                if project and project.user_id:
                    manager = project.user_id.id
            res[project.id] = manager
        return res.keys()
    
    def onchange_assignee(self, cr, uid, ids, assignee_id, context=None):
        res = {}
        if not assignee_id:
            res['assignee_user_id'] = False
        else:
            emp = self.pool.get('hr.employee').browse(cr, uid, assignee_id)
            user_id = False
            if emp and emp.user_id:
                user_id = emp.user_id.id
            res['assignee_user_id'] = user_id
        return {'value':res}    
        
    def compute_due_days(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        
        for line in self.browse(cr, uid, ids, context=context):
            days = False
            if line.date_deadline:
                days = (datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d') - datetime.strptime(line.date_deadline, '%Y-%m-%d')).days
            res[line.id] = days
        return res

    def _compute_due_days_string(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        searids = self.search(cr, uid, [('state','!=','done'),'|',('today_date','=',False),('today_date','!=',time.strftime('%Y-%m-%d'))])
        for line in self.browse(cr, uid, searids, context=context):
            days = False
            due_days_string = False
            if line.date_deadline:
                if line.state == 'done':
                    due_days_string = 'completed'
                else:    
                    days = (datetime.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d') - datetime.strptime(line.date_deadline, '%Y-%m-%d')).days
                    if days>0:
                        due_days_string = str(days) + ' days over due'
                    else:
                        due_days_string = str(abs(days)) + ' days to complete'
                    cr.execute('update project_task set due_days =%s,today_date=%s where id=%s',(days,time.strftime('%Y-%m-%d'),line.id))
                    cr.commit()
            res[line.id] = due_days_string
        return res
    
    def run_scheduler(self, cr, uid, context=None):
        cr.execute('select current_date')
        current_date = cr.fetchone()[0]
        searids = self.search(cr, uid, [('state','in', ('draft', 'open', 'pending'))], context=context)
        pending_stage_id = False
        comids = self.pool.get('project.task.type').search(cr, uid, [('name','=','Pending'),('state','=','pending')])
        if comids and len(comids):
            pending_stage_id = comids[0]
        for line in self.browse(cr, uid, searids, context=context):
            days = 0
            due_days_string = False
            state = line.stage_id.id
            sta = line.state
            if line.date_deadline:
                days = (datetime.strptime(current_date, '%Y-%m-%d') - datetime.strptime(line.date_deadline, '%Y-%m-%d')).days
                if days>0:
                    due_days_string = str(days) + ' days over due'
                    state = pending_stage_id and pending_stage_id or state
                    sta = 'pending'
                else:
                    due_days_string = str(abs(days)) + ' days to complete'
            cr.execute('update project_task set due_days =%s,due_days_string =%s,today_date=%s,stage_id=%s, state=%s where id=%s',(days,due_days_string,current_date,state,sta,line.id))
            cr.commit()            
        return True 
         
    def run_scheduler_for_task_message(self, cr, uid, context=None):
        searids = self.pool.get('project.task').search(cr, uid, [('flg_message','=',True)])
        vals = {}
        vals['remaining_hours'] = 0.0
        vals['state']='done'
        comids = self.pool.get('project.task.type').search(cr, uid, [('name','=','Completed'),('state','=','done')])
        if comids and len(comids):
            vals['stage_id']=comids[0]
        vals['progress']=100    
        vals['flg_message']=False
        if searids:
            self.pool.get('project.task').write(cr, uid, searids, vals)
        return True
    
    def run_scheduler_for_pending_task_message(self, cr, uid, context=None):
        r = []
        j = []
        search_ids = self.search(cr, uid, [('state','=','pending')])
        user = self.pool.get('res.users').browse(cr, uid, uid)
        for dt in self.pool.get('project.task').read(cr, uid, search_ids, ['assignee_id']):
            if dt['assignee_id']:
                r.append(dt['assignee_id'][0])
        for line in self.pool.get('hr.employee').browse(cr,uid,list(set(r)),context=context):
            srch_ids = self.search(cr,uid,[('state','=','pending'),('assignee_id','=',line.id)])
            for self_obj in self.read(cr,uid,srch_ids, ['name','project_id'],context=context):
                j.append('Project : {0} ====> Task : {1}'.format(self_obj['project_id'][1],self_obj['name'][1]))
        #Mail To Assignee
            if line.user_id and line.user_id.partner_id:
                post_values =  {
                    'email_from': user.partner_id.email or False,  
                    'partner_ids': [line.user_id.partner_id.id],
                    'subject': 'PENDING Tasks',                
                    'body': 'Following List of Tasks Assigned for you are PENDING : \n %s.' % (j),
                    }
                subtype = 'mail.mt_comment'
                self.message_post(cr, uid, [srch_ids[0]], type='comment', subtype=subtype, context=context, **post_values)
        return True
        
    def _get_reg_number(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        task = self.browse(cr, uid, ids[0])
        case_ids = self.pool.get('case.sheet').search(cr, uid, [('project_id','=',task.project_id.id)])
        for case in self.pool.get('case.sheet').browse(cr, uid, case_ids):
            res[task.id] = case.reg_number
        return res
        
    def _get_first_parties(self, cr, uid, ids, field_names, arg=None, context=None):
        res = {}
        task = self.browse(cr, uid, ids[0])
        firstids = []
        case_ids = self.pool.get('case.sheet').search(cr, uid, [('project_id','=',task.project_id.id)])
        for case in self.pool.get('case.sheet').browse(cr, uid, case_ids):
            for first in case.first_parties:
                firstids.append((0,0,{'type':first.type,'name':first.name}))
            res[task.id] = firstids
        return res
        
    def _get_opp_parties(self, cr, uid, ids, field_names, arg=None, context=None):
        res = {}
        task = self.browse(cr, uid, ids[0])
        oppids = []
        case_ids = self.pool.get('case.sheet').search(cr, uid, [('project_id','=',task.project_id.id)])
        for case in self.pool.get('case.sheet').browse(cr, uid, case_ids):
            for opp in case.opp_parties:
                oppids.append((0,0,{'type':opp.type,'name':opp.name}))
            res[task.id] = oppids
        return res
        
    def _get_bill_amount(self, cr, uid, ids, field_names, arg=None, context=None):
        res = {}
        task = self.browse(cr, uid, ids[0])
        line_ids = self.pool.get('case.tasks.line').search(cr, uid, [('task_id','=',task.id)])
        bill_lines = self.pool.get('fixed.price.stages').search(cr, uid, [('name','in',line_ids)])
        if len(bill_lines)>0:
            for line in self.pool.get('fixed.price.stages').browse(cr, uid, bill_lines):            
                res[task.id] = (line.amount and line.amount or 0.00)
        else:
            res[task.id] = 0.00    
        return res 
        
    def update_project_task_user(self, cr, uid, context=None):
        proj_ids = self.pool.get('project.task').search(cr, uid, [])
        for task in self.pool.get('project.task').browse(cr, uid, proj_ids):
            task.write({'proj_mgr_usr_id':task.project_id.user_id and task.project_id.user_id.id or False})
        return True         
        
   
        
    _columns = {
        'task_for':fields.selection([('employee','Assignee'),('associate','Associate'),('customer','Client')],'Task For',required=True),
        'billable':fields.boolean('Billable'),
        'assignee_id':fields.many2one('hr.employee','Assigned to(Assignee)'),
        'other_assignee_id':fields.many2one('res.partner','Assigned to(Associate)',domain="[('supplier','=',True)]"),
        'client_id':fields.many2one('res.partner','Assigned to(Client)'),
        'assigned_to':fields.function(_get_assigned_to, string='Assigned to(User)', type='char',store=
            {'project.task': (lambda self, cr, uid, ids, c={}: ids, ['assignee_id','other_assignee_id','client_id'], 20)}),
        #'proj_mgr_usr_id':fields.function(_get_manager_user, string='Project Manager', type='many2one', relation='res.users', store=             {'project.project': (lambda self, cr, uid, ids, c={}: ids, ['user_id'], 20)}),
        'proj_mgr_usr_id':fields.related('project_id','user_id',type='many2one',relation='res.users',string='project Manager',
            store={
                'project.task': (lambda self, cr, uid, ids, c={}: ids, ['project_id'], 10),
                'project.project': (_get_manager_user, ['user_id'], 10),
            }),    
        'name':fields.many2one('task.master','Name',required=True),
        'assignee_user_id': fields.many2one('res.users','Assignee User ID'),
        'project_id': fields.many2one('project.project', 'Project', ondelete='set null', select="1", track_visibility='onchange'),
        'due_days_string':fields.char('Due Days'),
        'due_days':fields.integer('Due Days'),
        'reg_number':fields.function(_get_reg_number,string='Case No.',type='char'),
        'first_parties': fields.function(_get_first_parties, method=True, type='one2many', relation='first.parties.details', string='First parties of the Case'),
        'opp_parties': fields.function(_get_opp_parties, method=True, type='one2many', relation='opp.parties.details', string='Opposite parties of the Case'),
        'bill_amount':fields.function(_get_bill_amount,string='Billing Amount',type='float'),
        'today_date':fields.date('Last Updated Date'),
        'flg_message':fields.boolean('Generate mail Message', track_visibility='always'),
        'state': fields.related('stage_id', 'state', type="selection", store=True,
                selection=_TASK_STATE, string="Status", readonly=True,
                help='The status is set to \'Draft\', when a case is created.\
                      If the case is in progress the status is set to \'Open\'.\
                      When the case is over, the status is set to \'Done\'.\
                      If the case needs to be reviewed then the status is \
                      set to \'Pending\'.', track_visibility='always'),
        'lot_name': fields.char('Lot Number', size=64, readonly=True),

    }
    

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        
        if context.get('order_by_end_date', False):
            order = 'date_end desc'
#             cr.execute("select project_id from case_sheet where division_id in (select id from hr_department where exclude_dashboard=True) and active=True;")
#             project_ids= [a[0] for a in map(lambda x: x, cr.fetchall())]
#             
#             cr.execute('select id from project_task where project_id in %s;',(tuple(project_ids),))
#             tasks_ids = [a[0] for a in map(lambda x: x, cr.fetchall())]
#             args += [('id','not in', tasks_ids)]
        return super(project_task, self).search(cr, uid, args, offset, limit, order, context, count)
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        for task_line in self.browse(cr, uid, ids, context=context):
            res.append((task_line.id,task_line.name.name))
        return res
    
    # Starting // Sanal Davis // 4-6-15
    def project_task_reevaluate(self, cr, uid, ids, context=None):
        '''
         Set warning for invoiced task if we press reevaluate button
        '''
        task = self.browse(cr, uid, ids[0])
        fixed_price_stages_pool = self.pool.get('fixed.price.stages')
        caseids = self.pool.get('case.sheet').search(cr, uid, [('project_id','=',task.project_id.id)])
        if len(caseids)>0:
            case = self.pool.get('case.sheet').browse(cr, uid, caseids[0])
            for line in case.tasks_lines:
                if line.task_id.id == task.id:
                    fixed_price_stages_id = fixed_price_stages_pool.search(cr, uid, [('name','=',line.id)])
                    for item in fixed_price_stages_pool.browse(cr, uid, fixed_price_stages_id):
                        if item.invoiced:
                            raise openerp.exceptions.Warning(_('Billed task Cannot be reactivate'))
        return super(project_task, self).project_task_reevaluate(cr, uid, ids,  context=context) 
        #Ending
           
    def write(self, cr, uid, ids, vals, context=None):
        stage = False
                    
        if vals.has_key('stage_id'):
            task = self.browse(cr, uid, ids[0])
            if task.state == 'done':
                raise openerp.exceptions.Warning(_("You can't change state of already completed task"))
            stage_obj = self.pool.get('project.task.type').browse(cr, uid, vals['stage_id'])
            stage = stage_obj.name
            if stage_obj.state == 'pending':
                cr.execute('select current_date')
                current_date = cr.fetchone()[0]
                days = (datetime.strptime(current_date, '%Y-%m-%d') - datetime.strptime(task.date_deadline, '%Y-%m-%d')).days
                if days <= 0:
                    raise openerp.exceptions.Warning(_("The Deadline date is not expired yet. so you can't change state to Pending"))
            elif stage_obj.state == 'draft' and task.state == 'open':
                    raise openerp.exceptions.Warning(_("You can't change state to New"))
            
            
            caseids = self.pool.get('case.sheet').search(cr, uid, [('project_id','=',task.project_id.id)])
            if len(caseids)>0:
                case = self.pool.get('case.sheet').browse(cr, uid, caseids[0])
                for line in case.tasks_lines:
                    if line.task_id.id == task.id:
                        #Starting // Sanal Davis // 4-6-15 //  Set warning for invoiced task if we press reevaluate button
                        fixed_price_stages_pool = self.pool.get('fixed.price.stages')
                        fixed_price_stages_id = fixed_price_stages_pool.search(cr, uid, [('name','=',line.id)])
                        for item in fixed_price_stages_pool.browse(cr, uid, fixed_price_stages_id):
                            if item.invoiced:
                                raise openerp.exceptions.Warning(_('Billed task Cannot be reactivate'))
                        # Ending
                        self.pool.get('case.tasks.line').write(cr, uid, [line.id], {'state':stage})
                        
                            
                for line in case.associate_tasks_lines:
                    if line.task_id.id == task.id:
                        self.pool.get('associate.tasks.line').write(cr, uid, [line.id], {'state':stage})
                for line in case.client_tasks_lines:
                    if line.task_id.id == task.id:
                        self.pool.get('client.tasks.line').write(cr, uid, [line.id], {'state':stage})                        
                            
        return super(project_task, self).write(cr, uid, ids, vals, context=context)
        
    def project_task_update_deadline(self, cr, uid, ids, context=None):
        task = self.browse(cr, uid, ids[0])
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'wizard_update_task_deadline_id')
        except ValueError, e:
            view_id = False
        return {
            'name':_("Update Task Deadline"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'project.task.deadline',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'task_id': task.id,
                'date_deadline':task.date_deadline
            }
        }    

class account_analytic_account(osv.osv):
    _inherit = 'account.analytic.account'
    _columns = {
        'task_id': fields.many2one('case.task.line', 'Task Title'),
        'case_id': fields.many2one('case.sheet', 'Case ID'),
        }
account_analytic_account()


def _type_get(self, cr, uid, context=None):
    type = [
        ('case', 'Case Sheet'), 
        ('meeting', 'Meeting'), 
        ('misc', 'Miscellaneous'),
        ('brow', 'Browsing/Handling Mails'),
        ('research', 'Research'),
        ('coordination', 'Coordination'),
        ]
    
    csm = self.pool.get('res.users').has_group(cr, uid, 'legal_e.group_legal_e_client_service_manager')
    if csm:
        type = [
            ('case', 'Case Sheet'),
            ('ex_meeting', 'Existing Client Meeting'),
            ('new_meeting', 'New Client Meeting'),
            ('coordination', 'Coordination'),
            ('billing', 'Billing'),
            ('bill_follow', 'Bill Follow up'),
            ('erp_update', 'ERP Update'),
            ('tele_call', 'Tele Calling'),
            ]
    lawyer = self.pool.get('res.users').has_group(cr, uid, 'legal_e.group_legal_e_lawyers')
    if csm and lawyer:
        type = [
            ('case', 'Case Sheet'),
            ('meeting', 'Meeting'),
            ('misc', 'Miscellaneous'),
            ('ex_meeting', 'Existing Client Meeting'),
            ('new_meeting', 'New Client Meeting'),
            ('coordination', 'Coordination'),
            ('billing', 'Billing'),
            ('bill_follow', 'Bill Follow up'),
            ('erp_update', 'ERP Update'),
            ('tele_call', 'Tele Calling'),
            ('brow', 'Browsing/Handling Mails'),
            ('research', 'Research'),
            ]
    if not csm and not lawyer:
        type = [
            ('case', 'Case Sheet'),
            ('meeting', 'Meeting'),
            ('misc', 'Miscellaneous'),
            ('ex_meeting', 'Existing Client Meeting'),
            ('new_meeting', 'New Client Meeting'),
            ('coordination', 'Coordination'),
            ('billing', 'Billing'),
            ('bill_follow', 'Bill Follow up'),
            ('erp_update', 'ERP Update'),
            ('tele_call', 'Tele Calling'),
            ('brow', 'Browsing/Handling Mails'),
            ('research', 'Research'),
            ]
    
    return type


class hr_analytic_timesheet(osv.osv):
    _inherit = 'hr.analytic.timesheet'
    
    
    def type_get(self, cr, uid, context=None):
        type = [
            ('case', 'Case Sheet'), 
            ('meeting', 'Meeting'), 
            ('misc', 'Miscellaneous'),
            ('brow', 'Browsing/Handling Mails'),
            ('research', 'Research'),
            ('coordination', 'Coordination'),
            ]
        
        csm = self.pool.get('res.users').has_group(cr, uid, 'legal_e.group_legal_e_client_service_manager')
        if csm:
            type = [
                ('case', 'Case Sheet'),
                ('ex_meeting', 'Existing Client Meeting'),
                ('new_meeting', 'New Client Meeting'),
                ('coordination', 'Coordination'),
                ('billing', 'Billing'),
                ('bill_follow', 'Bill Follow up'),
                ('erp_update', 'ERP Update'),
                ('tele_call', 'Tele Calling'),
                ]
        lawyer = self.pool.get('res.users').has_group(cr, uid, 'legal_e.group_legal_e_lawyers')
        if csm and lawyer:
            type = [
                ('case', 'Case Sheet'),
                ('meeting', 'Meeting'),
                ('misc', 'Miscellaneous'),
                ('ex_meeting', 'Existing Client Meeting'),
                ('new_meeting', 'New Client Meeting'),
                ('coordination', 'Coordination'),
                ('billing', 'Billing'),
                ('bill_follow', 'Bill Follow up'),
                ('erp_update', 'ERP Update'),
                ('tele_call', 'Tele Calling'),
                ('brow', 'Browsing/Handling Mails'),
                ('research', 'Research'),
                ]
        if not csm and not lawyer:
            type = [
                ('case', 'Case Sheet'),
                ('meeting', 'Meeting'),
                ('misc', 'Miscellaneous'),
                ('ex_meeting', 'Existing Client Meeting'),
                ('new_meeting', 'New Client Meeting'),
                ('coordination', 'Coordination'),
                ('billing', 'Billing'),
                ('bill_follow', 'Bill Follow up'),
                ('erp_update', 'ERP Update'),
                ('tele_call', 'Tele Calling'),
                ('brow', 'Browsing/Handling Mails'),
                ('research', 'Research'),
                ]
        return type

    _columns = {
        'case_id': fields.many2one('case.sheet', 'Case ID'),
        'court_date': fields.date('Court Proceeding Date'),
        'court_proceed_id': fields.many2one('court.proceedings', 'Proceeding'),
        'start_date': fields.datetime('Start Time'),
        'end_date':  fields.datetime('End Time'),
        'type': fields.selection(type_get, 'Related'),
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        
        'company_address': fields.char('Company Address'),
        'contact_person': fields.char('Contact Person'),
        'designation': fields.char('Designation'),
        'email': fields.char('Email'),
        'landline': fields.char('Landline'),
        'mobile': fields.char('Mobile'),
        'industry_type': fields.char('Type of Industry'),
        'next_date': fields.date('Next Followup Date'),
        }
    
    def _check_date(self, cr, uid, ids):
        for time_obj in self.browse(cr, uid, ids):
            time_sheet_ids = self.search(cr, uid, [('start_date', '<=', time_obj.start_date), ('end_date', '>=', time_obj.end_date), ('user_id', '=', time_obj.user_id.id), ('id', '<>', time_obj.id)])
            if time_sheet_ids:
                return False
        return True
    
    _constraints = [
        (_check_date, 'You can not have 2 timesheet that overlaps on same day!', ['start_date','end_date']),
    ] 
    
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('user_id', False):
            employee_id = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', vals['user_id'])], context=context)
            if employee_id:
                vals['employee_id'] = employee_id[0]
        
        res = super(hr_analytic_timesheet, self).create(cr, uid, vals, context=context)
        
        time_sheet_ids = self.search(cr, uid, [\
            ('user_id', '=', vals['user_id']),\
            ('start_date', '>=', vals['start_date'].split(' ')[0] +  ' 00:00:01'),\
            ('end_date', '<=', vals['end_date'].split(' ')[0] +  ' 11:59:58')
            ], context=context)
        unit_amount = vals['unit_amount']
        for time_obj in self.browse(cr, uid, time_sheet_ids, context=context):
            unit_amount += time_obj.unit_amount
        if unit_amount > 15:
            raise osv.except_osv(_('Warning!'),_('The daily maximum of timesheet duration(15 Hours) has been exceeded!'))
                
        
        
        return res
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals.get('user_id', False):
            employee_id = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', vals['user_id'])], context=context)
            if employee_id:
                vals['employee_id'] = employee_id[0]
        res = super(hr_analytic_timesheet, self).write(cr, uid, ids, vals, context=context)
        
        if vals.get('unit_amount', False):
            for line_obj in self.browse(cr, uid, ids, context=context):
                time_sheet_ids = self.search(cr, uid, [\
                    ('user_id', '=', line_obj.user_id.id),\
                    ('start_date', '>=', line_obj.start_date.split(' ')[0] +  ' 00:00:01'),\
                    ('end_date', '<=', line_obj.end_date.split(' ')[0] +  ' 11:59:58')
                    ])
                unit_amount = line_obj.unit_amount
                for time_obj in self.browse(cr, uid, time_sheet_ids, context=context):
                    unit_amount += time_obj.unit_amount
                if unit_amount > 15:
                    raise osv.except_osv(_('Warning!'),_('The daily maximum of timesheet duration(15 Hours) has been exceeded!'))
                
        return res
    
    
    
    def on_change_date(self, cr, uid, ids, date):
        res = super(hr_analytic_timesheet, self).on_change_date(cr, uid, ids, date)
        if date:
            dt = (datetime.strptime(date, '%Y-%m-%d') + timedelta(days=14)).strftime('%Y-%m-%d')
            current_date = time.strftime('%Y-%m-%d')
            if dt < current_date:
                warning = {
                   'title': _('Error!'),
                   'message' : 'Your are not permitted to create timesheet for that date'
                }
                return {'value': {'date': False}, 'warning': warning}
        return res
    
    def onchange_start_end_date(self, cr, uid, ids, date, start_date, end_date, context=None):
        res = {'value': {'unit_amount': 0.0}}
        if not date or not start_date or not end_date:
            return res
        else:
            start_time = datetime.strptime(str(start_date), '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(str(end_date), '%Y-%m-%d %H:%M:%S')
            
            date1 = start_time.strftime('%Y-%m-%d')
            date2 = end_time.strftime('%Y-%m-%d')
            warning = {
                   'title': _('Error!'),
                   'message' : 'Start time and end time must be in the same date as the record date'
                }
            if date != date1:
                return {'value': {'start_date': False}, 'warning': warning}
            if date != date2:
                return {'value': {'end_date': False}, 'warning': warning}
            time_difference = end_time - start_time
            hour = time_difference.total_seconds() / 60 / 60
            res['value']['unit_amount'] = hour
        return res
    
    def onchange_case_id(self, cr, uid, ids, case_id, court_proceed_id, context=None):
        res = {'value': {'account_id': False}}
        if not case_id:
            res['value']['account_id'] = self._get_default_timesheet_analytic_account(cr, SUPERUSER_ID, context=context)
            return res
        else:
            case_obj = self.pool.get('case.sheet').browse(cr, SUPERUSER_ID, case_id, context=context)
            res['value']['type'] = 'case'
            if court_proceed_id:
             court_obj = self.pool.get('court.proceedings').browse(cr, SUPERUSER_ID, court_proceed_id, context=context)
             if court_obj.case_id.id != case_id:
                res['value']['case_id'] = court_obj.case_id.id
                res['value']['account_id'] = court_obj.case_id.project_id.analytic_account_id.id
                return res
            if case_obj.project_id and case_obj.project_id.analytic_account_id:
                res['value']['account_id'] = case_obj.project_id.analytic_account_id.id
        return res
    
    def onchange_type(self, cr, uid, ids, type, case_id,context=None):
        res = {'value': {'case_id': False}}
        if not type:
            return res
        else:
            res['value']['case_id'] = case_id
            if type == 'misc':
                res['value']['case_id'] = False
                res['value']['account_id'] = self._get_default_timesheet_analytic_account(cr, uid, context=context)
        return res
    
    def onchange_court_proceed_id(self, cr, uid, ids, court_proceed_id, context=None):
        res = {'value': {'case_id': False}}
        if not court_proceed_id:
            return res
        else:
            court_obj = self.pool.get('court.proceedings').browse(cr, uid, court_proceed_id, context=context)
            if court_obj.case_id:
                res['value']['case_id'] = court_obj.case_id.id
        return res
   
hr_analytic_timesheet()


class hr_employee(osv.osv):
    _inherit = 'hr.employee'
   
    
    def update_dept(self, cr, uid, ids, context=None):        
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e', 'wizard_update_emp_dept_id')
        except ValueError, e:
            view_id = False
        return {
            'name':_("Update Employee Department"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'hr.employee.update.dept',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'emp_ids': ids
            }
        }
hr_employee()


class other_expenses(osv.osv):
    _name = 'other.expenses'
    _description = 'Other Expenses'
    
    _columns = {
                'case_id': fields.many2one('case.sheet','File Number'),
                'name':fields.char('Description',size=200),
                'date':fields.date('Date'),
                'amount':fields.float('Amount'),
                'billable':fields.selection([('bill','Billable'),('nobill','Not Billable')],'Billable'),
                'invoiced':fields.boolean('Invoiced ?'),
                'to_whom':fields.char('To Whom?', size=200),
                'old_id':fields.many2one('other.expenses','Old ID'),
                'expense_line_id': fields.many2one('hr.expense.line', 'Expense Line')
                }
        
    
    def copy_data(self, cr, uid, ids, default=None, context=None):
        default = default or {}
        default.update({
            'invoiced':False
            })
        return super(other_expenses, self).copy_data(cr, uid, ids, default, context)
    
    
    def unlink(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.expense_line_id:
                raise osv.except_osv(_('Error!'),_('You cannot delete an Expense Line.This record is associated with HR expense.'))
        
        return super(other_expenses, self).unlink(cr, uid, ids, context=context)
             
             
other_expenses()

# Starting // Sanal Davis //4-6-15
class hr_expense_expense(osv.osv):
    _inherit = 'hr.expense.expense'
    _description = 'HR Expense with case sheet'
    _columns = {
        'case_id': fields.many2one('case.sheet','Case Sheet'), #Add case sheet in HR Expence
        'line_ids': fields.one2many('hr.expense.line', 'expense_id', 'Expense Lines'),
        
        }
    
    
    def default_get(self, cr, uid, fields_list, context=None):
        if not context:
            context = {}
        res = super(hr_expense_expense, self).default_get(cr, uid, fields_list, context=context) 
        if context.has_key('case_id'):        
            res.update({'case_id':context.get('case_id', False)})
        return res  
    
    def expense_accept(self, cr, uid, ids, context=None):     
        res = super(hr_expense_expense, self).expense_accept(cr, uid, ids, context=context)
        for expense_obj in self.browse(cr, uid, ids, context=context):
            if expense_obj.case_id:
                for line_obj in expense_obj.line_ids:
                    vals = {
                        'case_id': expense_obj.case_id.id,
                        'name': line_obj.name,
                        'date': line_obj.date_value,
                        'amount': line_obj.total_amount,
                        'billable': line_obj.is_billable and 'bill' or 'nobill',
                        'to_whom': expense_obj.employee_id.name,
                        'expense_line_id': line_obj.id
                        }
                    self.pool.get('other.expenses').create(cr, uid, vals, context=context)
        return res
    
    
    def action_receipt_create(self, cr, uid, ids, context=None):
        for exp_obj in self.browse(cr, uid, ids, context=context):
            for line_obj in exp_obj.line_ids:
                if not line_obj.account_id:
                    raise osv.except_osv(_('Error!'),_('Please fill accounts in Expense Lines.'))
        
        
        res = super(hr_expense_expense, self).action_receipt_create(cr, uid, ids, context=context)
        for exp_obj in self.browse(cr, uid, ids, context=context):
            if exp_obj.account_move_id:
                self.pool.get('account.move').button_validate(cr, uid, [exp_obj.account_move_id.id], context=context)
        return res
    
    
    def move_line_get_item(self, cr, uid, line, context=None):
        res = {
            'type':'src',
            'name': line.name.split('\n')[0][:64],
            'price_unit':line.unit_amount,
            'quantity':line.unit_quantity,
            'price':line.total_amount,
            'account_id':line.account_id.id,
            'product_id':line.product_id.id,
            'uos_id':line.uom_id.id,
            'account_analytic_id':line.analytic_account.id,
            'case_id': line.expense_id.case_id and line.expense_id.case_id.id or False,
            'office_id': line.expense_id.case_id and line.expense_id.case_id.ho_branch_id.id or False,
            }
        return res
    
    
    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res = super(hr_expense_expense, self).line_get_convert(cr, uid, x, part, date, context=context)
        res.update({
            'case_id': x.get('case_id', False),
            'office_id': x.get('office_id', False),
            })
        return res
    
#     def invoice_pay_employee(self, cr, uid, ids, context=None):
#         if not ids: return []
#         dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account_voucher', 'view_vendor_receipt_dialog_form')
#         exp_obj = self.browse(cr, uid, ids[0], context=context)
#         return {
#             'name':_("Pay Expense"),
#             'view_mode': 'form',
#             'view_id': view_id,
#             'view_type': 'form',
#             'res_model': 'account.voucher',
#             'type': 'ir.actions.act_window',
#             'nodestroy': True,
#             'target': 'new',
#             'domain': '[]',
#             'context': {
#                 'payment_expected_currency': exp_obj.company_id.currency_id.id,
#                 'default_partner_id': self.pool.get('res.partner')._find_accounting_partner(exp_obj.employee_id.user_id.partner_id).id,
#                 'default_amount': exp_obj.amount,
#                 'default_reference': exp_obj.name,
#                 'close_after_process': True,
#                 'invoice_type': 'in_invoice',
#                 'default_type': 'payment',
#                 'type': 'payment'
#             }
#         }
    
hr_expense_expense()


class hr_expense_line(osv.osv):
    _inherit = 'hr.expense.line'
    _columns = {
        'is_billable': fields.boolean('Billable'),
        'account_id': fields.many2one('account.account', 'Account'),
        }
    
    def write(self, cr, uid, ids, vals, context=None):
        if vals:
            for line_obj in self.browse(cr, uid, ids, context=context):
                if line_obj.expense_id.state != 'draft':
                    
                    if line_obj.expense_id.state == 'accepted' and self.pool.get('res.users').has_group(cr, uid, 'account.group_account_manager') \
                         and not vals.get('is_billable', False) and not vals.get('unit_amount', False) and not vals.get('unit_quantity', False):
                        pass
                    else:
                        raise osv.except_osv(_('Warning!'), _('You are not permitted to edit this record.'))
                    
        return super(hr_expense_line, self).write(cr, uid, ids, vals, context=context)
    
hr_expense_line()


class account_move_line(osv.osv):
    _inherit = 'account.move.line'
    _description = 'office in Account move line'
    _columns = {
        'office_id': fields.many2one('ho.branch','Office'), #Add offfice in Account move line
        'case_id': fields.many2one('case.sheet','Case Sheet'), #Add case sheet in Account Move Line
        'department_id': fields.many2one('hr.department', 'Department'),
        'cost_id': fields.related('department_id', 'cost_id', type='many2one', relation='legal.cost.center', string="Cost Center", store=True),
        
        }
account_move_line()
# Ending

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
