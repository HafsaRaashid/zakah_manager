from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    zakah_period = fields.Integer(
        string='Zakah Calculation Period (days)',
        config_parameter='zakah.period',
        default=354
    )


    nisab_method = fields.Selection(
        [
            ('gold', 'Gold'),
            ('silver', 'Silver'),
        ],
        string="Nisab Method",
        config_parameter='zakah.nisab_method',
        default='gold'
    )

    zakah_rate = fields.Float(
        string='Zakah Rate',    
        config_parameter='zakah.rate',
        default=2.5
    )
   