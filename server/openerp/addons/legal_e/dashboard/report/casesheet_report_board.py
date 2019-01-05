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
from openerp.osv import fields,osv
from openerp import tools

class casesheet_report_board(osv.osv):
    _name = "casesheet.report.board"
    _table = 'casesheet_report_board'
    _description = "Open and Completed Case Sheets by Type of work"
    _auto = False
    _order="year,month"
    _columns = {
                'name':fields.char('File Number', size=128, readonly=True),
                'date': fields.date('Date', readonly=True),
                'nbr': fields.integer('# of Case Sheets', readonly=True),
                'state': fields.selection([
                    ('new', 'New'),
                    ('inprogress', 'In Progress'),
                    ('cancel', 'Cancelled'),
                    ('transfer','Transferred'),
                    ('won', 'Won'),
                    ('arbitrated', 'Arbitrated'),
                    ('withdrawn', 'With Drawn'),
                    ('lost', 'Lost'),
                    ('inactive', 'Inactive'),
                    ('done', 'Closed'),
                        ], 'Status', readonly=True),
                'month':fields.integer('Month'),
                'year':fields.integer('Year'),
                'year_month':fields.integer('Year Month'),
                'work_type':fields.selection([('civillitigation', 'Civil Litigation'),('criminallitigation', 'Criminal Litigation'), ('non_litigation', 'Non Litigation'), ('arbitration', 'Arbitration'),('execution', 'Execution'),('mediation', 'Mediation')], 'Type of Work',readonly=True)
                }

    
    def init(self, cr):
        tools.drop_view_if_exists(cr, 'casesheet_report_board')
        cr.execute("""
            create view casesheet_report_board as (
                select             
                    c.date::varchar||'-'||c.id::varchar AS id,
                    c.date as date,
                    1 as nbr,       
                    c.name as name,
                    c.state as state,                    
                    to_char(c.date, 'YYYY')::integer as year,                    
                    to_char(c.date, 'MM')::integer as month,
                    to_char(c.date, 'YYYY-MM-DD') as day,
                    c.work_type as work_type,
                     (to_char(c.date, 'YYYY')||to_char(c.date, 'MM'))::integer AS year_month
                    
                from case_sheet c 
                 order by year,month
            )
            """)
    
casesheet_report_board()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: