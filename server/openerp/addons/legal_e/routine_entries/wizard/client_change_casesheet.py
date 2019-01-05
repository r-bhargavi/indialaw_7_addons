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

class client_change_casesheet(osv.osv):

    _name = "client.change.casesheet"
    _description = "Client Change for Casesheet's"

    _columns = {
        'name': fields.many2one('res.partner','Client Name'),
        'change_client_id': fields.many2one('res.partner','Client Name'),
        'contact_partner1_id': fields.many2one('res.partner','Contact Person 1'),
        'contact_partner2_id': fields.many2one('res.partner','Contact Person 2'),
    
        'date':fields.date('Date'),
        'ho_branch_id':fields.many2one('ho.branch','Location'),
        'company_ref_no':fields.char('Client Ref #',size=40, track_visibility='onchange'),
        'our_client':fields.selection([('first','First Party'),('opposite','Opposite Party')],'Side'),
        'client_service_executive_id': fields.many2one('hr.employee','Client Service Admin'),
        'client_service_manager_id': fields.many2one('hr.employee','Client Relationship Manager'),
        'state_id':fields.many2one('res.country.state', string='State'),
        'district_id':fields.many2one('district.district', 'Assignee District'),
        'group_val':fields.selection([('individual','INDIVIDUAL'),('proprietary','PROPRIETARY'),('company','COMPANY'),('firm','FIRM'),('llp','LLP'),('trust','TRUST'),('bank','BANK'),('others','OTHERS')],'Group'),
        'division_id':fields.many2one('hr.department', 'Department/Division'),
        'work_type':fields.selection([('civillitigation', 'Civil Litigation'),('criminallitigation', 'Criminal Litigation'), ('non_litigation', 'Non Litigation'), ('arbitration', 'Arbitration'),('execution', 'Execution'),('mediation', 'Mediation')], 'Type of Work'),
        'casetype_id': fields.many2one('case.master','Case Type'),
        'court_district_id': fields.many2one('district.district','Court District'),
        'court_location_id': fields.many2one('court.location','Court Location'),
        'court_id': fields.many2one('court.master','Court Name'),
        'arbitrator_id': fields.many2one('arbitrator.master','Arbitrator'),
        'mediator_id': fields.many2one('mediator.master','Mediator'),
        'lodging_number':fields.char('Lodging Number'),
        'lodging_date':fields.date('Lodging Date'),
        'reg_number':fields.char('Case No.'),
        'reg_date':fields.date('Case Date'),
        'lot_name': fields.char('Lot Number'),
        
    
    	'change_case_sheet_ids':fields.many2many('case.sheet','case_change_new_client_rel', 'change_id','case_id','File Numbers to change Client'),
    	'change_case_sheet_office_ids':fields.many2many('case.sheet','case_change_new_client_office_rel', 'change_office_id','case_id','File Numbers to change Client'),
        
        'flg_change':fields.boolean('Button Change Clicked?'),
        'office_id': fields.many2one('ho.branch','Office'),
        'filter': fields.selection([('client', 'Client'), ('office', 'Office')], 'Filter Based On')
    }
    _defaults = {
        'flg_change':False,
        'filter': 'client',
    }
    
    def update_project_details(self, cr, uid, ids, case, from_id, to_id, context=None):
        task_pool = self.pool.get('project.task')
        members = [(4, to_id.user_id.id)]
        tasks_ids = task_pool.search(cr, uid, [('project_id','=',case.project_id.id), ('state','!=','done')], context=context)
        if from_id:
            members.append((3, from_id.user_id.id))
            for task_obj in task_pool.browse(cr, uid, tasks_ids, context=context):
                if task_obj.user_id.id == from_id.user_id.id:
                    task_pool.write(cr, uid, [task_obj.id], {'user_id': to_id.user_id.id}, context=context)
            
            for line_obj in case.tasks_lines:
                if line_obj.assign_to.id == from_id.id:
                    self.pool.get('case.tasks.line').write(cr, uid, [line_obj.id], {'assign_to': to_id.id}, context=context)
        
        if from_id == to_id:
            project_mem = [mem.id for mem in case.project_id.members]
            case_mem = [mem.id for mem in case.members]
            if to_id not in project_mem and to_id not in case_mem: 
                if (3, from_id.user_id.id) in  members:
                    members.remove((3, from_id.user_id.id))
                    
        self.pool.get('project.project').write(cr, uid, [case.project_id.id], {'members': members}, context=context)
        self.pool.get('case.sheet').write(cr, uid, [case.id], {'members': members}, context=context)
        
        return True
    
    
    def change_casesheet_client(self, cr, uid, ids, context=None):
        
        for line in self.browse(cr, uid, ids):
            line.write({'flg_change':True})
            # For Each Case selected in the List
            change_case_sheet_ids = False
            if line.filter == 'client':
                change_case_sheet_ids = line.change_case_sheet_ids
            else:
                change_case_sheet_ids = line.change_case_sheet_office_ids
                
            for case in change_case_sheet_ids:
                #Change the Client for Not Completed Client tasks
                for task in case.client_tasks_lines:
                    if task.state in ('New','In Progress','Pending'): # and task.assign_to_in_client == line.name
                        task.write({'assign_to_in_client':line.change_client_id.id})
                #Change the Client and Contact in Case Sheets
                vals = {}
                if line.change_client_id:
                    if case.client_id == line.name:
                        vals.update({'client_id': line.change_client_id.id})
                        
                        self.pool.get('project.project').write(cr, uid, [case.project_id.id], {'partner_id': line.change_client_id.id}, context=context)
                        tasks_ids = self.pool.get('project.task').search(cr, uid, [('project_id','=',case.project_id.id), ('state','!=','done')], context=context)
                        self.pool.get('project.task').write(cr, uid, tasks_ids, {'partner_id': line.change_client_id.id}, context=context)
                
                if  line.contact_partner1_id:
                    vals.update({'contact_partner1_id': line.contact_partner1_id.id})
                    
                if  line.contact_partner2_id:
                    vals.update({'contact_partner2_id': line.contact_partner2_id.id})
                    
                if  line.date:
                    vals.update({'date': line.date})
                    
                if  line.ho_branch_id:
                    vals.update({'ho_branch_id': line.ho_branch_id.id})
                    
                if  line.company_ref_no:
                    vals.update({'company_ref_no': line.company_ref_no})
                    
                if  line.our_client:
                    vals.update({'our_client': line.our_client})
                    
                if  line.client_service_executive_id:
                    vals.update({'client_service_executive_id': line.client_service_executive_id.id})
                    self.update_project_details(cr, uid, ids, case, case.client_service_executive_id, line.client_service_executive_id, context)
                    
                if  line.client_service_manager_id:
                    vals.update({'client_service_manager_id': line.client_service_manager_id.id})
                    self.update_project_details(cr, uid, ids, case, case.client_service_manager_id, line.client_service_manager_id, context)
                        
                if  line.state_id:
                    vals.update({'state_id': line.state_id.id})
                    
                if  line.district_id:
                    vals.update({'district_id': line.district_id.id})
                    
                if  line.group_val:
                    vals.update({'group_val': line.group_val})
                    
                if  line.division_id:
                    vals.update({'division_id': line.division_id.id})
                    
                if  line.work_type:
                    vals.update({'work_type': line.work_type})
                    
                if  line.casetype_id:
                    vals.update({'casetype_id': line.casetype_id.id})
                    
                if  line.court_district_id:
                    vals.update({'court_district_id': line.court_district_id.id})
                    
                if  line.court_location_id:
                    vals.update({'court_location_id': line.court_location_id.id})
                    
                if  line.court_id:
                    vals.update({'court_id': line.court_id.id})   
                    
                if  line.arbitrator_id:
                    vals.update({'arbitrator_id': line.arbitrator_id.id})
                    
                if  line.mediator_id:
                    vals.update({'mediator_id': line.mediator_id.id})    
                    
                if  line.lodging_number:
                    vals.update({'lodging_number': line.lodging_number}) 
                      
                if  line.lodging_date:
                    vals.update({'lodging_date': line.lodging_date})   
                     
                if  line.reg_number:
                    vals.update({'reg_number': line.reg_number})  
                      
                if  line.reg_date:
                    vals.update({'reg_date': line.reg_date}) 
                       
                if  line.lot_name:
                    vals.update({'lot_name': line.lot_name})   
                         
                case.write(vals)
        return True
    
client_change_casesheet()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: