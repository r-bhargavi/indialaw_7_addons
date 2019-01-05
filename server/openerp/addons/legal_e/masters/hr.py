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

class hr_employee(osv.osv):
    _inherit = "hr.employee"

    def onchange_user(self, cr, uid, ids, user_id, context=None):
        work_email = False
        if user_id:
            user_obj = self.pool.get('res.users').browse(cr, uid, user_id, context=context)
            address_home_id = (user_obj.partner_id and user_obj.partner_id.id or False)
        return {'value': {'work_email' : work_email,'address_home_id':address_home_id}}    
    
    def onchange_name(self, cr, uid, ids, name, context=None):
        if not name:
            return {'value': {'city_code': False}}
        val = {
            'city_code': (name and len(name)>=3 and name[:3].upper() or False)
        }
        return {'value': val}
    
    _columns = {
        'tds': fields.float('TDS Amount'),
        'pan_id':fields.char('PAN No', size=10),
        'code':fields.char('Code', size=10),
        'date_of_join':fields.date('Date of Joining'),
        'street':fields.related('address_home_id','street',type='char', size=128, string='Street'),
        'street2':fields.related('address_home_id','street2',type='char',size=128, string='Street2'),
        'city':fields.related('address_home_id','city',type='char',size=128, string='City'),
        'state_id':fields.related('address_home_id','state_id',type='many2one',relation='res.country.state',string='State'),
        'zip':fields.related('address_home_id','zip',type='char',size=24, string='Pin'),
        'country_id':fields.related('address_home_id','country_id',type='many2one',relation='res.country',string='Country'),
        'ho_branch_id':fields.many2one('ho.branch','HO Branch', required=True),
        'work_street':fields.char('Street', size=128),
        'work_street2':fields.char('Street2', size=128),
        'work_city':fields.char('City', size=128),
        'work_zip':fields.char('Pin', size=24),
        'work_district_id':fields.many2one('district.district', 'District'),
        'work_state_id':fields.many2one('res.country.state', 'State'),
        'work_country_id':fields.many2one('res.country', 'Country'),
        'office_id': fields.many2one('hr.office', 'Office'),
        #'department_id': fields.many2one('hr.department', 'Department(Subdivision)'),
        'department_type': fields.selection([('legal', 'Legal'),('non_legal', 'Non Legal')],'Department Type'),
        'client_service_admin': fields.boolean('Client Service Admin'),
        'job_id': fields.many2one('hr.job', 'Designation'),
        'parent_id': fields.many2one('hr.employee', 'Reporting Head'),
    }
    
    _sql_constraints = [
        ('code_uniq', 'unique(code)', 'Code must be unique!'),
    ]
                
    def onchange_district(self, cr, uid, ids, district_id, context=None):
        if district_id:
            state_id = self.pool.get('district.district').browse(cr, uid, district_id, context).state_id.id
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'work_country_id':country_id,'work_state_id':state_id}}
        return {}
        
    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'work_country_id':country_id}}
        return {}        
        
    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.has_key('address_home_id') and vals['address_home_id']:
            self.pool.get('res.partner').write(cr, uid, [vals['address_home_id']], {'street':vals.get('street',False), 'street2':vals.get('street2',False), 'city':vals.get('city',False), 'state_id':vals.get('state_id',False), 'zip':vals.get('zip',False), 'country_id':vals.get('country_id',False)})
        vals['code'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.employee') 
        retvals = super(hr_employee, self).create(cr, uid, vals, context=context) 
        return retvals
        
#     
#     def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
#         if not args:
#             args = []
#         if context is None:
#             context = {}
#         ids = []
#         employee_ids = []
#         if name:
#             if context.get('dept_employes', False):
#                 dept_obj = self.pool.get('hr.department').browse(cr, user, context['dept_employes'], context=context)
#                 employee_ids = [dept.id for dept in dept_obj.employee_ids]
#                 args += [('id', 'in', employee_ids)]
#                 
#                 ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
#             else:
#                 ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
#         if not ids:
#             if employee_ids:
#                 ids = employee_ids
#             else:
#                 ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
#         return self.name_get(cr, user, ids, context)
#     
#     def search(self, cr, uid, args, offset=0, limit=None, order=None,
#             context=None, count=False):
#         if context is None:
#             context = {}
#         print '...........................',context
#         if context.get('dept_employes', False):
#             dept_obj = self.pool.get('hr.department').browse(cr, uid, context['dept_employes'], context=context)
#             return [dept.id for dept in dept_obj.employee_ids]
#                 
#         return super(hr_employee, self).search(cr, uid, args, offset, limit,
#                 order, context=context, count=count)
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        if context.get('dept_manager', False):
            dept_obj = self.pool.get('hr.department').browse(cr, uid, context['dept_manager'], context=context)
            employee_ids = [dept_obj.manager_id.id]
            args += [('id', 'in', employee_ids)]
            
        if context.get('dept_employes', False):
            dept_obj = self.pool.get('hr.department').browse(cr, uid, context['dept_employes'], context=context)
            employee_ids = [emp.id for emp in dept_obj.employee_ids]
            args += [('id', 'in', employee_ids)]
        
        return super(hr_employee, self).name_search(
            cr, uid, name, args, operator=operator, context=context, limit=limit)
    
hr_employee()


class hr_office(osv.osv):
    _description="HR Office"
    _name = 'hr.office'
    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'state_id':fields.many2one('res.country.state','State', required=True),
        'parent_office':fields.many2one('hr.office','Parent Office'),
        }
    
