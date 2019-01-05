# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 ZestyBeanz Technologies Pvt Ltd(<http://www.zbeanztech.com>).
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
from datetime import timedelta

from osv import osv, fields
from openerp.tools.translate import _

class hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"
    _description = "Leave Type"
    
    _columns = {
        'unpaid': fields.boolean('Unpaid'),
        }

hr_holidays_status()


class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'

    _columns = {
        'mobile_expense': fields.float('Mobile Expenses'),
        'train_pass': fields.float('Train Pass'),
        'travel_expense': fields.float('Travelling Expenses'),
        'incentives': fields.float('Incentives'),
        'arrears': fields.float('Arrears'),
        'tax': fields.float('Prof.Tax'),
#         'loan': fields.float('Loan'),
#         'advance': fields.float('Salary Advance'),
    }
    
    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day, context=None):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
            if holiday_ids:
                res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id
            return res
 
        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            if not contract.working_hours:
                #fill only if the contract as a working schedule linked
                continue
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            leaves = overtime = unpaid_leaves = {}
            overtime_hours = 0
            overtime_ids = []
            holiday_ids = []
            unpaid_days = unpaid_hours = 0
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                datetime_day = day_from + timedelta(days=day)
                day1 = datetime_day.strftime("%Y-%m-%d")
                overtime_ids += self.pool.get('hr.overtime').search(cr, uid, [('state','=','validate'),('employee_id','=',contract.employee_id.id),('date_from','<=',day1),('date_to','>=',day1)])
                holiday_ids += self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',contract.employee_id.id),('type','=','remove'),('date_from','<=',day1),('date_to','>=',day1)])
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                if working_hours_on_day:
                    #the employee had to work
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    if leave_type:
                        #if he was on leave, fill the leaves dict
                        if leave_type in leaves:
                            leaves[leave_type]['number_of_days'] += 1.0
                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        else:
                            leaves[leave_type] = {
                                'name': leave_type.name,
                                'sequence': 5,
                                'code': leave_type.name,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            }
                    else:
                        #add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day
                        
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + leaves
            if overtime_ids:
                overtime_ids = list(set(overtime_ids))
                overtime_objs = self.pool.get('hr.overtime').browse(cr, uid, overtime_ids, context=context)
                for overtime_obj in overtime_objs:
                    overtime_hours += overtime_obj.number_of_hours_temp
            if overtime_hours != 0:
                overtime = {
                        'name': 'Overtime',
                        'sequence': 2,
                        'code': 'OT',
                        'number_of_days': 0.0,
                        'number_of_hours': overtime_hours,
                        'contract_id': contract.id,
                    }
                res += [overtime]
            if holiday_ids:
                holiday_ids = list(set(holiday_ids))
                holiday_objs = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)
                for holiday_obj in holiday_objs:
                    if holiday_obj.holiday_status_id.unpaid:
                        unpaid_days += holiday_obj.number_of_days_temp
            if unpaid_days > 0:
                unpaid_leaves = {
                     'name': 'Absent Days',
                     'sequence': 3,
                     'code': 'Absent',
                     'number_of_days': unpaid_days,
                     'number_of_hours': unpaid_hours,
                     'contract_id': contract.id,
                     }
                res += [unpaid_leaves]
        return res
    
hr_payslip()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: