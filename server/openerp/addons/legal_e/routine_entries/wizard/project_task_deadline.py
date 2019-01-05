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

class project_task_deadline(osv.osv):

    _name = "project.task.deadline"
    _description = "Project Task Deadline Change"

    _columns = {
        'name': fields.text('Reason'),
        'new_date_deadline':fields.date('New Deadline Date'),
        'date_deadline':fields.date('Current Deadline Date'),
        'state':fields.selection([('new','Waiting for Approval'),('approve','Approved')],'State'),
        'task_id':fields.many2one('project.task','Task'),
        'project_id':fields.related('task_id','project_id',type='many2one',relation='project.project',string='Project',store=True),
    }
    _defaults = {
        'state':'new',        
    }
    
    def create_record(self, cr, uid, ids, context=None):
        return True

    def create(self, cr, uid, vals, context=None):
        vals['task_id'] = context.has_key('task_id') and context['task_id'] or False
        vals['date_deadline'] = context.has_key('date_deadline') and context['date_deadline'] or False
        if context.has_key('task_id') and context['task_id']:
            task = self.pool.get('project.task').browse(cr, uid, context['task_id'])
            searids = self.pool.get('case.tasks.line').search(cr, uid, [('task_id','=',task.id)])
            start_date = False
            if len(searids):
                start_date = self.pool.get('case.tasks.line').browse(cr, uid, searids[0]).start_date
            else:
                searids = self.pool.get('associate.tasks.line').search(cr, uid, [('task_id','=',task.id)])
                if len(searids):
                    start_date = self.pool.get('case.tasks.line').browse(cr, uid, searids[0]).start_date
            if start_date:
                if vals['new_date_deadline']<start_date:
                    raise osv.except_osv(_('Error'),_('New Deadline date should be Greater than/ Equal to Start date in the Case Sheet ' + str(start_date)))
                
        return super(project_task_deadline, self).create(cr, uid, vals, context=context)

            
    def update_date_deadline(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
            self.pool.get('project.task').write(cr, uid, obj.task_id.id, {'date_deadline':obj.new_date_deadline})            
            task = self.pool.get('project.task').browse(cr, uid, obj.task_id.id)
            searids = self.pool.get('case.tasks.line').search(cr, uid, [('task_id','=',task.id)])
            if len(searids):
                self.pool.get('case.tasks.line').write(cr, uid, searids, {'planned_completion_date':obj.new_date_deadline})
                self.pool.get('case.tasks.line').update_days(cr, uid, searids, context=context)
            else:
                searids = self.pool.get('associate.tasks.line').search(cr, uid, [('task_id','=',task.id)])
                if len(searids):
                    self.pool.get('case.tasks.line').write(cr, uid, searids, {'planned_completion_date':obj.new_date_deadline})
            self.pool.get('project.task.deadline').write(cr, uid, [obj.id], {'state':'approve'})

project_task_deadline()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: