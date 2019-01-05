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


class add_employee(osv.osv_memory):
    _name = "legale.add.employee"
    _description = "Add Employees"

    _columns = {
        'type': fields.selection([('add','Add'),('remove','Remove')],'Type'),
        'employee_ids': fields.many2many('hr.employee', 'add_employee_dept', 'dept_id', 'employee_id', 'Employees'),
        'remo_employee_id': fields.many2one('hr.employee', 'Employee'),
        'new_employee_id': fields.many2one('hr.employee', ' New Employee'),
        'dept_id': fields.many2one('hr.department', 'Department')
        }
    _defaults = {
        'type': 'add',
        }
    
    def update_add_remove_dept(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
            
        active_ids = context.get('active_ids', False)
        case_pool = self.pool.get('case.sheet')
        department_pool = self.pool.get('hr.department')
        project_pool = self.pool.get('project.project')
        for data_obj in self.browse(cr, uid, ids, context=context):
            case_ids = case_pool.search(cr, uid, [('division_id', '=', active_ids[0]), ('state','not in',['done','cancel'])], context=context)
                
            if data_obj.type == 'add':
                user_ids = []
                employee_ids = []
                if data_obj.employee_ids:
                    for emp_obj in data_obj.employee_ids:
                        employee_ids.append((4, emp_obj.id))
                        user_ids.append((4, emp_obj.user_id.id))
                for case_obj in case_pool.browse(cr, uid, case_ids, context=context):
                    if case_obj.project_id:
                        project_pool.write(cr, uid, [case_obj.project_id.id], {'members': user_ids}, context=context)
                        case_pool.write(cr, uid, [case_obj.id], {'members': user_ids}, context=context)
                department_pool.write(cr, uid, active_ids, {'employee_ids':employee_ids}, context=context)
            else:
                user_ids = [(3, data_obj.remo_employee_id.user_id.id)]
                employee_ids = [(3, data_obj.remo_employee_id.id)]
                if data_obj.new_employee_id:
                    user_ids += [(4, data_obj.new_employee_id.user_id.id)]
                    employee_ids += [(4, data_obj.new_employee_id.id)]
                for case_obj in self.pool.get('case.sheet').browse(cr, uid, case_ids, context=context):
                    if case_obj.project_id:
                        project_pool.write(cr, uid, [case_obj.project_id.id], {'members': user_ids}, context=context)
                        case_pool.write(cr, uid, [case_obj.id], {'members': user_ids}, context=context)
                        for line_obj in case_obj.tasks_lines:
                            if not data_obj.new_employee_id and line_obj.assign_to.id == data_obj.remo_employee_id.id:
                                raise osv.except_osv(_('Error!'), _("This employee already have tasks assigned in %s matter !\n\n Please add 'New Employee' in the update wizard."% case_obj.name))
                            if data_obj.new_employee_id and line_obj.assign_to.id == data_obj.remo_employee_id.id and line_obj.task_id and line_obj.task_id.state != 'done':
                                self.pool.get('case.tasks.line').write(cr, uid, [line_obj.id], {'assign_to': data_obj.new_employee_id.id}, context=context)
                
                department_pool.write(cr, uid, active_ids, {'employee_ids': employee_ids}, context=context)
                
                
            
        return True

add_employee()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: