from odoo import models, fields, api, _


class InvoiceJournalField(models.Model):
	_inherit = 'account.invoice'


	journal_id = fields.Many2one('account.journal', string="Journal", required=True)

