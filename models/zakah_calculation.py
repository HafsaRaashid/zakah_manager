from odoo import models, fields, api
from datetime import date, timedelta


class ZakahCalculation(models.Model):
    _name = 'zakah.calculation'
    _description = 'Zakah Calculation'
    _rec_name = 'name'
    name = fields.Char(default="Zakah Dashboard")

    inventory_value = fields.Float(compute='_compute_inventory_value', store=False)
    cash_value = fields.Float(compute='_compute_cash_value', store=False)
    receivables_value = fields.Float(compute='_compute_receivables_value', store=False)
    short_term_liabilities = fields.Float(compute='_compute_short_term_liabilities', store=False)
    deduct_liabilities = fields.Boolean( string="Deduct Short Term Liabilities", default=False )
    total_assets = fields.Float(compute='_compute_total_assets', store=False)
    zakah_due = fields.Float(compute='_compute_zakah_due', store=False)

    # Hard coded values for nisab calculation
    GOLD_NISAB_GRAMS = 85
    SILVER_NISAB_GRAMS = 595
    GOLD_PRICE_PER_GRAM = 1000.0
    SILVER_PRICE_PER_GRAM = 12.0

    # Zakah period cutoff date
    @property 
    def cutoff_date(self):
        config = self.env['ir.config_parameter'].sudo()
        zakah_period = int(config.get_param('zakah.period', 354))
        return date.today() - timedelta(days=zakah_period)

    # Inventory Value
    def _compute_inventory_value(self):
        for record in self:
            products = self.env['product.product'].search([
            ('detailed_type', '=', 'product')
            ])

            total_value = 0.0
            for product in products:
                total_value += product.qty_available * product.list_price

            record.inventory_value = total_value


    # Cash & Bank Value
    def _compute_cash_value(self):
        for record in self:
            cash_bank_accounts = self.env['account.account'].search([
                ('account_type', 'in', ['asset_cash', 'asset_bank'])
            ])

            move_lines = self.env['account.move.line'].search([
                ('date', '<=', self.cutoff_date),
                ('account_id', 'in', cash_bank_accounts.ids),
                ('parent_state', '=', 'posted')
            ])

            record.cash_value = sum(move_lines.mapped('balance'))

    # Receivables with recovery %
    def _compute_receivables_value(self):
        for record in self:
            invoices = self.env['account.move'].search([
                ('invoice_date', '<=', self.cutoff_date),
                ('move_type', '=', 'out_invoice'),
                ('payment_state', '!=', 'paid'),
                ('state', '=', 'posted')
            ])

            total = 0.0
            for inv in invoices:
                recovery = inv.partner_id.zakah_recovery_rate or 0.0
                total += inv.amount_residual * (recovery / 100)

            record.receivables_value = total

    # Short Term Liabilities
    def _compute_short_term_liabilities(self):
        for record in self:
            liability_accounts = self.env['account.account'].search([
                ('account_type', 'in', ['liability_payable', 'liability_current'])
            ])
            move_lines = self.env['account.move.line'].search([
                ('account_id', 'in', liability_accounts.ids),
                ('parent_state', '=', 'posted')
            ])
            record.short_term_liabilities = sum(move_lines.mapped('balance'))

    # Total Assets
    @api.depends('inventory_value', 'cash_value', 'receivables_value', 'short_term_liabilities', 'deduct_liabilities')
    def _compute_total_assets(self):
        for record in self:
            base_assets = record.inventory_value + record.cash_value + record.receivables_value
            record.total_assets = (base_assets - record.short_term_liabilities if record.deduct_liabilities else base_assets)

    # Zakah Due
    @api.depends('inventory_value', 'cash_value', 'receivables_value')
    def _compute_zakah_due(self):
        config = self.env['ir.config_parameter'].sudo()

        zakah_rate = float(config.get_param('zakah.rate', 2.5)) / 100
        nisab_method = config.get_param('zakah.nisab_method', 'gold')

        for record in self:
            if nisab_method == 'gold':
                nisab = self.GOLD_NISAB_GRAMS * self.GOLD_PRICE_PER_GRAM
            else:
                nisab = self.SILVER_NISAB_GRAMS * self.SILVER_PRICE_PER_GRAM

            record.zakah_due = (
                record.total_assets * zakah_rate
                if record.total_assets >= nisab else 0.0
            )

    def print_report(self):
        return self.env.ref('zakah_manager.zakah_summary_report').report_action(self)
