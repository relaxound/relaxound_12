from odoo import models, api, fields
import json

class InvoiceJournalField(models.Model):
    _inherit = 'account.invoice'

    reverse_charg_note_german = fields.Text(string='REVERSE CHARGE',compute='_set_reverse_charge')
    reverse_charg_note_france = fields.Text(string='REVERSE CHARGE',compute='_set_reverse_charge')


    @api.multi
    def _set_reverse_charge(self):
        if self.partner_id.country_id.name == 'Belgium':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : " livraison intracommunautaire exonérée TVA"})

        elif self.partner_id.country_id.name == 'Bulgaria':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  Neoblagaema vatreshnoobshtnostna dostavka"})

        elif self.partner_id.country_id.name == 'Denmark':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  momsfri EU levering"})

        elif self.partner_id.country_id.name == 'Estonia':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  käibemaksuvaba ühendusesisene kättetoimetamine"})

        elif self.partner_id.country_id.name == 'Finland':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  veroton yhteisömyynti"})

        elif self.partner_id.country_id.name == 'France':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /"  , 'reverse_charg_note_france' : "livraison intracommunautaire exonérée TVA"})

        elif self.partner_id.country_id.name == 'Greece':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  tax free intracommunity delivery"})

        elif self.partner_id.country_id.name == 'Ireland':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  tax free intracommunity despatch"})

        elif self.partner_id.country_id.name == 'Italy':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  cessioni intracomunitarie esenti"})

        elif self.partner_id.country_id.name == 'Latvia':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : " Ar 0% apliekamas precu piegades ES ietvaros, PVN likuma 28. pants*)"})

        elif self.partner_id.country_id.name == 'Lithuania':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  pridétinés vertés mokesciu neapmokestinamas tiekimas Europos Sajungos viduje"})

        elif self.partner_id.country_id.name == 'Luxembourg':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  livraison intracommunautaire exonérée TVA."})

        elif self.partner_id.country_id.name == 'Malta':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  tax free intracommunity delivery"})

        elif self.partner_id.country_id.name == 'Netherlands':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  intracommunautaire levering"})

        elif self.partner_id.country_id.name == 'Austria':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  steuerfreie innergemeinschaftliche Lieferung"})

        elif self.partner_id.country_id.name == 'Poland':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  wewnatrzwspólnotowa dostawa towarów opodatkowana wg. stawki podatku 0% (Art.42 Ust. 0 pod. od tow.il usl.*)"})

        elif self.partner_id.country_id.name == 'Portugal':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  fornecimento inter-comunitário isento de IVA"})

        elif self.partner_id.country_id.name == 'Romania':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  Livrare intracomunitara scutita de TVA."})

        elif self.partner_id.country_id.name == 'Sweden':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  skattefri gemenskapsintern leverans"})

        elif self.partner_id.country_id.name == 'Slovakia':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  od dane oslobodené intrakomunitárne dodávky"})

        elif self.partner_id.country_id.name == 'Slovenia':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  oproscena dobava znotraj skupnosti"})

        elif self.partner_id.country_id.name == 'Spain':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  entrega intracomunitaria libre de impuesto"})

        elif self.partner_id.country_id.name == 'Czech Republic':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  dodání zbozí do jiného clenského státu, osvobozené od DPH"})

        elif self.partner_id.country_id.name == 'Hungary':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  forgalmiadó-mentes, Közösségenbelülrol történo áruszállítás"})

        elif self.partner_id.country_id.name == 'Cyprus':
            self.update({'reverse_charg_note_german': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /", 'reverse_charg_note_france' : "  tax free intracommunity delivery"})

