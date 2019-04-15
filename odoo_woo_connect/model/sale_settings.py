from odoo import models, fields, api


class SaleLoanSettings(models.TransientModel):
    """Create two fields to the Reward setting form 'Loan Percentage' and 'Loan Duration'"""
    # _name = 'loan.settings'
    _inherit = 'res.config.settings'

    loan_per = fields.Float('Loan Interest rate')
    loan_duration = fields.Selection([
        ('24', '24 Months'),
        ('36', '36 Months'),
        ('48', '48 Months'),
        ('60', '60 Months'),
        ('72', '72 Months'),
        ('84', '84 Months')],default='24')

    @api.multi
    def execute(self):
        """Set the default values for 'Loan Percentage' and 'Loan Duration' fields """
        ir_values = self.env['ir.default']
        ir_values.set('loan.settings','loan_per', self.loan_per)
        ir_values.set('loan.settings','loan_duration', self.loan_duration)
        return True