hr_office()

class hr_department(osv.osv):
    _inherit = "hr.department"
    _columns = {
        'office_id':fields.many2one('ho.branch','Office'),    
        'litigation': fields.boolean('Litigation'),
        'non_litigation': fields.boolean('Non Litigation'),
        'function_head': fields.many2one('hr.employee','Function Head'),
        'reporting_head': fields.many2one('hr.employee','Reporting Head'),
        #'legal': fields.boolean('Legal'),
        #'non_legal': fields.boolean('Non Legal'),
        'type': fields.selection([('legal', 'Legal'),('non_legal', 'Non Legal')],'Type'),
        # Add Type of work in hr department // Sanal Davis // 5-6-15
        'work_type':fields.selection([('civillitigation', 'Civil Litigation'),('criminallitigation', 'Criminal Litigation'), ('non_litigation', 'Non Litigation'), ('arbitration', 'Arbitration'),('execution', 'Execution'),('mediation', 'Mediation')], 'Type of Work', track_visibility='onchange'),
        'employee_ids': fields.many2many('hr.employee', 'employee_department_rel', 'emp_id', 'dept_id', 'Employees'),
        'child_id': fields.one2many('hr.department', 'parent_id', string='Child Departments'),
        
        'exclude_dashboard': fields.boolean('Exclude From Dashboard'),
        'cost_id': fields.many2one('legal.cost.center', 'Cost Center')
        }
    
    
#     def get_parent_records(self, cr, uid, ids, grp_id, context=None):
#         res = []     
#         grp_obj = self.pool.get('res.groups')
#         grp = grp_obj.browse(cr, uid, grp_id)
#         if grp.implied_ids:
#             for parent_grp in grp.implied_ids:
#                 res.append(parent_grp.id)            
#                 if parent_grp.implied_ids:
#                     parent_ids = self.get_parent_records(cr, uid, ids, parent_grp.id)
#                     for parent_id in parent_ids:
#                         res.append(parent_id)
#         return res
    
    def get_parent_records(self, cr, uid, dep_obj, res, context=None): 
        if not res:
            res = [] 
        if dep_obj.parent_id:
                res.append(dep_obj.parent_id.id)            
                if dep_obj.parent_id.parent_id:
                    res.append(dep_obj.parent_id.parent_id.id)
                    self.get_parent_records(cr, uid, dep_obj.parent_id.parent_id, res, context=context)
        return res
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
#             if record['parent_id']:
#                 name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res
        
hr_department()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: