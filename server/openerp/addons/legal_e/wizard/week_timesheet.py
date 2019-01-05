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
import datetime
from openerp.osv import fields, osv

class week_timesheet(osv.osv_memory):

    _name = "week.timesheet"
    _description = "Week Timesheet Report"

    _columns = {
        'name':fields.many2one('hr.employee','Employee'),
        'year': fields.integer('Year'),
        'from_date':fields.date('From date'),
        'to_date':fields.date('To Date'),
        'date_filter':fields.selection([('=','is equal to'),('!=','is not equal to'),('>','greater than'),('<','less than'),('>=','greater than or equal to'),('<=','less than or equal to'),('between','between')],'Date'),
    }
    
    def _get_user(self, cr, uid, context=None):
        emp_obj = self.pool.get('hr.employee')
        emp_id = emp_obj.search(cr, uid, [('user_id', '=', uid)], context=context)
        if not emp_id:
            raise osv.except_osv(_("Warning!"), _("Please define employee for this user!"))
        return emp_id and emp_id[0] or False
    
    _defaults = {
        'year': lambda *a: datetime.date.today().year,
        'from_date':lambda *a: time.strftime('%Y-%m-%d'),
        'to_date':lambda *a: time.strftime('%Y-%m-%d'),
        'date_filter':'between',
        'name': _get_user
             }
    
    def filter_proceedings(self, cr, uid, ids, context=None):
        filters = []
        if context.has_key('case_id') and context['case_id']!=False:
            filters.append(('id','=',context['case_id']))
        if context.has_key('client_id') and context['client_id']!=False:
            filters.append(('client_id','=',context['client_id']))
                  
        data_ids = self.pool.get('case.sheet').search(cr, uid, filters)
        return self.write(cr, uid, ids, {'case_lines':[(6, 0, data_ids)]})
        return True
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return ['Week Timesheet']
        for task_line in self.browse(cr, uid, ids, context=context):
            res.append((task_line.id,'Week Timesheet'))
        return res
        
    
    def generate_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        data['employee_id'] = context['employee_id']
        data['date_filter'] = context['date_filter']
        data['from_date'] = context['from_date']
        data['to_date'] = context['to_date']
        datas = {
             'ids': [],
             'model': 'hr_timesheet_sheet.sheet',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'week.timesheet',
            'datas': datas,
            'nodestroy': True,
            'name':'Weekly Timesheet'
            }	
    def clear_filters(self, cr, uid, ids, context=None):
        res={}
        res['name'] = False
        res['case_id'] = False
        return self.write(cr, uid, ids, res)
            
    def clear_filters_all(self, cr, uid, ids, context=None):
        res={}
        res['name'] = False
        res['case_id'] = False
        cr.execute('delete from work_summary_lines')
        return self.write(cr, uid, ids, res)

week_timesheet()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: