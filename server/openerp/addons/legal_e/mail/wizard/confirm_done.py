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

class confirm_done(osv.osv_memory):

    _name = "confirm.done"
    _description = "Mark Selected Tasks as Done"

    _columns = {
        'name': fields.char('Do you want to Make selected Tasks as Done?', size=64),
    }
    
    
    def button_confirm(self, cr, uid, ids, context=None):
        if context.has_key('active_ids'):       
            vals = {}
            vals['remaining_hours'] = 0.0
            vals['state']='done'
            stage_id = False
            comids = self.pool.get('project.task.type').search(cr, uid, [('name','=','Completed'),('state','=','done')])
            if comids and len(comids):
                vals['stage_id']=comids[0]
                stage_id = comids[0]
            
            actids = tuple(context['active_ids'])
            if len(context['active_ids'])>1:
                qry = "update project_task set remaining_hours=0.0, state='done', flg_message=True,progress=100, stage_id="+str(stage_id)+" where id in "+str(actids)+""
            else:
                qry = "update project_task set remaining_hours=0.0, state='done', flg_message=True,progress=100, stage_id="+str(stage_id)+" where id ="+str(context['active_ids'][0])+""    
            cr.execute(qry)
        return True
        
confirm_done()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
