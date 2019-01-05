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
from datetime import timedelta,datetime
from openerp.osv import fields, osv
from openerp import netsvc

class reset_emp_leaves(osv.osv_memory):

    _name = "reset.emp.leaves"
    _description = "To Reset the Employees Leaves"

    _columns = {
        'name': fields.many2one('hr.holidays.status','Leave Type'),
        'employee_ids':fields.many2many('hr.employee', 'reset_emp_leave_rel', 'reset_id','employee_id',
            'Employees'),
    }
    _defaults = {
    }
    def reset_leaves(self, cr, uid, ids, context=None):
        holi_status_obj = self.pool.get('hr.holidays.status')
        cr.execute("select employee_id,max(date_to) from hr_holidays where flg_reset_leaves=true group by employee_id")
        rest = cr.dictfetchall()
        max_dates = {}
        for r in rest:
            max_dates[r['employee_id']] = r['max']
        if context.has_key('leave_type') and context['leave_type']:
            for emp in self.pool.get('hr.employee').browse(cr, uid, context['employee_ids'][0][2]):
                leaves_rest = holi_status_obj.get_days( cr, uid, [context['leave_type']], emp.id, False)[context['leave_type']]['remaining_leaves']
                
                context['employee_id'] = emp.id    
                start_dt = '1900-01-01 00:00:01'
                end_dt = '1900-01-01 00:00:01'
                if max_dates.has_key(emp.id):
                    start_dt = (datetime.strptime(max_dates[emp.id], '%Y-%m-%d %H:%M:%S') + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                end_dt = (datetime.strptime(start_dt, '%Y-%m-%d %H:%M:%S') + timedelta(days=leaves_rest)).strftime('%Y-%m-%d %H:%M:%S')
                
                if leaves_rest>0:
                    leave_id = self.pool.get('hr.holidays').create(cr, uid, {'name':'To Reset the Leaves', 'holiday_type':'employee', 'holiday_status_id':context['leave_type'], 'employee_id':emp.id, 'number_of_days_temp':leaves_rest, 'date_from': start_dt, 'date_to': end_dt,'flg_reset_leaves':True}, context=context)
                    wf_service = netsvc.LocalService("workflow")
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                    wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        else:
            leave_type_ids = self.pool.get('hr.holidays.status').search(cr, uid, ['|',('active','=',True),('active','=',False)])
            for leave_type in self.pool.get('hr.holidays.status').browse(cr, uid, leave_type_ids):
                cr.execute("select employee_id,max(date_to) from hr_holidays where flg_reset_leaves=true group by employee_id")
                rest = cr.dictfetchall()
                max_dates = {}
                for r in rest:
                    max_dates[r['employee_id']] = r['max']
                for emp in self.pool.get('hr.employee').browse(cr, uid, context['employee_ids'][0][2]):
                    leaves_rest = holi_status_obj.get_days( cr, uid, [leave_type.id], emp.id, False)[leave_type.id]['remaining_leaves']
                
                    context['employee_id'] = emp.id    
                    start_dt = '1900-01-01 00:00:01'
                    end_dt = '1900-01-01 00:00:01'
                    if max_dates.has_key(emp.id):
                        start_dt = (datetime.strptime(max_dates[emp.id], '%Y-%m-%d %H:%M:%S') + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
                    end_dt = (datetime.strptime(start_dt, '%Y-%m-%d %H:%M:%S') + timedelta(days=leaves_rest)).strftime('%Y-%m-%d %H:%M:%S')
                
                    if leaves_rest>0:
                        leave_id = self.pool.get('hr.holidays').create(cr, uid, {'name':'To Reset the Leaves', 'holiday_type':'employee', 'holiday_status_id':leave_type.id, 'employee_id':emp.id, 'number_of_days_temp':leaves_rest, 'date_from': start_dt, 'date_to': end_dt,'flg_reset_leaves':True}, context=context)
                        wf_service = netsvc.LocalService("workflow")
                        wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'confirm', cr)
                        wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'validate', cr)
                        wf_service.trg_validate(uid, 'hr.holidays', leave_id, 'second_validate', cr)
        return True
reset_emp_leaves()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: