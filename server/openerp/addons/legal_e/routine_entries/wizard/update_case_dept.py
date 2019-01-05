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


class update_case_dept(osv.osv_memory):

    _name = "update.case.dept"
    _description = "Update Case sheet Department"

    _columns = {
        'assignee_id': fields.many2one('hr.employee','Assignee'),
        'office_id':fields.many2one('ho.branch','Office'),
        'dept_id': fields.many2one('hr.department', 'Department'),
        'new_assignee_id':fields.many2one('hr.employee','New Assignee'),
        'task_assignee_id':fields.many2one('hr.employee','New Task Assignee'),
        'case_ids': fields.many2many('case.sheet', 'case_sheet_update_dept', 'case_id', 'update_id', 'Case Sheet'),
        'partner_id': fields.many2one('res.partner', 'Client')
        }
    
    def onchange_new_assignee_id(self, cr, uid, ids, new_assignee_id, context=None):
        if new_assignee_id:
            return {'value': {'task_assignee_id': new_assignee_id}}
        return {'value': {'task_assignee_id':False}}
    
    def onchange_office_id(self, cr, uid, ids, office_id, context=None):
        return {'value': {'dept_id': False}}
    
    
    def update_project_details(self, cr, uid, ids, data, case_ids, assignee_id, task_assignee_id, context=None):
        task_pool = self.pool.get('project.task')
        for case_obj in self.pool.get('case.sheet').browse(cr, uid, case_ids, context=context):
            if case_obj.project_id:
                try:
                    self.pool.get('project.project').write(cr, uid, [case_obj.project_id.id], {'user_id': assignee_id.user_id.id, 'members':[(4, assignee_id.user_id.id),(4, task_assignee_id.user_id.id),(3, data.assignee_id.user_id.id)]}, context=context)
                    self.pool.get('case.sheet').write(cr, uid, [case_obj.id], {'members':[(4, assignee_id.user_id.id),(4, task_assignee_id.user_id.id),(3, data.assignee_id.user_id.id)]}, context=context)
                except Exception:
                    self.pool.get('project.project').write(cr, uid, [case_obj.project_id.id], {'members':[(4, assignee_id.user_id.id),(4, task_assignee_id.user_id.id),(3, data.assignee_id.user_id.id)]}, context=context)
                    self.pool.get('case.sheet').write(cr, uid, [case_obj.id], {'members':[(4, assignee_id.user_id.id),(4, task_assignee_id.user_id.id),(3, data.assignee_id.user_id.id)]}, context=context)
                    self.pool.get('account.analytic.account').write(cr, uid, [case_obj.project_id.analytic_account_id.id], {'user_id': assignee_id.user_id.id}, context=context)
            for line_obj in case_obj.tasks_lines:
                if line_obj.assign_to.id == data.assignee_id.id and line_obj.task_id and line_obj.task_id.state != 'done':
                    self.pool.get('case.tasks.line').write(cr, uid, [line_obj.id], {'assign_to': task_assignee_id.id}, context=context)
        return True
    
    
    def update_emp_dept(self, cr, uid, ids, context=None):
        case_pool = self.pool.get('case.sheet')
        for data in self.browse(cr, uid, ids, context=context):
            case_ids = [case.id for case in data.case_ids]
            self.update_project_details(cr, uid, ids, data, case_ids, data.new_assignee_id, data.task_assignee_id,context=context)
            case_pool.write(cr, uid, case_ids, {'assignee_id': data.new_assignee_id.id}, context=context)
            
#             case_div_ids = case_pool.search(cr, uid, [('division_id','=',data.dept_id.id), ('state','not in',['done','cancel']), ('id', 'not in', case_ids)], context=context)
#             self.update_project_details(cr, uid, ids, data, case_div_ids, data.task_assignee_id, context=context)
            
        return True
      
update_case_dept()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: