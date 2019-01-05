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

import re
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
from openerp import netsvc


class bulk_case_hold(osv.osv_memory):
    
    _name = 'bulk.case.hold'
    _description = 'Bulk Case Hold/Unhold'
    
    _columns = {
        'datas': fields.binary('File Content'),
        'summary': fields.text('Summary'),
        'type': fields.selection([('hold', 'Hold'), ('unhold', 'Unhold')], 'Type')
        }
        
    _defaults = {
        'type': 'hold'
        }
    
    def generate_bulk_casesheet_hold(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        case_pool = self.pool.get('case.sheet')
        wf_service = netsvc.LocalService("workflow")
        ir_pool = view_ref = self.pool.get('ir.model.data')
        summary = ''
        for line in self.browse(cr, uid, ids, context=context):
            csvfile = line.datas.decode('base64')
            rowcount = 0
            csvsplit = csvfile.split('\n')
            case_sheet =[row.strip() for row in csvsplit if row]
            case_ids = case_pool.search(cr, uid, [('name', 'in', case_sheet),('state', 'not in', ['new', 'done', 'cancel'])], context=context)
            if line.type == 'hold':
                
                type_ids = self.pool.get('project.task.type').search(cr, uid, [('state', '=', 'hold')], context=context)
                for case_obj in case_pool.browse(cr, uid, case_ids, context=context):
                    cr.execute("update project_task set state='hold', stage_id=%s  where project_id=%s and state in ('draft','pending', 'open');",(type_ids[0], case_obj.project_id.id))
                case_pool.write(cr, uid, case_ids, {'state': 'hold'}, context=context)
            else:
                type_ids = self.pool.get('project.task.type').search(cr, uid, [('state', '=', 'open')], context=context)
                for case_obj in case_pool.browse(cr, uid, case_ids, context=context):
                        
                        cr.execute("update project_task set state='open', stage_id=%s  where project_id=%s and state in ('hold');",(type_ids[0], case_obj.project_id.id))
                
                case_pool.write(cr, uid, case_ids, {'state':'inprogress'}, context=context)
        view_id = False
        
        view_ref = ir_pool.get_object_reference(cr, uid, 'legal_e', 'bulk_case_hold_form_closed')
        view_id = view_ref and view_ref[1] or False,
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Case Sheet Hold'),
            'res_model': 'bulk.case.hold',
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
            }
        
bulk_case_hold()
