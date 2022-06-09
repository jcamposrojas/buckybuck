from pytz import timezone
from datetime import date, datetime, time

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'
    
    indicadores_id = fields.Many2one('hr.indicadores', string='Indicadores',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Defines Previred Forecast Indicators')
    movimientos_personal = fields.Selection([('0', 'Sin Movimiento en el Mes'),
     ('1', 'Contratación a plazo indefinido'),
     ('2', 'Retiro'),
     ('3', 'Subsidios (L Médicas)'),
     ('4', 'Permiso Sin Goce de Sueldos'),
     ('5', 'Incorporación en el Lugar de Trabajo'),
     ('6', 'Accidentes del Trabajo'),
     ('7', 'Contratación a plazo fijo'),
     ('8', 'Cambio Contrato plazo fijo a plazo indefinido'),
     ('11', 'Otros Movimientos (Ausentismos)'),
     ('12', 'Reliquidación, Premio, Bono')     
     ], string='Código Movimiento', default="0")

    date_start_mp = fields.Date('Fecha Inicio MP',  help="Fecha de inicio del movimiento de personal")
    date_end_mp = fields.Date('Fecha Fin MP',  help="Fecha del fin del movimiento de personal")

    @api.model
    def create(self, vals):
        if 'indicadores_id' in self.env.context:
            vals['indicadores_id'] = self.env.context.get('indicadores_id')
        if 'movimientos_personal' in self.env.context:
            vals['movimientos_personal'] = self.env.context.get('movimientos_personal')
        return super(HrPayslip, self).create(vals)

    @api.model
    def _get_worked_day_lines(self, domain=None, check_out_of_contract=True):
    #def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super(HrPayslip, self)._get_worked_day_lines(domain, check_out_of_contract)
        temp = 0 
        dias = 0
        attendances = {}
        leaves = []

        for line in res:
            entry = self.env['hr.work.entry.type'].search(
                [
                    ('id', '=', line.get('work_entry_type_id')),
                ])

            if entry.code == 'WORK100':
            #if line.get('work_entry_type_id.code') == 'WORK100':
                attendances = line
            else:
                leaves.append(line)
        for leave in leaves:
            temp += leave.get('number_of_days') or 0
        #Dias laborados reales para calcular la semana corrida
        effective = attendances.copy()
        entry_effective = self.env['hr.work.entry.type'].search(
                [
                    ('code', '=', 'EFF100'),
                ])
        effective.update({
            'name': _("Dias de trabajo efectivos"),
            'sequence': 2,
            #'code': 'EFF100',
            'work_entry_type_id': entry_effective.id,
        })
        # En el caso de que se trabajen menos de 5 días tomaremos los dias trabajados en los demás casos 30 días - las faltas
        # Estos casos siempre se podrán modificar manualmente directamente en la nomina.
        # Originalmente este dato se toma dependiendo de los dias del mes y no de 30 dias
        # TODO debemos saltar las vacaciones, es decir, las vacaciones no descuentan dias de trabajo. 
        _logger.info('NUMBEROFDAY')
        _logger.info(effective.get('number_of_days'))
        if (effective.get('number_of_days') or 0) < 5:
            dias = effective.get('number_of_days')
        else:
            dias = 30 - temp
        attendances['number_of_days'] = dias
        res = []
        res.append(attendances)
        res.append(effective)
        res.extend(leaves)
        return res
