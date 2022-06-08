from odoo import api, fields, models, tools, _
from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import requests
import re

_logger = logging.getLogger(__name__)
MONTH_LIST= [('1', 'Enero'), 
        ('2', 'Febrero'), ('3', 'Marzo'), 
        ('4', 'Abril'), ('5', 'Mayo'), 
        ('6', 'Junio'), ('7', 'Julio'), 
        ('8', 'Agosto'), ('9', 'Septiembre'), 
        ('10', 'Octubre'), ('11', 'Noviembre'),
        ('12', 'Diciembre')]

STATES = {'draft': [('readonly', False)]}

class hr_indicadores_previsionales(models.Model):

    _name = 'hr.indicadores'
    _description = 'Indicadores Previsionales'

    name = fields.Char('Nombre')
    state = fields.Selection([
        ('draft','Borrador'),
        ('done','Validado'),
        ], string=u'Estado', readonly=True, default='draft')
    asignacion_familiar_primer = fields.Float(
        'Asignación Familiar Tramo 1', 
        readonly=True, states=STATES,
        help="Asig Familiar Primer Tramo")
    asignacion_familiar_segundo = fields.Float(
        'Asignación Familiar Tramo 2', 
        readonly=True, states=STATES,
        help="Asig Familiar Segundo Tramo")
    asignacion_familiar_tercer = fields.Float(
        'Asignación Familiar Tramo 3', 
        readonly=True, states=STATES,
        help="Asig Familiar Tercer Tramo")
    asignacion_familiar_monto_a = fields.Float(
        'Monto Tramo Uno', readonly=True, states=STATES, help="Monto A")
    asignacion_familiar_monto_b = fields.Float(
        'Monto Tramo Dos', readonly=True, states=STATES, help="Monto B")
    asignacion_familiar_monto_c = fields.Float(
        'Monto Tramo Tres', readonly=True, states=STATES, help="Monto C")
    contrato_plazo_fijo_empleador = fields.Float(
        'Contrato Plazo Fijo Empleador', 
        readonly=True, states=STATES,
        help="Contrato Plazo Fijo Empleador")
    contrato_plazo_fijo_trabajador = fields.Float(
        'Contrato Plazo Fijo Trabajador', 
        readonly=True, states=STATES,
        help="Contrato Plazo Fijo Trabajador")    
    contrato_plazo_indefinido_empleador = fields.Float(
        'Contrato Plazo Indefinido Empleador', 
        readonly=True, states=STATES,
        help="Contrato Plazo Fijo")
    contrato_plazo_indefinido_empleador_otro = fields.Float(
        'Contrato Plazo Indefinido 11 anos o mas', 
        readonly=True, states=STATES,
        help="Contrato Plazo Indefinido 11 anos Empleador")
    contrato_plazo_indefinido_trabajador_otro = fields.Float(
        'Contrato Plazo Indefinido 11 anos o mas', 
        readonly=True, states=STATES,
        help="Contrato Plazo Indefinido 11 anos Trabajador")
    contrato_plazo_indefinido_trabajador = fields.Float(
        'Contrato Plazo Indefinido Trabajador', 
        readonly=True, states=STATES,
        help="Contrato Plazo Indefinido Trabajador")
    caja_compensacion = fields.Float(
        'Caja Compensación', 
        readonly=True, states=STATES,
        help="Caja de Compensacion")
    deposito_convenido = fields.Float(
        'Deposito Convenido', readonly=True, states=STATES, help="Deposito Convenido")
    fonasa = fields.Float('Fonasa', readonly=True, states=STATES, help="Fonasa")
    mutual_seguridad = fields.Float(
        'Mutualidad', readonly=True, states=STATES, help="Mutual de Seguridad")
    isl = fields.Float(
        'ISL', readonly=True, states=STATES, help="Instituto de Seguridad Laboral")
    pensiones_ips = fields.Float(
        'Pensiones IPS', readonly=True, states=STATES, help="Pensiones IPS")
    sueldo_minimo = fields.Float(
        'Trab. Dependientes e Independientes', readonly=True, states=STATES, help="Sueldo Minimo")
    sueldo_minimo_otro = fields.Float(
        'Menores de 18 y Mayores de 65:', 
        readonly=True, states=STATES,
        help="Sueldo Mínimo para Menores de 18 y Mayores a 65")
    tasa_afp_cuprum = fields.Float(
        'Cuprum', readonly=True, states=STATES, help="Tasa AFP Cuprum")
    tasa_afp_capital = fields.Float(
        'Capital', readonly=True, states=STATES, help="Tasa AFP Capital")
    tasa_afp_provida = fields.Float(
        'ProVida', readonly=True, states=STATES, help="Tasa AFP Provida")
    tasa_afp_modelo = fields.Float(
        'Modelo', readonly=True, states=STATES, help="Tasa AFP Modelo")
    tasa_afp_planvital = fields.Float(
        'PlanVital', readonly=True, states=STATES, help="Tasa AFP PlanVital")
    tasa_afp_habitat = fields.Float(
        'Habitat',  help="Tasa AFP Habitat")
    tasa_afp_uno = fields.Float(
        'Uno', help="Tasa AFP Uno")
    tasa_sis_cuprum = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Cuprum")
    tasa_sis_capital = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Capital")
    tasa_sis_provida = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Provida")
    tasa_sis_planvital = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS PlanVital")
    tasa_sis_habitat = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa SIS Habitat")
    tasa_sis_modelo = fields.Float(
        'SIS',  help="Tasa SIS Modelo")
    tasa_sis_uno = fields.Float(
        'SIS', help="Tasa SIS Uno")
    tasa_independiente_cuprum = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Cuprum")
    tasa_independiente_capital = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Capital")
    tasa_independiente_provida = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Provida")
    tasa_independiente_planvital = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes PlanVital")
    tasa_independiente_habitat = fields.Float(
        'SIS', readonly=True, states=STATES, help="Tasa Independientes Habitat")
    tasa_independiente_modelo = fields.Float(
        'SIS',  help="Tasa Independientes Modelo")
    tasa_independiente_uno = fields.Float(
        'SIS', help="Tasa Independientes Uno")
    tope_anual_apv = fields.Float(
        'Tope Anual APV', readonly=True, states=STATES, help="Tope Anual APV")
    tope_mensual_apv = fields.Float(
        'Tope Mensual APV', readonly=True, states=STATES, help="Tope Mensual APV")
    tope_imponible_afp = fields.Float(
        'Tope imponible AFP', readonly=True, states=STATES, help="Tope Imponible AFP")
    tope_imponible_ips = fields.Float(
        'Tope Imponible IPS', readonly=True, states=STATES, help="Tope Imponible IPS")
    tope_imponible_salud = fields.Float(
        'Tope Imponible Salud', readonly=True, states=STATES,)
    tope_imponible_seguro_cesantia = fields.Float(
        'Tope Imponible Seguro Cesantía', 
        readonly=True, states=STATES,
        help="Tope Imponible Seguro de Cesantía")
    uf = fields.Float(
        'UF',  required=True, readonly=True, states=STATES, help="UF fin de Mes")
    utm = fields.Float(
        'UTM',  required=True, readonly=True, states=STATES, help="UTM Fin de Mes")
    uta = fields.Float('UTA', readonly=True, states=STATES, help="UTA Fin de Mes")
    uf_otros = fields.Float(
        'UF Otros', readonly=True, states=STATES, help="UF Seguro Complementario")
    mutualidad_id = fields.Many2one('hr.mutual', 'MUTUAL', readonly=True, states=STATES)
    ccaf_id = fields.Many2one('hr.ccaf', 'CCAF', readonly=True, states=STATES)
    month = fields.Selection(MONTH_LIST, string='Mes', required=True, readonly=True, states=STATES)
    year = fields.Integer('Año', required=True, default=datetime.now().strftime('%Y'), readonly=True, states=STATES)
    gratificacion_legal = fields.Boolean('Gratificación L. Manual', readonly=True, states=STATES)
    mutual_seguridad_bool = fields.Boolean('Mutual Seguridad', default=True, readonly=True, states=STATES)
    ipc = fields.Float(
        'IPC',  required=True, readonly=True, states=STATES, help="Indice de Precios al Consumidor (IPC)")
    
    def action_done(self):
        self.write({'state': 'done'})
        return True
    
    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.onchange('month')
    def get_name(self):
        self.name = str(self.month).replace('10', 'Octubre').replace('11', 'Noviembre').replace('12', 'Diciembre').replace('1', 'Enero').replace('2', 'Febrero').replace('3', 'Marzo').replace('4', 'Abril').replace('5', 'Mayo').replace('6', 'Junio').replace('7', 'Julio').replace('8', 'Agosto').replace('9', 'Septiembre') + " " + str(self.year)

    def find_between_r(self, s, first, last ):
        try:
            start = s.rindex( first ) + len( first )
            end = s.rindex( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def find_month(self, s):
        if s == '1':
            return 'Enero'
        if s == '2':
            return 'Febrero'
        if s == '3':
            return 'Marzo'
        if s == '4':
            return 'Abril'
        if s == '5':
            return 'Mayo'
        if s == '6':
            return 'Junio'
        if s == '7':
            return 'Julio'
        if s == '8':
            return 'Agosto'
        if s == '9':
            return 'Septiembre'
        if s == '10':
            return 'Octubre'
        if s == '11':
            return 'Noviembre'
        if s == '12':
            return 'Diciembre'


    def update_document(self):
        #self.update_date = datetime.today()
        try:
            url = 'https://www.previred.com/web/previred/indicadores-previsionales'
            page = urlopen(url)
            html_bytes = page.read()
            html = html_bytes.decode("utf-8")
            brute = re.findall("\$ [\d\.,]+<|>[\d]+\.[\d\.]+<|>[\d,]+%<|>[\d,]+% R\.I\. ?<", html)
            pure = []
            for item in brute:
                pure.append(float((re.search("[\d\.,]+", item)[0]).replace('.','').replace(',','.')))
        except ValueError:
            return ""
        def uf_convert(cad):
            return round(cad / self.uf, 2)
        try:
            # UF
            self.uf = pure[4]
            
            # 1 UTM
            self.utm = pure[6]

            # 1 UTA
            self.uta = pure[7]

            # 3 RENTAS TOPES IMPONIBLES UF
            self.tope_imponible_afp = uf_convert(pure[8])
            self.tope_imponible_ips = uf_convert(pure[9])
            self.tope_imponible_seguro_cesantia = uf_convert(pure[10])

            # 4 RENTAS TOPES IMPONIBLES
            self.sueldo_minimo = pure[0]
            self.sueldo_minimo_otro = pure[1] #check

            # Ahorro Previsional Voluntario
            self.tope_mensual_apv = uf_convert(pure[14])
            self.tope_anual_apv = uf_convert(pure[15])

            # 5 DEPÓSITO CONVENIDO
            self.deposito_convenido = uf_convert(pure[16])

            # 6 RENTAS TOPES IMPONIBLES
            self.contrato_plazo_indefinido_empleador = pure[17]
            self.contrato_plazo_indefinido_trabajador = pure[18]
            self.contrato_plazo_fijo_empleador = pure[19]
            self.contrato_plazo_indefinido_empleador_otro = pure[20]

            # 7 ASIGNACIÓN FAMILIAR
            self.asignacion_familiar_monto_a = pure[43]
            self.asignacion_familiar_monto_b = pure[45]
            self.asignacion_familiar_monto_c = pure[47]

            self.asignacion_familiar_primer = pure[44]
            self.asignacion_familiar_segundo = pure[46]
            self.asignacion_familiar_tercer = pure[48]

            # 8 TASA COTIZACIÓN OBLIGATORIO AFP
            self.tasa_afp_capital = pure[22]
            self.tasa_sis_capital = pure[23]

            self.tasa_afp_cuprum = pure[25]
            self.tasa_sis_cuprum = pure[26]

            self.tasa_afp_habitat = pure[28]
            self.tasa_sis_habitat = pure[29]

            self.tasa_afp_planvital = pure[31]
            self.tasa_sis_planvital = pure[32]

            self.tasa_afp_provida = pure[34]
            self.tasa_sis_provida = pure[35]

            self.tasa_afp_modelo = pure[37]
            self.tasa_sis_modelo = pure[38]

            self.tasa_afp_uno = pure[40]
            self.tasa_sis_uno = pure[41]

            self.tasa_independiente_capital = pure[24]
            self.tasa_independiente_cuprum = pure[27]
            self.tasa_independiente_habitat = pure[30]
            self.tasa_independiente_planvital = pure[33]
            self.tasa_independiente_provida = pure[36]
            self.tasa_independiente_modelo = pure[39]
            self.tasa_independiente_uno = pure[42]
        except ValueError:
            return ""
