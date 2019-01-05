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

class work_summary(osv.osv_memory):

    _name = "work.summary"
    _description = "Work Summary Report"

    _columns = {
        'name':fields.many2one('res.partner','Client Name'),
        'case_id':fields.many2one('case.sheet','File Number'),
        'state':fields.selection([('new','New'), ('inprogress','In Progress'), ('cancel','Cancelled'), ('transfer','Transferred'), ('done','Closed'), ('hold','Hold')],'Case State'),
        'ho_branch_id':fields.many2one('ho.branch','Location'),
        'assignee_id': fields.many2one('hr.employee','Assignee'),
        'other_assignee_id':fields.many2one('res.partner','Other Associate'),
        'division_id':fields.many2one('hr.department', 'Department/Division'),
        'work_type':fields.selection([('civillitigation', 'Civil Litigation'),('criminallitigation', 'Criminal Litigation'), ('non_litigation', 'Non Litigation'), ('arbitration', 'Arbitration'),('execution', 'Execution'),('mediation', 'Mediation')], 'Type of Work'),
        'casetype_id': fields.many2one('case.master','Case Type'),
        'contact_partner1_id': fields.many2one('res.partner','Contact Person 1'),
    	'contact_partner2_id': fields.many2one('res.partner','Contact Person 2'),
    	'company_ref_no':fields.char('Client Ref #',size=40),
    	'reg_number':fields.char('Case No.'),
    	'court_district_id': fields.many2one('district.district','Court District'),
    	'court_location_id': fields.many2one('court.location','Court Location'),
    	'court_id': fields.many2one('court.master','Court Name'),
    	'parent_id_manager':fields.many2one('hr.employee', "Manager"),
    	'bill_type':fields.selection([('fixed_price','Fixed Price'),('assignment_wise','Assignment Wise')],'Billing Type'),
    	'first_party_name':fields.char('First Party name'),
    	'oppo_party_name':fields.char('Opposite Party name'),
        'case_lines': fields.many2many('case.sheet', 'work_summary_lines', 'summary_id', 'case_id', 'Case Sheets'),
    }
    _defaults = {
    }
    
    def filter_proceedings(self, cr, uid, ids, context=None):
        filters = []
        if context.has_key('case_id') and context['case_id']!=False:
            filters.append(('id','=',context['case_id']))
        if context.has_key('client_id') and context['client_id']!=False:
            filters.append(('client_id','=',context['client_id']))
        if context.has_key('state') and context['state']!=False:
            filters.append(('state','=',context['state']))
        if context.has_key('ho_branch_id') and context['ho_branch_id']!=False:
            filters.append(('ho_branch_id','=',context['ho_branch_id']))
        if context.has_key('assignee_id') and context['assignee_id']!=False:
            filters.append(('assignee_id','=',context['assignee_id']))
        if context.has_key('other_assignee_id') and context['other_assignee_id']!=False:
            filters.append(('other_assignee_ids.name','=',context['other_assignee_id']))
        if context.has_key('division_id') and context['division_id']!=False:
            filters.append(('division_id','=',context['division_id']))
        if context.has_key('work_type') and context['work_type']!=False:
            filters.append(('work_type','=',context['work_type']))
        if context.has_key('casetype_id') and context['casetype_id']!=False:
            filters.append(('casetype_id','=',context['casetype_id']))
        if context.has_key('contact_partner1_id') and context['contact_partner1_id']!=False:
            filters.append(('contact_partner1_id','=',context['contact_partner1_id']))
        if context.has_key('contact_partner2_id') and context['contact_partner2_id']!=False:
            filters.append(('contact_partner2_id','=',context['contact_partner2_id']))
        if context.has_key('company_ref_no') and context['company_ref_no']!=False:
            filters.append(('company_ref_no','ilike',context['company_ref_no']))
        if context.has_key('reg_number') and context['reg_number']!=False:
            filters.append(('reg_number','ilike',context['reg_number']))
        if context.has_key('court_district_id') and context['court_district_id']!=False:
            filters.append(('court_district_id','=',context['court_district_id']))
        if context.has_key('court_location_id') and context['court_location_id']!=False:
            filters.append(('court_location_id','=',context['court_location_id']))
        if context.has_key('court_id') and context['court_id']!=False:
            filters.append(('court_id','=',context['court_id']))
        if context.has_key('parent_id_manager') and context['parent_id_manager']!=False:
            filters.append(('assignee_id.parent_id','=',context['parent_id_manager']))
        if context.has_key('bill_type') and context['bill_type']!=False:
            filters.append(('bill_type','=',context['bill_type']))
        if context.has_key('first_party_name') and context['first_party_name']!=False:
            filters.append(('first_parties.name','ilike',context['first_party_name']))
        if context.has_key('oppo_party_name') and context['oppo_party_name']!=False:
            filters.append(('opp_parties.name','ilike',context['oppo_party_name']))
                  
        data_ids = self.pool.get('case.sheet').search(cr, uid, filters)
        return self.write(cr, uid, ids, {'case_lines':[(6, 0, data_ids)]})
        return True
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return ['Work Summary']
        for task_line in self.browse(cr, uid, ids, context=context):
            res.append((task_line.id,'Work Summary'))
        return res
    
   
    def generate_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        data['client_id'] = context['client_id']
        data['case_id'] = context['case_id']
        datas = {
             'ids': [],
             'model': 'case.sheet',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'work.summary',
            'datas': datas,
            'nodestroy': True,
            'name':'Work Summary'
            }	
    
    def clear_filters(self, cr, uid, ids, context=None):
        res={}
        res['name'] = False
        res['case_id'] = False
        res['state'] =False
        res['ho_branch_id'] = False
        res['assignee_id'] = False
        res['other_assignee_id'] = False
        res['division_id'] = False
        res['work_type'] = False
        res['casetype_id'] = False
        res['contact_partner1_id'] = False
        res['contact_partner2_id'] = False
        res['company_ref_no'] = False
        res['reg_number'] = False
        res['court_district_id'] = False
        res['court_location_id'] = False
        res['court_id'] = False
        res['parent_id_manager'] = False
        res['bill_type'] = False
        res['first_party_name'] = False
        res['oppo_party_name'] = False
        return self.write(cr, uid, ids, res)
            
    def clear_filters_all(self, cr, uid, ids, context=None):
        res={}
        self.clear_filters(cr, uid, ids, context)
        cr.execute('delete from work_summary_lines')
        return self.write(cr, uid, ids, res)

work_summary()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: