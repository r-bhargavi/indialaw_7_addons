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
from datetime import datetime, date, timedelta
import time
import logging
from openerp.osv import fields, osv
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from openerp.tools import ustr
from openerp import netsvc


_logger = logging.getLogger(__name__)


class hr_holidays_public(osv.osv):

    _name = 'hr.holidays.public'
    _description = 'Public Holidays'

    _columns = {
        'year': fields.char("calendar Year", required=True),
        'line_ids': fields.one2many('hr.holidays.public.line', 'holidays_id', 'Holiday Dates'),
    }

    _rec_name = 'year'
    _order = "year"

    _sql_constraints = [
        ('year_unique', 'UNIQUE(year)', _('Duplicate year!')),
    ]

    def is_public_holiday(self, cr, uid, dt, context=None):

        ph_obj = self.pool.get('hr.holidays.public')
        ph_ids = ph_obj.search(cr, uid, [
            ('year', '=', dt.year),
        ],
            context=context)
        if len(ph_ids) == 0:
            return False

        for line in ph_obj.browse(cr, uid, ph_ids[0], context=context).line_ids:
            if date.strftime(dt, "%Y-%m-%d") == line.date:
                return True

        return False

    def get_holidays_list(self, cr, uid, year, context=None):

        res = []
        ph_ids = self.search(cr, uid, [('year', '=', year)], context=context)
        if len(ph_ids) == 0:
            return res
        [res.append(l.date)
         for l in self.browse(cr, uid, ph_ids[0], context=context).line_ids]
        return res
        
    def get_next_working_day(self, cr, uid, dt, context=None):
        dt = datetime.strptime(dt, '%Y-%m-%d')
        ph_obj = self.pool.get('hr.holidays.public')
        ph_ids = ph_obj.search(cr, uid, [
            ('year', '=', dt.year),
        ],
            context=context)
        if len(ph_ids) == 0:
            if dt.weekday() == 6:
                dt = (dt + timedelta(days=1)).strftime('%Y-%m-%d')
                return self.get_next_working_day(cr, uid, dt, context=context)
            else:
                return dt    
            
        for line in ph_obj.browse(cr, uid, ph_ids[0], context=context).line_ids:
            if date.strftime(dt, "%Y-%m-%d") == line.date or dt.weekday() == 6:
                dt = (dt + timedelta(days=1)).strftime('%Y-%m-%d')
                return self.get_next_working_day(cr, uid, dt, context=context)

        return date.strftime(dt, "%Y-%m-%d")
    
hr_holidays_public()

class hr_holidays_line(osv.osv):

    _name = 'hr.holidays.public.line'
    _description = 'Public Holidays Lines'

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'date': fields.date('Date', required=True),
        'holidays_id': fields.many2one('hr.holidays.public', 'Holiday Calendar Year'),
        'variable': fields.boolean('Date may change'),
    }

    _order = "date, name desc"

hr_holidays_line()


class hr_timesheet_sheet(osv.osv):
    _inherit = "hr_timesheet_sheet.sheet" 
    
    
    def _get_year_from_date(self, cr, uid, ids, field_name, args, context=None):
        res={}
        for obj in self.browse(cr, uid, ids):
            res[obj.id] = obj.date_from[:4]
        return res
    
    _columns = {
        'project_task_work_ids' : fields.one2many('project.task.work', 'timesheet_id', 'Project Task Work lines'),
        'start_year':fields.function(_get_year_from_date, type='integer', string='Year', store={
                'hr_timesheet_sheet.sheet': (lambda self, cr, uid, ids, c={}: ids, ['date_from'], 10),
            }),
        }
    
    _defaults = {
        'date_to' : time.strftime('%Y-%m-%d')
        }
    
    
    def create(self, cr, uid, vals, context=None):
        date_format = '%Y-%m-%d'
        current_date = time.strftime('%Y-%m-%d')
        if vals['date_from'] > current_date or vals['date_to'] > current_date:
            raise osv.except_osv(_('Error'),_('Future date selection restricted.'))
        date_from_wk_no = datetime.strptime(vals['date_from'], date_format)
        date_to_wk_no = datetime.strptime(vals['date_to'], date_format)
        if date_from_wk_no.strftime("%V") == date_to_wk_no.strftime("%V"):
            if (date_to_wk_no - date_from_wk_no).days != 6:
                raise osv.except_osv(_('Error'),_("Please select 'Monday' as date from and 'Sunday' as date to in respective weeks"))
        else:
            raise osv.except_osv(_('Error'),_('From & To date must be in same week.'))
        
        return super(hr_timesheet_sheet, self).create(cr, uid, vals, context=context)
    
    
    def write(self, cr, uid, ids, vals, context=None):
        res = super(hr_timesheet_sheet, self).write(cr, uid, ids, vals, context=context)
        if vals.get('date_from', False) or vals.get('date_to', False):
            date_format = '%Y-%m-%d'
            current_date = time.strftime('%Y-%m-%d')
            for time_sheet_obj in self.browse(cr, uid, ids, context=context):
                if time_sheet_obj.date_from > current_date or time_sheet_obj.date_to > current_date:
                    raise osv.except_osv(_('Error'),_('Future date selection restricted.'))
                date_from_wk_no = datetime.strptime(time_sheet_obj.date_from, date_format)
                date_to_wk_no = datetime.strptime(time_sheet_obj.date_to, date_format)
                if date_from_wk_no.strftime("%V") == date_to_wk_no.strftime("%V"):
                    if (date_to_wk_no - date_from_wk_no).days != 6:
                        raise osv.except_osv(_('Error'),_("Please select 'Monday' as date from and 'Sunday' as date to in respective weeks"))
                else:
                    raise osv.except_osv(_('Error'),_('From & To date must be in same week.'))
        return res
    
    
    def button_reset(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        self.write(cr, uid, ids, {'state': 'new'}, context=context)
        wf_service = netsvc.LocalService("workflow")
        for id in ids:
            wf_service.trg_delete(uid, 'hr_timesheet_sheet.sheet', id, cr)
        return True
    
    
    def button_open(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for time_obj in self.browse(cr, uid, ids, context=context):
            cr.execute('select id from wkf_instance where res_id=%s and res_type=%s and state=%s', (time_obj.id or None,'hr_timesheet_sheet.sheet' or None, 'active'))
            res = cr.fetchall()
            if not res:
                wf_service.trg_create(uid, 'hr_timesheet_sheet.sheet', time_obj.id, cr)
        return True
    
hr_timesheet_sheet()


class hr_analytic_timesheet(osv.osv):
    _inherit = "hr.analytic.timesheet"
    
    
    def _get_default_timesheet_analytic_account(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        anal_acc_pool = self.pool.get('account.analytic.account')
        company=False
        parent_id = False
        child_id = False
        if user.company_id:
            company = user.company_id.name
            parent_ids = anal_acc_pool.search(cr, uid, [('name','=',company),('type','=','view')])
            if not len(parent_ids):
                parent_id = anal_acc_pool.create(cr, uid,{'name':company, 'use_timesheets':True, 'type':'view'})
            else:
                parent_id=parent_ids[0]
            if parent_id:    
                child_ids = anal_acc_pool.search(cr, uid, [('name','=','Miscellaneous Timesheet'),('type','=','normal'), ('parent_id','=',parent_id)])
                if not len(child_ids):
                    child_id = anal_acc_pool.create(cr, uid,{'name':'Miscellaneous Timesheet', 'use_timesheets':True, 'type':'normal', 'parent_id':parent_id})
                else:
                    child_id=child_ids[0]     
                  
        return child_id
    
    _columns = {
        'from_time':fields.float('From Time'),
        'to_time':fields.float('To Time'),        
        }
    _defaults = {
        'account_id':lambda s, cr, uid, c:s._get_default_timesheet_analytic_account(cr, uid, c),
    }

    def onchange_time(self, cr, uid, ids, from_time, to_time, context=None):
        vals={}
        if from_time and to_time:
            if from_time > to_time:
                raise osv.except_osv(_('Error'),_('From Time should be Less than To Time.'))
            else:
                vals['unit_amount'] = to_time-from_time
        return {'value':vals}
            
            
hr_analytic_timesheet()
    
    
class project_work(osv.osv):
    _inherit = "project.task.work"
    
    def _check_from_to_time(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        obj = self.browse(cr, uid, ids[0])
        if obj.from_time and obj.to_time:
            if obj.from_time > obj.to_time:
                return False
        return True
        
    _columns={
        'timesheet_id' : fields.many2one('hr_timesheet_sheet.sheet', 'Timesheet'),
        'project_id':fields.many2one('project.project', 'Project', ondelete='set null', select="1"),
        'from_time':fields.float('From Time'),
        'to_time':fields.float('To Time'),
        'date': fields.datetime('Date', select="1"),
    }        
    _constraints = [
        (_check_from_to_time, 'Error! From Time should be Less than To Time.', ['To Time'])
        ]
    
    def create(self, cr, uid, vals, *args, **kwargs):
        task_obj = self.pool.get('project.task')
        
        timesheet_data = self.pool.get('hr_timesheet_sheet.sheet').read(cr, uid, vals['timesheet_id'], ['employee_id'])
        vals['user_id'] = self.pool.get('hr.employee').read(cr, uid, timesheet_data['employee_id'][0], ['user_id'])['user_id'][0]
        retvals = super(project_work,self).create(cr, uid, vals, *args, **kwargs)
        obj = self.browse(cr, uid, retvals)
        if obj.hr_analytic_timesheet_id:
            vals_line = {}
            task_obj = task_obj.browse(cr, uid, obj.task_id.id)
            vals_line['name'] = '%s: %s' % (ustr(task_obj.name.name), ustr(obj.name or '/'))
            vals_line['from_time'] = obj.from_time
            vals_line['to_time'] = obj.to_time
            #vals_line['user_id'] = obj.timesheet_id.employee_id.id
            obj.hr_analytic_timesheet_id.write(vals_line)
        return retvals
        
    def write(self, cr, uid, ids, vals, context=None):
        """
        When a project task work gets updated, handle its hr analytic timesheet.
        """
        if context is None:
            context = {}
        retvals =  super(project_work,self).write(cr, uid, ids, vals, context)

        if isinstance(ids, (long, int)):
            ids = [ids]

        for task in self.browse(cr, uid, ids, context=context):
            line_id = task.hr_analytic_timesheet_id
            if not line_id:
                # if a record is deleted from timesheet, the line_id will become
                # null because of the foreign key on-delete=set null
                continue

            vals_line = {}
            if 'name' in vals or 'task_id' in vals:
                vals_line['name'] = '%s: %s' % (ustr(task.task_id.name.name), ustr(task.name or '/'))
            if 'from_time' in vals:
                vals_line['from_time'] = vals['from_time']
            if 'to_time' in vals:
                vals_line['to_time'] = vals['to_time']
            self.pool.get('hr.analytic.timesheet').write(cr, uid, [line_id.id], vals_line, context=context)

        return retvals    
        
        
    def onchange_time(self, cr, uid, ids, from_time, to_time, context=None):
        vals={}
        if from_time and to_time:
            if from_time > to_time:
                raise osv.except_osv(_('Error'),_('From Time should be Less than To Time.'))
            else:
                vals['hours'] = to_time-from_time
        return {'value':vals}

project_work()




class hr_holidays(osv.osv):
    _inherit = "hr.holidays"
    
    _columns={
        'flg_reset_leaves':fields.boolean('To Reset the leaves'),
        'state': fields.selection([('draft', 'To Submit'), 
                                   ('cancel', 'Cancelled'),
                                   ('confirm', 'To Approve'), 
                                   ('refuse', 'Refused'), 
                                   ('validate1', 'Second Approval'), 
                                   ('management_validate', 'Waiting Management Approval'), 
                                   ('validate', 'Approved')],
            'Status', readonly=True, track_visibility='onchange',
            help='The status is set to \'To Submit\', when a holiday request is created.\
            \nThe status is \'To Approve\', when holiday request is confirmed by user.\
            \nThe status is \'Refused\', when holiday request is refused by manager.\
            \nThe status is \'Approved\', when holiday request is approved by manager.'),
        }
    
    _defaults = {
        'flg_reset_leaves':False
        }
    
    def check_department(self, cr, uid, ids):
        """
        @return: True or False
        """
        res = False
        for record in self.browse(cr, uid, ids):
            user_obj = self.pool.get('res.users').browse(cr, uid, uid)
            departments = user_obj.company_id.client_business_dept_ids
            if record.employee_id.department_id in departments:
                res = True
        return res
    
    def _get_employee_manager(self, cr, uid, ids, holiday_record, context=None):
        employee_pool = self.pool.get('hr.employee')
        user_obj = self.pool.get('res.users').browse(cr, uid, uid)
        management_department = user_obj.company_id.management_dept_id
        if management_department:
            manager_id = employee_pool.search(cr, uid, [('department_id','=',management_department.id),
                                                        ('ho_branch_id','=',holiday_record.employee_id.ho_branch_id.id)], limit=1, context=context)
            if manager_id:
                manager_obj = employee_pool.browse(cr, uid, manager_id, context=context)
                return manager_obj
        return False

    def get_signup_url(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        document = self.browse(cr, SUPERUSER_ID, ids[0], context=context)
        manager_objs = self._get_employee_manager(cr, SUPERUSER_ID, ids, document, context=context)
        user = manager_objs and manager_objs[0].user_id
        partner = user.partner_id
        action = 'hr_holidays.open_ask_holidays'
        partner.signup_prepare()
        return partner._get_signup_url_for_action(action=action, view_type='form', res_id=document.id)[partner.id]
    
    def holidays_management_validate(self, cr, uid, ids, context=None):
        mail_mail = self.pool.get('mail.mail')
        ir_model_data = self.pool.get('ir.model.data')
        if context:
            ctx = context.copy()
        else:
            ctx = {}
        for record in self.browse(cr, uid, ids, context=context):
            manager_obj = self._get_employee_manager(cr, uid, ids, record, context=context)
            if manager_obj:
                template_id = ir_model_data.get_object_reference(cr, uid, 'legal_e_hr', 'email_template_hr_holiday')[1]
                ctx.update({
                    'email_to': manager_obj and manager_obj[0].work_email or '', 
#                     'email_from': record.employee_id.parent_id and record.employee_id.parent_id.work_email
                    })
                self.pool.get('email.template').send_mail(cr, SUPERUSER_ID, template_id, record.id, force_send=True, context=ctx)
            record.write({'state': 'management_validate'})
        return True
    
    def get_signup_url_manager(self, cr, uid, ids, context=None):
        assert len(ids) == 1
        document = self.browse(cr, SUPERUSER_ID, ids[0], context=context)
        user = document.employee_id.parent_id.user_id
        partner = user.partner_id
        action = 'hr_holidays.open_ask_holidays'
        partner.signup_prepare()
        return partner._get_signup_url_for_action(action=action, view_type='form', res_id=document.id)[partner.id]
    
    def holidays_confirm(self, cr, uid, ids, context=None):
        res = super(hr_holidays, self).holidays_confirm(cr, uid, ids, context=context)
        for record in self.browse(cr, uid, ids, context=context):
            if record.employee_id.parent_id and record.employee_id.parent_id.user_id:
                template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'legal_e_hr', 'email_template_hr_holiday_submit')[1]
                if context is None:
                    context = {}
                context.update({
                    'email_to': record.employee_id.parent_id.work_email or '', 
                    })
                self.pool.get('email.template').send_mail(cr, SUPERUSER_ID, template_id, record.id, force_send=True, context=context)
        return res
    
hr_holidays()

class hr_employee(osv.osv):
    _inherit = "hr.employee"

    _columns = {
        'hr_employee_transfer_history_ids': fields.one2many('hr.employee.transfer.history', 'hr_employee_id', 'Employee Transfer History'),
        'hr_employee_promotion_history_ids': fields.one2many('hr.employee.promotion.history', 'hr_employee_id', 'Employee Promotion History'),
        'hr_employee_recommendation_history_ids': fields.one2many('hr.employee.recommendation.history', 'hr_employee_id', 'Employee Recommendation History'),
        }
hr_employee()

class hr_employee_transfer_history(osv.osv):

    _name = 'hr.employee.transfer.history'
    _description = 'Employee Transfer History'

    _columns = {
        #'name': fields.char('Name', size=128),
        'date': fields.date('Date'),
        'description': fields.text('Description'),
        'hr_employee_id': fields.many2one('hr.employee', 'Employee'),
    }

hr_employee_transfer_history()

class hr_employee_promotion_history(osv.osv):

    _name = 'hr.employee.promotion.history'
    _description = 'Employee Promotion History'

    _columns = {
        #'name': fields.char('Name', size=128),
        'date': fields.date('Date'),
        'description': fields.text('Description'),
        'hr_employee_id': fields.many2one('hr.employee', 'Employee'),
    }

hr_employee_promotion_history()

class hr_employee_recommendation_history(osv.osv):

    _name = 'hr.employee.recommendation.history'
    _description = 'Employee Recommendation History'

    _columns = {
        #'name': fields.char('Name', size=128),
        'date': fields.date('Date'),
        'description': fields.text('Description'),
        'hr_employee_id': fields.many2one('hr.employee', 'Employee'),
    }

hr_employee_recommendation_history()




class analytical_timesheet_employees(osv.osv_memory):
    _inherit = "hr.analytical.timesheet.users"

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(analytical_timesheet_employees, self).default_get(cr, uid, fields, context=context)
        emp_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if emp_ids:
            res.update({'employee_ids': [(6, 0, emp_ids)]})
        return res
    
    
analytical_timesheet_employees()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: