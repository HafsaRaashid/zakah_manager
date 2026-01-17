from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    zakah_recovery_rate = fields.Float(
        string='Receivable Recovery %',
        default=100.0,
        help='Expected recoverable percentage for zakah calculation'
    )
