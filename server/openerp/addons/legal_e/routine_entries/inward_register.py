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
from openerp import SUPERUSER_ID

class inward_register(osv.osv):
    
    _name = 'inward.register'
    _description = 'Inward Register'
    _inherit = ['mail.thread','ir.needaction_mixin']
    
    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result

    def _data_set(self, cr, uid, id, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
        file_size = len(value.decode('base64'))
        if location:
            attach = self.browse(cr, uid, id, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            fname = self._file_write(cr, uid, location, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(inward_register, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(inward_register, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
        
    def _get_related_tasks(self, cr, uid, context=None):        
        return (('0','Select...'))
        
    def _get_employees(self, cr, uid, context=None):
        if context is None:
            context = {}
        emps = self.pool.get('hr.employee').search(cr, uid, [])        
        usrs = self.pool.get('hr.employee').read(cr, uid, emps, ['user_id'])
        users = []
        for usr in usrs: 
            if usr['user_id']:
                users.append(usr['user_id'][0])
        parts = self.pool.get('res.users').read(cr, uid, users, ['partner_id'])
        partners = []
        for part in parts:            
            partners.append(part['partner_id'][0])
        partner_obj = self.pool.get('res.partner')
        return partner_obj.name_get(cr, uid, partners, context) + [(False, '')]
        
    def _get_location(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('case.sheet').browse(cr, uid, ids, context=context):
            for court in line.court_proceedings:
                result[court.id] = line.ho_branch_id.id
        return result.keys()
        
    def _get_default_ho_branch(self, cr, uid, context=None):
        emps = self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])
        if len(emps):
            emp = self.pool.get('hr.employee').browse(cr, uid, emps[0])
            if emp.ho_branch_id:
                return emp.ho_branch_id.id
        return False            
    
    _columns = {
    		'name': fields.char('Entry Number', size=64, required=False, readonly=False, select=True),
    		'date':fields.date('Entry Date'),
    		'file_number':fields.many2one('case.sheet','File Number'),
    		'our_ref_no':fields.char('Our Ref. Number',size=128),
    		'their_number':fields.char('Their Number',size=128),
    		'inward_date':fields.date('Inward Date'),
    		'agency_from':fields.many2one('res.partner','Agency From'),
    		'priority':fields.selection([('low','Low'),('medium','Medium'),('high','High')],'Priority'),
    		'assignee_id':fields.many2one('hr.employee','Assignee',readonly=True),
    		'material_code':fields.char('Material ID',readonly=True),
    		'material_id':fields.many2one('material.master', 'Material Title'),
    		'task_present':fields.boolean('Task Present'),
    		'assign_date':fields.date('Assign Date'),
    		'filing_date':fields.date('Filing Date'),
    		'exec_date':fields.date('Execution Date'),
    		'remarks':fields.text('Remarks'),
    		'task_date':fields.date('Task Date'),
    		'task_id':fields.many2one('case.tasks.line','Related Task'),
    		'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
    		'datas_fname': fields.char('File Name',size=256),
    		'store_fname': fields.char('Stored Filename', size=256),
        	'db_datas': fields.binary('Database Data'),
        	'file_size': fields.integer('File Size'),
        	'attach_id': fields.many2one('ir.attachment','Attachment ID'),
        	'addressee_name':fields.selection(_get_employees,'Given To',size=-1),
            'ho_branch_id':fields.many2one('ho.branch','Location'),
        }
        
    _defaults = {
    	'date':lambda *a: time.strftime('%Y-%m-%d'),
    	'inward_date':lambda *a: time.strftime('%Y-%m-%d'),
    	'assign_date':lambda *a: time.strftime('%Y-%m-%d'),
    	'filing_date':lambda *a: time.strftime('%Y-%m-%d'),
    	'exec_date':lambda *a: time.strftime('%Y-%m-%d'),
    	'task_date':lambda *a: time.strftime('%Y-%m-%d'),
    	'ho_branch_id':lambda s, cr, uid, c:s._get_default_ho_branch(cr, uid, c),
    }
    
    _order = 'name desc, date desc'
    
    def default_get(self, cr, uid, fields_list, context=None):
        if not context:
            context = {}
        res = super(inward_register, self).default_get(cr, uid, fields_list, context=context)
        return res
        
    def onchange_file_number(self, cr, uid, ids, fileno, context=None):
        res = {}
        if fileno:
            case = self.pool.get('case.sheet').browse(cr, uid, fileno, context=context)
            res['assignee_id']=(case.assignee_id and case.assignee_id.id or False)
            res['task_id']=False
        else:
            res['assignee_id' ] = False
        return {'value': res}
    
    def onchange_material_title(self, cr, uid, ids, material, context=None):
        res = {}
        if material:
            mate = self.pool.get('material.master').browse(cr, uid, material, context=context)
            res['material_code']=(mate.material_code and mate.material_code or False)
        return {'value': res}
    
    def onchange_task_present(self, cr, uid, ids, present, context=None):
        res = {}
        if not present:        
            res['task_date']= time.strftime('%Y-%m-%d')
            res['task_id']=False
        return {'value': res}
        
    
    def create(self, cr, uid, vals, context=None):
        if not vals.has_key('name') or not vals['name']:
            name = self.pool.get('ir.sequence').get(cr, uid, 'inward.register', context=context) or '/' 
            vals['name'] = name
        if vals['file_number']:
            case = self.pool.get('case.sheet').browse(cr, uid, vals['file_number'], context=context)
            assignee_id = (case.assignee_id and case.assignee_id.id or False)
            vals['assignee_id'] = assignee_id
        if vals['material_id']:
            mate = self.pool.get('material.master').browse(cr, uid, vals['material_id'], context=context)
            vals['material_code']=(mate.material_code and mate.material_code or False)
        retvals = super(inward_register, self).create(cr, uid, vals, context=context)
        obj = self.browse(cr, uid, retvals)
        if vals['datas_fname']:            
            attach_id = self.pool.get('ir.attachment').create(cr, uid, {'name':vals['datas_fname'],'type':'binary','datas':vals['datas'],'user_id':uid,'res_model':(obj.file_number and 'case.sheet' or 'inward.register'),'res_id':(obj.file_number and obj.file_number.id or retvals),'res_name':(obj.file_number and obj.file_number.name or obj.name)})
            self.write(cr, uid, [retvals], {'attach_id':attach_id})
        return retvals        

    def write(self, cr, uid, ids, vals, context=None):
        if vals.has_key('file_number') and vals['file_number']:
            case = self.pool.get('case.sheet').browse(cr, uid, vals['file_number'], context=context)
            assignee_id = (case.assignee_id and case.assignee_id.id or False)
            vals['assignee_id'] = assignee_id
        retvals = super(inward_register, self).write(cr, uid, ids, vals, context=context)
        line = self.browse(cr, uid, ids)[0]
        if not line.attach_id and vals.has_key('datas_fname'):
            attach_id = self.pool.get('ir.attachment').create(cr, uid, {'name':line.datas_fname,'type':'binary','datas':line.datas,'user_id':uid,'res_model':(line.file_number and 'case.sheet' or 'inward.register'),'res_id':(line.file_number and line.file_number.id or retvals),'res_name':(line.file_number and line.file_number.name or line.name)})
            self.write(cr, uid, [line.id], {'attach_id':attach_id}) 
        return retvals
        
inward_register()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: