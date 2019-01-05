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


class bulk_task_close(osv.osv_memory):
    
    _name = 'bulk.task.close'
    _description = 'Bulk Task Close'
    
    
    _columns = {
        'flg_first_row':fields.boolean('The first row of the file contains the label of the column'),
        'field_delimiter':fields.selection([(',',','),(';',';'),(':',':')],'Field Delimiter'),
        'text_delimiter':fields.selection([('"','"'),("'","'")],'Text Delimiter'),
        'datas': fields.binary('File Content'),
        }
        
    _defaults = {
        'field_delimiter':',',
        'text_delimiter':'"',
        'flg_first_row': True
        }
    
    def generate_bulk_task_close(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        task_pool = self.pool.get('project.task')
        task_master_pool = self.pool.get('task.master')
        project_pool = self.pool.get('project.project')
        wf_service = netsvc.LocalService("workflow")
        ir_pool = self.pool.get('ir.model.data')
        stage_ids = self.pool.get('project.task.type').search(cr, uid, [('state','=','done')])
        task_ids = []
        for line in self.browse(cr, uid, ids, context=context):
            csvfile = line.datas.decode('base64')
            rowcount = 0
            csvsplit = csvfile.split('\n')
            for row in range(rowcount,len(csvsplit)):
                csvsplit[row]=re.sub(r'[^\x00-\x7f]',r'',csvsplit[row])
                cells = csvsplit[row].split(line.field_delimiter)
                text_delimiter = ''
                if line.text_delimiter:
                    text_delimiter = line.text_delimiter
                if len(cells)>1:
                    cells[0] = cells[0].replace(text_delimiter,"").rstrip()
                    cells[1] = cells[1].replace(text_delimiter,"").rstrip()
                    task_id = task_master_pool.search(cr, uid, [('name', '=', cells[0])], context=context)
                    project_id = project_pool.search(cr, uid, [('name', '=', cells[1])], context=context)
                    if task_id and project_id:
                        task_ids += task_pool.search(cr, uid, [('name', '=', task_id[0]), ('project_id', '=', project_id[0])], context=context)
                        
        task_ids  = list(set(task_ids))
        if task_ids and stage_ids:
            task_pool.write(cr, uid, task_ids, {'state': 'done', 'stage_id': stage_ids[0]}, context=context)
           
        
        view_ref = ir_pool.get_object_reference(cr, uid, 'legal_e', 'bulk_task_close_form_closed')
        view_id = view_ref and view_ref[1] or False,
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bulk Task Close'),
            'res_model': 'bulk.task.close',
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
            }
        
bulk_task_close()
