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
from osv import osv, fields
from openerp.tools.translate import _


class hr_attendance(osv.osv):
    _inherit = 'hr.attendance'

    
    def close_signout(self, cr, uid, ids, context=None):
        attendance_pool = self.pool.get('hr.attendance')
        emp_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '!=', False)], context=context)
        for emp_id in emp_ids:
            ids_signin = attendance_pool.search(cr,uid,[('action','=','sign_in'),('employee_id', '=', emp_id)], context=context)
            ids_signout = attendance_pool.search(cr,uid,[('action','=','sign_out'),('employee_id', '=', emp_id)], context=context)
            if len(ids_signin) != len(ids_signout):
                    attendance_obj = attendance_pool.browse(cr, uid, ids_signin[0], context=context)
                    date = attendance_obj.name.split(' ')
                    name = date[0] + ' 23:00:00'
                    if not ids_signout or ids_signin[0] > ids_signout[0]:
                        if not attendance_obj.sheet_id:
                            vals = {
                                'employee_id': emp_id,
                                'name': name,
                                'action': 'sign_out',
                                }
                            attendance_pool.create(cr, uid, vals, context=context)
                        else:
                             cr.execute('insert into hr_attendance (employee_id, name, action, sheet_id) values (%s, %s, %s, %s);',(emp_id, name, 'sign_out', attendance_obj.sheet_id.id))
        return True
    
    
    def automatic_signout_scheduler(self, cr, uid, context=None):
        attendance_pool = self.pool.get('hr.attendance')
        emp_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '!=', False)], context=context)
        for emp_id in emp_ids:
            ids_signin = attendance_pool.search(cr,uid,[('name', '>=', time.strftime('%Y-%m-%d') + ' 00:00:01'),('name', '<=', time.strftime('%Y-%m-%d') + ' 23:59:59'),('action','=','sign_in'),('employee_id', '=', emp_id)], context=context)
            ids_signout = attendance_pool.search(cr,uid,[('name', '>=', time.strftime('%Y-%m-%d') + ' 00:00:01'),('name', '<=', time.strftime('%Y-%m-%d') + ' 23:59:59'),('action','=','sign_out'),('employee_id', '=', emp_id)], context=context)
            if len(ids_signin) != len(ids_signout):
                if not ids_signout or ids_signin[0] > ids_signout[0]:
                    vals = {
                        'employee_id': emp_id,
                        'name': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'action': 'sign_out',
                        }
                    attendance_pool.create(cr, uid, vals, context=context)
        
        return True 


hr_attendance()


class legal_hr_attendance(osv.osv):
    _name = 'legal.hr.attendance'
    _rec_name = 'employee_id'
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee'),
        'office_id': fields.many2one('ho.branch', 'Branch'),
        'dom': fields.float('DOM'),
        'day_present': fields.float('Days Present'),
        'absent': fields.float('Absent'),
        'comp_off': fields.float('Comp Off'),
        'comp_off_balance': fields.float('Comp Off Balance'),
        'late_mark': fields.float('Late Mark'),
        'leave_balance': fields.float('Leave Balance'),
        'leave_availed': fields.float('Leave Availed'),
        'leave_remain': fields.float('Leave Remaining'),
        'ot_hour': fields.float('OT Hours'),
        'date_from': fields.date('Date From'),
        'date_to': fields.date('Date To'),
        }
     
legal_hr_attendance()    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: