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
import re
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

class bulk_case_sheet(osv.osv_memory):
    
    _name = 'bulk.case.sheet'
    _description = 'Bulk Case Sheet'
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

    def _data_set(self, cr, uid, ids, name, value, arg, context=None):
        # We dont handle setting data to null
        if not value:
            return True
        if context is None:
            context = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
        file_size = len(value.decode('base64'))
        if location:
            attach = self.browse(cr, uid, ids, context=context)
            if attach.store_fname:
                self._file_delete(cr, uid, location, attach.store_fname)
            fname = self._file_write(cr, uid, location, value)
            # SUPERUSER_ID as probably don't have write access, trigger during create
            super(bulk_case_sheet, self).write(cr, SUPERUSER_ID, [ids], {'store_fname': fname, 'file_size': file_size}, context=context)
        else:
            super(bulk_case_sheet, self).write(cr, SUPERUSER_ID, [ids], {'db_datas': value, 'file_size': file_size}, context=context)
        return True
        
    def name_get(self, cr, uid, ids, context=None):
        res = []
        if not ids:
            return res
        for line in self.browse(cr, uid, ids, context=context):
            res.append((line.id,line.name.name))
        return res
    
    _columns = {
    		'name': fields.many2one('case.sheet','File Number to Duplicate'),
    		'flg_first_row':fields.boolean('The first row of the file contains the label of the column'),
    		'field_delimiter':fields.selection([(',',','),(';',';'),(':',':')],'Field Delimiter'),
    		'text_delimiter':fields.selection([('"','"'),("'","'")],'Text Delimiter'),
    		'datas': fields.function(_data_get, fnct_inv=_data_set, string='File Content', type="binary", nodrop=True),
    		'datas_fname': fields.char('File Content',size=256, required=True),
    		'store_fname': fields.char('Stored Filename', size=256),
        	'db_datas': fields.binary('Database Data'),
        	'file_size': fields.integer('File Size'),
        	'attach_id': fields.many2one('ir.attachment','Attachment ID'),
            'lot_name': fields.char('Lot Number', size=64, required=True),
            'arbitration_amount': fields.float('Arbitration Fee'),
        }
        
    _defaults = {
                'field_delimiter':',',
                'text_delimiter':'"',
    }
    
    def generate_bulk_casesheet(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            csvfile = line.datas.decode('base64')
            rowcount = 0
            if line.flg_first_row:
                rowcount = 1
            csvsplit = csvfile.split('\n')
            for row in range(rowcount,len(csvsplit)):
                csvsplit[row]=re.sub(r'[^\x00-\x7f]',r'',csvsplit[row])
                cells = csvsplit[row].split(line.field_delimiter)
                text_delimiter = ''
                if line.text_delimiter:
                    text_delimiter = line.text_delimiter
                if len(cells)>1:
                    cells[0] = cells[0].replace(text_delimiter,"")
                    cells[1] = cells[1].replace(text_delimiter,"")
                    refsearchids = self.pool.get('case.sheet').search(cr, uid, [('client_id','=',line.name.client_id.id),('company_ref_no','=',cells[0])])
                    if len(refsearchids):
                        raise osv.except_osv(_('Warning'),_('For this Client "%s" Client Reference already Exists.'%cells[0]))
                    opp_data = {}
                    for opp in line.name.opp_parties:
                        opp_data['type'] = opp.type
                        opp_data['name'] = cells[1]
                    if opp_data == {}:
                        opp_data = {'name':cells[1]}
                    context.update({'bulk_case':  True})
                    newid = self.pool.get('case.sheet').copy(cr, uid, line.name.id,{'lot_name': line.lot_name, 'arbitration_amount': line.arbitration_amount,'company_ref_no':cells[0],'opp_parties':[(0, 0, opp_data)]}, context=context)
                    self.pool.get('case.sheet').confirm_casesheet(cr, uid, [newid])
            self.pool.get('case.sheet').write(cr, uid, [line.name.id], {'lot_name': line.lot_name, 'arbitration_amount': line.arbitration_amount}, context=context)
        return True
        
    def create(self, cr, uid, vals, context=None): 
        if context is None:
            context = {}
        retvals = super(bulk_case_sheet, self).create(cr, uid, vals, context=context)
        return retvals
        
bulk_case_sheet()
