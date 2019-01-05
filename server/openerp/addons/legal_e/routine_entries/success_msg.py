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

class succes_msg(osv.osv_memory):

    _name = "success.msg"
    _description = "Selected Date is a Holiday!"

    _columns = {
        'name': fields.char('Selected Day is a Holiday!',size=64),
    }

succes_msg()

class succes_msg1(osv.osv_memory):

    _name = "succes.msg1"
    _description = "To Show a Message when connection to AP was successful"

    _columns = {
        'name': fields.text('Status', readonly=True),
    }

succes_msg1()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
