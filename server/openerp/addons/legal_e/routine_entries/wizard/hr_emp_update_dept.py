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


class hr_emp_update_dept(osv.osv):

    _name = "hr.employee.update.dept"
    _description = "Update the Department of the Employee"

    _columns = {
        'new_dept_id': fields.many2one('hr.department', 'New Department'),
        'sub_emp_id':fields.many2one('hr.employee','Substitute Employee'),
        'name':fields.selection([('transfer','Transfer Dept'), ('resign','Resigned')], 'Type'),
    }
    
    def update_emp_dept(self, cr, uid, ids, context=None):
        emp = self.pool.get('hr.employee').browse(cr, uid, context['active_id'])
        sub_emp = self.pool.get('hr.employee').browse(cr, uid, context['sub_emp_id'])
        
        if context['type']=='transfer' and emp.department_id and emp.department_id.id == context['new_dept_id']:
            return True
        #To Update the Emp with Substitute Employee in Project and Task
        if emp.user_id:
            proj_ids = self.pool.get('project.project').search(cr, uid, [('state','in',('draft','open')),('user_id','=',emp.user_id.id)])
            for proj in self.pool.get('project.project').browse(cr, uid, proj_ids):
                if sub_emp.user_id:
                    try:
                        proj.write({'user_id': sub_emp.user_id.id})
                    except Exception:
                        self.pool.get('account.analytic.account').write(cr, uid, [proj.analytic_account_id.id], {'user_id': sub_emp.user_id.id}, context=context)
            
                    
        #To Update the Project Team with Substitute Employee
        if emp.user_id:
            proj_ids = self.pool.get('project.project').search(cr, uid, [('state','in',('draft','open')), ('members','=', emp.user_id.id)])
            for proj in self.pool.get('project.project').browse(cr, uid, proj_ids):
                proj.write({'members':[(3, emp.user_id.id)]})
                if sub_emp.user_id:
                    proj.write({'members':[(4, sub_emp.user_id.id)]})
                    
            case_ids = self.pool.get('case.sheet').search(cr, uid, [('members','=', emp.user_id.id), ('state','=','inprogress')])
            for case in self.pool.get('case.sheet').browse(cr, uid, case_ids):
                case.write({'members':[(3, emp.user_id.id)]})
                if sub_emp.user_id:
                    case.write({'members':[(4, sub_emp.user_id.id)]}) 
                    
        #To Update the Employee to his New Department Not Completed Projects
        if emp.user_id and context['type'] == 'transfer':
            case_ids = self.pool.get('case.sheet').search(cr, uid, [('division_id','=',context['new_dept_id']), ('state','=','inprogress'), ('project_id','!=', False)])
            for case in self.pool.get('case.sheet').browse(cr, uid, case_ids):
                case.project_id.write({'members':[(4, emp.user_id.id)]})
                case.write({'members':[(4, emp.user_id.id)]})                   
        
        #To Replace the Assigned To with Substitute Employee in Assignee Tasks
        case_task_ids = self.pool.get('case.tasks.line').search(cr, uid, [('task_id.state','in',('draft', 'open', 'pending')),('assign_to','=',context['active_id'])])
        for task in self.pool.get('case.tasks.line').browse(cr, uid, case_task_ids):
            task.write({'assign_to': context['sub_emp_id']}) 
        
        #To Replace the Assignee with Substitute Employee in Case Sheet
        case_ids = self.pool.get('case.sheet').search(cr, uid, [('state','in',('new','inprogress')),('assignee_id','=',context['active_id'])])
        for case in self.pool.get('case.sheet').browse(cr, uid, case_ids):
            case.write({'assignee_id': context['sub_emp_id']})
        
        #To Update the Department of the Employee
        if context['type'] == 'transfer':
            self.pool.get('hr.employee').write(cr, uid, [context['active_id']], {'department_id':context['new_dept_id']})
            self.pool.get('hr.employee').onchange_department_id(cr, uid, [context['active_id']], context['new_dept_id'])
        elif context['type'] == 'resign':
            self.pool.get('hr.employee').write(cr, uid, [context['active_id']], {'active':False})
        
        return True    
hr_emp_update_dept()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: