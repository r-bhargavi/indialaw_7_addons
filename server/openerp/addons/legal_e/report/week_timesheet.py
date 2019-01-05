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
import math
from datetime import datetime
from openerp.report import report_sxw
from openerp.osv import orm


class week_timesheet_report(report_sxw.rml_parse):
    _name = 'report.week.timesheet'
    def __init__(self, cr, uid, name, context=None):
        super(week_timesheet_report, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'datetime':datetime,
            'get_data':self.get_data,
            'get_employee_details':self.get_employee_details,
        })
        
    def get_employee_details(self, data, option):
        context = data['form']
        selection = {'=':'is equal to','!=':'is not equal to','>':'greater than','<':'less than','>=':'greater than or equal to','<=':'less than or equal to','between':'between'}
        emp = self.pool.get('hr.employee').browse(self.cr, self.uid, context['employee_id'])
        if option == 'name':
            return emp.name
        elif option == 'head':
            return emp.parent_id and emp.parent_id.name or ''
        elif option == 'sheet':
            if context['date_filter'] == 'between':
                return datetime.strptime(context['from_date'],'%Y-%m-%d').strftime('%d/%m/%Y') + ' - ' + datetime.strptime(context['to_date'],'%Y-%m-%d').strftime('%d/%m/%Y')
            else:
                return selection[context['date_filter']] + ' ' + datetime.strptime(context['from_date'],'%Y-%m-%d').strftime('%d/%m/%Y')
        
    def filter_string(self, context):
        filters = []
        if context.has_key('employee_id') and context['employee_id']!=False:
            filters.append(('sheet_id.employee_id','=',context['employee_id']))
        if context.has_key('date_filter') and context['date_filter']!=False:
            if context['date_filter']!='between':
                filters.append(('date',context['date_filter'],context['from_date'])) 
            else:
                filters.append(('date','>=',context['from_date']))     
                filters.append(('date','<=',context['to_date']))
        return filters
        
        
    def get_data(self, data):
        try:
            filters = self.filter_string(data['form'])
            search_ids = self.pool.get('hr.analytic.timesheet').search(self.cr, self.uid, filters)
            ret_datas = []
            
            if len(search_ids):
                for data in self.pool.get('hr.analytic.timesheet').browse(self.cr, self.uid, search_ids): 
                        ret_data = {}
                        proj_ids = self.pool.get('project.project').search(self.cr, self.uid, [('analytic_account_id', '=', data.account_id.id)])
                        file_number = False
                        if len(proj_ids):
                            case_ids = self.pool.get('case.sheet').search(self.cr, self.uid, [('project_id','=',proj_ids[0])])
                            if len(case_ids):
                                case = self.pool.get('case.sheet').browse(self.cr, self.uid, case_ids[0])
                                file_number = case.name
                                ret_data['date'] = datetime.strptime(data.date,'%Y-%m-%d').strftime('%A %d/%m/%y')
                                ret_data['file_number'] = file_number
                                ret_data['client'] = case.client_id.name
                                ret_data['description'] = data.name
                                ret_data['from_time'] = str(int(data.from_time))+':'+str(int(math.floor((data.from_time  % 1) * 60)))
                                ret_data['to_time'] = str(int(data.to_time))+':'+str(int(math.floor((data.to_time  % 1) * 60)))
                                ret_data['hours'] = str(int(data.unit_amount))+':'+str(int(math.floor((data.unit_amount  % 1) * 60)))
                                ret_datas.append(ret_data)    
                        else:
                            ret_data['date'] = datetime.strptime(data.date,'%Y-%m-%d').strftime('%A %d/%m/%y')
                            ret_data['file_number'] = ''
                            ret_data['client'] = ''
                            ret_data['description'] = data.name
                            ret_data['from_time'] = str(int(data.from_time))+':'+str(int(math.floor((data.from_time  % 1) * 60)))
                            ret_data['to_time'] = str(int(data.to_time))+':'+str(int(math.floor((data.to_time  % 1) * 60)))
                            ret_data['hours'] = str(int(data.unit_amount))+':'+str(int(math.floor((data.unit_amount  % 1) * 60)))
                            ret_datas.append(ret_data) 
            return ret_datas
        except NameError:
                raise orm.except_orm(_(''),
                     _('No Data To Generate Report'))
                     
    def format_date(self, hours):
        return datetime.strptime(str(hours), '%H.%S').strftime('%H:%S')
        
    
report_sxw.report_sxw('report.week.timesheet', 'hr_timesheet_sheet.sheet', 'addons/legal_e/report/week_timesheet_view.rml', parser=week_timesheet_report, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: