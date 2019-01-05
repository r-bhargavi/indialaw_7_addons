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
from openerp.osv import fields, osv


class court_diary(osv.osv_memory):
    parent_id = False
    _name = "court.diary"
    _description = "Court Diary Details"

    _columns = {
        'name': fields.many2one('case.sheet', 'File Number'),
#         'client_id':fields.many2one('res.partner','Client Name'),
        'from_date':fields.date('From date'),
        'to_date':fields.date('To Date'),
        'date_filter':fields.selection([('=','is equal to'),('!=','is not equal to'),('>','greater than'),('<','less than'),('>=','greater than or equal to'),('<=','less than or equal to'),('between','between')],'Proceed Date'),
        'next_from_date':fields.date('From date'),
        'next_to_date':fields.date('To Date'),
        'next_date_filter':fields.selection([('=','is equal to'),('!=','is not equal to'),('>','greater than'),('<','less than'),('>=','greater than or equal to'),('<=','less than or equal to'),('between','between'),('missing','IS MISSING')],'Next Proceed Date'),
        'court_proceed_lines': fields.many2many('court.proceedings', 'court_diary_line_ids', 'diary_id', 'proceeding_id', 'Court History'),
        'missing_date':  fields.boolean('Missing Dates'),
        'office_id': fields.many2one('ho.branch', 'Office'),
        'state_id': fields.many2one('res.country.state', 'State'),
        'client_service_manager_id': fields.many2one('hr.employee','Client Relationship Manager'),
        'last_smt': fields.boolean('Last Proceeding Only'),
        
        'assignee_id': fields.many2one('hr.employee','Assignee'),
        'division_id':fields.many2one('hr.department', 'Department/Division'),
        'client_ids':  fields.many2many('res.partner', 'client_missing_diary_rel', 'client_id', 'court_diary_id', 'Clients')
        
            
        
    }
    _defaults = {
        'from_date':lambda *a: time.strftime('%Y-%m-%d'),
        'to_date':lambda *a: time.strftime('%Y-%m-%d'),
        'next_from_date':lambda *a: time.strftime('%Y-%m-%d'),
        'next_to_date':lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def default_get(self, cr, uid, fields_list, context=None):
        if not context:
            context = {}
        self.parent_id = False    
        res = super(court_diary, self).default_get(cr, uid, fields_list, context=context)
        return res
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return ['COURT_HISTORY']
        for task_line in self.browse(cr, uid, ids, context=context):
            res.append((task_line.id,'COURT HISTORY'))
        return res
    
    def filter_proceedings(self, cr, uid, ids, context=None):
        procee_pool = self.pool.get('court.proceedings')
        filters = []
        self.parent_id = ids[0]
        if context.has_key('case_id') and context['case_id']!=False:
            filters.append(('case_id','=',context['case_id']))
        if context.get('client_ids', False) and context['client_ids'][0][2]:
            filters.append(('client_id','in', context['client_ids'][0][2])) 
        if context.has_key('date_filter') and context['date_filter']!=False:
            if context['date_filter']!='between':
                filters.append(('proceed_date',context['date_filter'],context['proceed_from_date'])) 
            else:
                filters.append(('proceed_date','>',context['proceed_from_date']))     
                filters.append(('proceed_date','<',context['proceed_to_date']))     
        if context.has_key('next_date_filter') and context['next_date_filter']!=False:
            filters.append(('flg_next_date','=',True))
            if context['next_date_filter']=='missing':
                filters.append(('next_proceed_date','=',False))                  
            elif context['next_date_filter']!='between':
                filters.append(('next_proceed_date',context['next_date_filter'],context['next_proceed_from_date'])) 
            else:
                filters.append(('next_proceed_date','>',context['next_proceed_from_date']))     
                filters.append(('next_proceed_date','<',context['next_proceed_to_date']))
        if context.get('missing_date', False):
            filters.append(('date_missing','=', True))
        if context.get('office_id', False):
            filters.append(('case_id.ho_branch_id','=', context['office_id']))
        if context.get('state_id', False):
            filters.append(('case_id.state_id','=', context['state_id']))
            
        if context.get('assignee_id', False):
            filters.append(('case_id.assignee_id','=', context['assignee_id']))
        
        if context.get('division_id', False):
            filters.append(('case_id.division_id','=', context['division_id']))
        
        if context.get('client_service_manager_id', False):
            filters.append(('case_id.client_service_manager_id','=', context['client_service_manager_id']))
                  
        data_ids = procee_pool.search(cr, uid, filters, order='proceed_date desc',context=context)
        if context.get('last_smt', False):
            case_ids = [proce_obj.case_id.id for proce_obj in procee_pool.browse(cr, uid, data_ids, context=context)]
            case_ids = list(set(case_ids))
            proceed_ids = []
            for case_id in case_ids:
                proc_ids =  procee_pool.search(cr, uid, [('case_id', '=', case_id)], order='proceed_date desc', context=context)
                proceed_ids.append(proc_ids[0])
            return self.write(cr, uid, ids, {'court_proceed_lines':[(6, 0, proceed_ids)]})
        return self.write(cr, uid, ids, {'court_proceed_lines':[(6, 0, data_ids)]})
    
    def clear_filters(self, cr, uid, ids, context=None):
        res={}
        res['name'] = False
        res['client_id'] = False
        res['date_filter'] = False
        res['from_date'] = time.strftime('%Y-%m-%d')
        res['to_date'] = time.strftime('%Y-%m-%d')
        res['next_date_filter'] = False
        res['next_from_date'] = time.strftime('%Y-%m-%d')
        res['next_to_date'] = time.strftime('%Y-%m-%d')
        res['client_service_manager_id'] = False
        res['state_id'] = False
        res['office_id'] = False
        res['date_missing'] = False
        res['last_smt'] = False
        return self.write(cr, uid, ids, res)
            
    def clear_filters_all(self, cr, uid, ids, context=None):
        res={}
        res['name'] = False
        res['client_id'] = False
        res['date_filter'] = False
        res['from_date'] = time.strftime('%Y-%m-%d')
        res['to_date'] = time.strftime('%Y-%m-%d')
        res['next_date_filter'] = False
        res['next_from_date'] = time.strftime('%Y-%m-%d')
        res['next_to_date'] = time.strftime('%Y-%m-%d')
        res['client_service_manager_id'] = False
        res['state_id'] = False
        res['office_id'] = False
        res['date_missing'] = False
        res['last_smt'] = False
        cr.execute('delete from court_diary_line_ids')
        return self.write(cr, uid, ids, res)
        
                     
    def get_ids(self, cr, uid):
        ret = []
        if self.parent_id:
            for line in self.browse(cr, uid, self.parent_id).court_proceed_lines:
                ret.append(str(line.id))
        return {"ids":ret}

court_diary()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: