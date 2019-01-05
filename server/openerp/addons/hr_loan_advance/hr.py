# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 ZestyBeanz Technologies Pvt. Ltd.
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

from osv import fields, osv
import time
import datetime

class hr_employee_advance(osv.osv):
    _name = "hr.employee.advance"
    _description = "Employee Advances"
    _columns = {
        'name': fields.many2one('hr.employee', "Employee",required=True),
        'date': fields.date("Date"),
        'amount': fields.float("Amount"),
        'description': fields.char("Description", size=64)
        }
    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d')
        }
    
hr_employee_advance()


class hr_employee_loan(osv.osv):
    _name = "hr.employee.loan"
    _description = "Employee Loan"
    _order= 'start_date'
    
    def _calc_bal(self, cr, uid, ids, name, args, context=None):
        res = {}
        for loan in self.read(cr, uid, ids, ['amount'], context=context):
            res[loan['id']] = loan['amount']
            cr.execute("SELECT sum(amount) FROM hr_employee_loan_trn WHERE loan_id=%s"%(loan['id']))
            res[loan['id']]-=(cr.fetchone()[0] or 0.0)
        return res
     
    def _calc_last_trn(self, cr, uid, ids, name, args, context=None):
        res = {}
        for loan in self.read(cr, uid, ids, ['id'], context=context):
            cr.execute("SELECT max(date) FROM hr_employee_loan_trn WHERE loan_id=%s"%(loan['id']))
            res[loan['id']] =cr.fetchone()[0]
        return res
     
    def _get_loan_trn(self, cr, uid, ids, context=None):
        result = {}
        for trn in self.pool.get('hr.employee.loan.trn').browse(cr, uid, ids, context=context):
            result[trn.loan_id.id] = True
        return result.keys()
     
    _columns = {
        'name': fields.many2one('hr.employee', "Employee",required=True),
        'start_date': fields.date("Start Date",required=True),
        'amount': fields.float("Amount"),
        'monthly_payment': fields.integer('Monthly Payment'),
        'description': fields.char("Description", size=64),
        'tran_ids':  fields.one2many('hr.employee.loan.trn', 'loan_id', 'Payments'),
        'balance_amount': fields.function(_calc_bal, string='Balance', readonly=True,
            type='float', store={
                'hr.employee.loan': (lambda self, cr, uid, ids, c={}: ids, ['amount','tran_ids'], 20),
                'hr.employee.loan.trn': (_get_loan_trn, None, 20),
            }),
        'last_trn_date': fields.function(_calc_last_trn, string='Last Trns. Date', readonly=True,
            type='date', store={
                'hr.employee.loan': (lambda self, cr, uid, ids, c={}: ids, ['tran_ids'], 20),
                'hr.employee.loan.trn': (_get_loan_trn, None, 20),
            }),
        }
    _defaults = {
        'start_date': lambda *a: time.strftime('%Y-%m-%d'),
        }
         
    def create_loan_trn_for_payslip(self, cr, uid, employee_id, start_date, end_date, payslip_id):
        loan_trn_obj= self.pool.get('hr.employee.loan.trn')
        loan_ids= self.search(cr, uid, [('name', '=', employee_id), ('balance_amount', '>', 0),
                        ('start_date','<', start_date)], order= 'start_date')
        if not loan_ids:
            return True
        cr.execute("select max(monthly_payment), sum(balance_amount) from \
            hr_employee_loan where id in %s", (tuple(loan_ids),))
        monthly_payment,balance_amount= cr.fetchone()
        check_amount= min(balance_amount,monthly_payment)
        for loan in self.read(cr, uid, loan_ids, ['balance_amount']):
            trn_ids= loan_trn_obj.search(cr, uid, [('loan_id', '=', loan['id']),
                                        ('date', '>=', start_date), ('date', '<=', end_date)])
            if not trn_ids:
                description= 'Payment for '+datetime.datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %Y')
                amount= min(loan['balance_amount'], check_amount)
                check_amount-=amount
                loan_trn_obj.create(cr, uid, {'name': description, 'loan_id': loan['id'],
                                    'amount': amount, 'date': end_date, 'payslip_id': payslip_id})
            if check_amount<=0: 
                return True
        return True
    
hr_employee_loan()


class hr_employee_loan_trn(osv.osv):
    _name = "hr.employee.loan.trn"
    _description = "Loan Payments"
    _columns = {
        'name': fields.char("Description", size=64),
        'loan_id': fields.many2one('hr.employee.loan', "Loan",required=True),
        'date': fields.date("Date",required=True),
        'amount': fields.float("Amount"),
        'payslip_id': fields.many2one('hr.payslip', 'Payslip', readonly=True),
        }
    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d'),
        }
    
    def compute_loan_on_payslip(self, cr, uid, ids, context={}):
        payslip_ids=[]
        for loan_trn in self.browse(cr, uid, ids, context=context):
            if loan_trn.payslip_id: 
                payslip_ids.append(loan_trn.payslip_id.id)
        return payslip_ids
    
    def create(self, cr, uid, vals, context=None):
        res= super(hr_employee_loan_trn, self).create(cr, uid, vals, context=context)
        slip_ids= self.compute_loan_on_payslip(cr, uid, [res], context)
        if slip_ids: 
            self.pool.get('hr.payslip').compute_sheet(cr, uid, slip_ids)
        return res
    
hr_employee_loan_trn()


class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'    
    
    def _get_advance(self, cr, uid, ids, name, args, context=None):
        result = {}
        advance = self.pool.get('hr.employee.advance')
        amount = 0
        for slip in self.browse(cr, uid, ids, context=context):
            result[slip.id] = 0.0
            advance_ids = advance.search(cr, uid, [('name', '=', slip.employee_id.id), ('date', '>=', slip.date_from),
                                                    ('date', '<=', slip.date_to)], context=context)
            if advance_ids:
                advance_objs = advance.browse(cr, uid, advance_ids, context=context)
                for advance_obj in advance_objs:
                    amount += advance_obj.amount
                result[slip.id] = amount
        return result
    
    def _get_loan(self, cr, uid, ids, name, args, context=None):
        result = {}
        for payslip in self.browse(cr, uid, ids, context=context):
            slip= self.read(cr, uid, payslip.id, ['employee_id', 'date_from', 'date_to'])
            cr.execute("SELECT sum(amount) FROM hr_employee_loan_trn WHERE payslip_id = %s AND \
                date>='%s' AND date<='%s' AND loan_id in (SELECT id FROM hr_employee_loan WHERE \
                name = %s)"%(payslip.id, slip['date_from'], slip['date_to'],slip['employee_id'][0],))
            loan_amount= cr.fetchone()
            loan_amount= loan_amount and loan_amount[0] or 0
            result[payslip.id] = loan_amount
        return result
    
    _columns = {
        'advance': fields.function(_get_advance, method=True, type='float', string='Advance', store=True),
        'loan': fields.function(_get_loan, method=True, type='float', string='Loan', store=True),
        }
    
    def compute_sheet(self, cr, uid, ids, context=None):
        slip = self.browse(cr, uid, ids[0],context=context)
        self.pool.get('hr.employee.loan').create_loan_trn_for_payslip(cr, uid, slip.employee_id.id, slip.date_from, slip.date_to, slip.id)
        res = super(hr_payslip, self).compute_sheet(cr, uid, ids, context)
        return res
        
hr_payslip()  

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
