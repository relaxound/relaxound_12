from odoo import models, api, fields
import json

class InvoiceJournalField(models.Model):
    _inherit = 'account.invoice'

    reverse_charg_note_german = fields.Text(string='REVERSE CHARGE',compute='_set_reverse_charge')
    reverse_charg_note_france = fields.Text(string='REVERSE CHARGE',compute='_set_reverse_charge')


    @api.multi
    def _set_reverse_charge(self):
	#Reverse charge note condition applied on tax
        for account_id in self:
            if account_id.partner_id.country_id.name == 'Belgium':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : " livraison intracommunautaire exonérée TVA"})

            elif account_id.partner_id.country_id.name == 'Bulgaria':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  Neoblagaema vatreshnoobshtnostna dostavka"})

            elif account_id.partner_id.country_id.name == 'Denmark':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  momsfri EU levering"})

            elif account_id.partner_id.country_id.name == 'Estonia':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  käibemaksuvaba ühendusesisene kättetoimetamine"})

            elif account_id.partner_id.country_id.name == 'Finland':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  veroton yhteisömyynti"})

            elif account_id.partner_id.country_id.name == 'France':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /"  , 'reverse_charg_note_france' : "livraison intracommunautaire exonérée TVA"})

            elif account_id.partner_id.country_id.name == 'Greece':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  tax free intracommunity delivery"})

            elif account_id.partner_id.country_id.name == 'Ireland':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  tax free intracommunity despatch"})

            elif account_id.partner_id.country_id.name == 'Italy':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  cessioni intracomunitarie esenti"})

            elif account_id.partner_id.country_id.name == 'Latvia':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : " Ar 0% apliekamas precu piegades ES ietvaros, PVN likuma 28. pants*)"})

            elif account_id.partner_id.country_id.name == 'Lithuania':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  pridétinés vertés mokesciu neapmokestinamas tiekimas Europos Sajungos viduje"})

            elif account_id.partner_id.country_id.name == 'Luxembourg':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  livraison intracommunautaire exonérée TVA."})

            elif account_id.partner_id.country_id.name == 'Malta':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  tax free intracommunity delivery"})

            elif account_id.partner_id.country_id.name == 'Netherlands':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  intracommunautaire levering"})

            elif account_id.partner_id.country_id.name == 'Austria':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  steuerfreie innergemeinschaftliche Lieferung"})

            elif account_id.partner_id.country_id.name == 'Poland':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  wewnatrzwspólnotowa dostawa towarów opodatkowana wg. stawki podatku 0% (Art.42 Ust. 0 pod. od tow.il usl.*)"})

            elif account_id.partner_id.country_id.name == 'Portugal':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  fornecimento inter-comunitário isento de IVA"})

            elif account_id.partner_id.country_id.name == 'Romania':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  Livrare intracomunitara scutita de TVA."})

            elif account_id.partner_id.country_id.name == 'Sweden':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  skattefri gemenskapsintern leverans"})

            elif account_id.partner_id.country_id.name == 'Slovakia':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  od dane oslobodené intrakomunitárne dodávky"})

            elif account_id.partner_id.country_id.name == 'Slovenia':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  oproscena dobava znotraj skupnosti"})

            elif account_id.partner_id.country_id.name == 'Spain':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  entrega intracomunitaria libre de impuesto"})

            elif account_id.partner_id.country_id.name == 'Czech Republic':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  dodání zbozí do jiného clenského státu, osvobozené od DPH"})

            elif account_id.partner_id.country_id.name == 'Hungary':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  forgalmiadó-mentes, Közösségenbelülrol történo áruszállítás"})

            elif account_id.partner_id.country_id.name == 'Cyprus':
                account_id.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  tax free intracommunity delivery"})
