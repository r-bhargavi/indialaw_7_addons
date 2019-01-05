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
from datetime import datetime, timedelta
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID


class acknowledgement_status(osv.osv):
    _name = 'acknowledgement.status'
    _columns = {
        'name':fields.char('Status Name',size=128, required=True),
    }

acknowledgement_status()


class outward_toname(osv.osv):
    _name = 'outward.toname'
    _columns = {
        'outward_id':fields.many2one('outward.register','Outward Register Ref'),
        'acknowledgement_status':fields.many2one('acknowledgement.status','Status'),
        'name':fields.char('To',required=True),
        'from':fields.char('From'),
        'ack_reference': fields.char('ACK Reference',  size=128)
    }
    
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        for line in self.browse(cr, uid, ids, context=context):
            res.append((line.id,line.name.name))
        return res

outward_toname()


class outward_register(osv.osv):
    
    _name = 'outward.register'
    _description = 'Outward Register'
    _inherit = ['mail.thread']
    
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
            super(outward_register, self).write(cr, SUPERUSER_ID, [id], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(outward_register, self).write(cr, SUPERUSER_ID, [id], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
        
    def _get_to_names(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for reg in self.browse(cr, uid, ids, context=context):
            names=''
            for line in reg.to_ids:
                names = (names!='' and (names+', '+ line.name) or line.name)
            res[reg.id] = names    
        return res
        
    def _get_to_name_acknowledge(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for reg in self.browse(cr, uid, ids, context=context):
            names=''
            for line in reg.to_ids:
                names = (names!='' and (names+', '+ (line.name + ' - ' + (line.acknowledgement_status.name or ''))) or (line.name + ' - ' + (line.acknowledgement_status.name or '')))
            res[reg.id] = names    
        return res
        
    def _get_remainder_date(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for reg in self.browse(cr, uid, ids, context=context):
            remaind = False
            if reg.set_remainder and reg.days_ahead and reg.days_ahead > 0:
                remaind = (datetime.strptime(reg.date, '%Y-%m-%d') + timedelta(days=reg.days_ahead)).strftime('%Y-%m-%d')
            res[reg.id] = remaind
       
        return res
    
    def _fnct_search(self, cr, uid, obj, name, args, context=None):
        toname_ids = self.pool.get('outward.toname').search(cr, uid, [('name','ilike',args[0][2])])
        lst = list(set([toname.outward_id.id for toname in self.pool.get('outward.toname').browse(cr, uid, toname_ids)]))
        return [('id','in',lst)]          
        
    
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
    		'name': fields.char('Entry Number', size=64, required=False, select=True),
    		'date':fields.date('Entry Date'),
    		'file_number':fields.many2one('case.sheet','File Number'),
    		'description':fields.char('Description'),
    		'auto_ref_no':fields.boolean('Auto Ref. No'),
    		'file_ref_no':fields.char('Ref. No',size=128),
    		'material_code':fields.char('Material ID',readonly=True),
    		'material_id':fields.many2one('material.master', 'Material Title'),
    		'to_ids':fields.one2many('outward.toname','outward_id','To Name(s)'),
    		'assignee_id':fields.many2one('hr.employee','Assignee',readonly=True),
    		'delivery_mode':fields.many2one('delivery.master','Delivery Mode'),
    		'party_receipt_date':fields.date('Date of Receipt by Party'),
    		'inward_date':fields.date('Inward Date'),
    		'set_remainder':fields.boolean('Set Reminder'),
    		'days_ahead':fields.integer('Days Ahead'),
    		'remainder_date':fields.function(_get_remainder_date,string='Remainder Date',type='date',store={'outward.register' : (lambda self, cr, uid, ids, c={}: ids, ['days_ahead','set_remainder'], 20)}),
    		'acknowledgement':fields.char('Acknowledgement',size=128),
    		'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
    		'datas_fname': fields.char('File Name',size=256),
    		'store_fname': fields.char('Stored Filename', size=256),
        	'db_datas': fields.binary('Database Data'),
        	'file_size': fields.integer('File Size'),
        	'attach_id': fields.many2one('ir.attachment','Attachment ID'),
        	'to_names':fields.function(_get_to_names,string='To Name(s)',fnct_search=_fnct_search,type='char'),
        	'to_name_acknowledge':fields.function(_get_to_name_acknowledge,string='To Name(s) Acknowledgement',type='char'),
        	'state':fields.selection([('new','New'),('done','Completed')],'State'),
            'ho_branch_id':fields.many2one('ho.branch','Location'),
            'remarks':  fields.text('Remarks')
        }
        
    _defaults = {
    	'date':lambda *a: time.strftime('%Y-%m-%d'),
    	'inward_date':lambda *a: time.strftime('%Y-%m-%d'),
    	'party_receipt_date':lambda *a: time.strftime('%Y-%m-%d'),
    	'state':'new',
    	'ho_branch_id':lambda s, cr, uid, c:s._get_default_ho_branch(cr, uid, c),
    }
    _order = 'name desc, date desc'
    
    def complete_outward(self, cr, uid, ids, context=None):
        for obj in self.browse(cr, uid, ids):
            self.write(cr, uid, [obj.id], {'state':'done'})
        return True    
        
    def onchange_file_number(self, cr, uid, ids, autoref, name, fileno, context=None):
        res = {}

        if fileno:
            to_ids = []
            case = self.pool.get('case.sheet').browse(cr, uid, fileno, context=context)
            res['assignee_id']=(case.assignee_id and case.assignee_id.id or False)
            for ln in case.opp_parties:
                to_ids.append((0,0,{'name':ln.name}))
            res['to_ids'] = to_ids
        else:
            res['assignee_id' ] = False
            res['to_ids'] = []
        return {'value': res}
        
        if autoref:
            case = self.pool.get('case.sheet').browse(cr, uid, fileno, context=context)
            res['file_ref_no'] = name +'/'+ (fileno and case.name +'/' or '')+ time.strftime('%Y')[2:]
            
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
    
    def onchange_remainder(self, cr, uid, ids, remainder, context=None):
        res = {}
        if not remainder:        
            res['days_ahead']= False
            res['remainder_date']= False
        return {'value': res} 
    
        
    def generate_file_ref_no(self, cr, uid, ids, autoref, name, fileno, context=None):
        res = {}
        if autoref:
            case = self.pool.get('case.sheet').browse(cr, uid, fileno, context=context)
            res['file_ref_no'] = name +'/'+ (fileno and case.name +'/' or '')+ time.strftime('%Y')[2:]
        else:
            res['file_ref_no'] = False
        return {'value':res}
    
    def create(self, cr, uid, vals, context=None):
        if not vals.has_key('name') or not vals['name']:
            name = self.pool.get('ir.sequence').get(cr, uid, 'outward.register', context=context) or '/' 
            vals['name'] = name
        
        if vals['file_number']:
            case = self.pool.get('case.sheet').browse(cr, uid, vals['file_number'], context=context)
            assignee_id = (case.assignee_id and case.assignee_id.id or False)
            vals['assignee_id'] = assignee_id
        if vals['material_id']:
            mate = self.pool.get('material.master').browse(cr, uid, vals['material_id'], context=context)
            vals['material_code']=(mate.material_code and mate.material_code or False)

        retvals = super(outward_register, self).create(cr, uid, vals, context=context)
        obj = self.browse(cr, uid, retvals)
        
        
        if vals['datas_fname']:            
            attach_id = self.pool.get('ir.attachment').create(cr, uid, {'name':vals['datas_fname'],'type':'binary','datas':vals['datas'],'user_id':uid,'res_model':(obj.file_number and 'case.sheet' or 'outward.register'),'res_id':(obj.file_number and obj.file_number.id or retvals),'res_name':(obj.file_number and obj.file_number.name or obj.name)})
            self.write(cr, uid, [retvals], {'attach_id':attach_id})
        return retvals        

    def write(self, cr, uid, ids, vals, context=None):
        if vals.has_key('file_number') and vals['file_number']:
            case = self.pool.get('case.sheet').browse(cr, uid, vals['file_number'], context=context)
            assignee_id = (case.assignee_id and case.assignee_id.id or False)
            vals['assignee_id'] = assignee_id
        
        retvals = super(outward_register, self).write(cr, uid, ids, vals, context=context)
        line = self.browse(cr, uid, ids)[0]
        if not line.attach_id and vals.has_key('datas_fname'):
            attach_id = self.pool.get('ir.attachment').create(cr, uid, {'name':line.datas_fname,'type':'binary','datas':line.datas,'user_id':uid,'res_model':'outward.register','res_id':line.id,'res_name':line.name})
            self.write(cr, uid, [line.id], {'attach_id':attach_id})            
        
        return retvals
        
outward_register()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: