from odoo import models, api, fields

class InvoiceJournalField(models.Model):
    _inherit = 'account.invoice'

    reverse_charg_note = fields.Text(string='REVERSE CHARGE',compute='_set_reverse_charge')

    @api.multi
    def _set_reverse_charge(self):
        if self.partner_id.country_id.name == 'Belgium':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  livraison intracommunautaire exonérée TVA"})

        elif self.partner_id.country_id.name == 'Bulgaria':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  Neoblagaema vatreshnoobshtnostna dostavka"})

        elif self.partner_id.country_id.name == 'Denmark':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  momsfri EU levering"})

        elif self.partner_id.country_id.name == 'Estonia':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  käibemaksuvaba ühendusesisene kättetoimetamine"})

        elif self.partner_id.country_id.name == 'Finland':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  veroton yhteisömyynti"})

        elif self.partner_id.country_id.name == 'France':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  livraison intracommunautaire exonérée TVA"})

        elif self.partner_id.country_id.name == 'Greece':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  tax free intracommunity delivery"})

        elif self.partner_id.country_id.name == 'Ireland':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  tax free intracommunity despatch"})

        elif self.partner_id.country_id.name == 'Italy':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  cessioni intracomunitarie esenti"})

        elif self.partner_id.country_id.name == 'Latvia':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  Ar 0% apliekamas precu piegades ES ietvaros, PVN likuma 28. pants*)"})

        elif self.partner_id.country_id.name == 'Lithuania':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  pridétinés vertés mokesciu neapmokestinamas tiekimas Europos Sajungos viduje"})

        elif self.partner_id.country_id.name == 'Luxembourg':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  livraison intracommunautaire exonérée TVA."})

        elif self.partner_id.country_id.name == 'Malta':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  tax free intracommunity delivery"})

        elif self.partner_id.country_id.name == 'Netherlands':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  intracommunautaire levering"})

        elif self.partner_id.country_id.name == 'Austria':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  steuerfreie innergemeinschaftliche Lieferung"})

        elif self.partner_id.country_id.name == 'Poland':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  wewnatrzwspólnotowa dostawa towarów opodatkowana wg. stawki podatku 0% (Art.42 Ust. 0 pod. od tow.il usl.*)"})

        elif self.partner_id.country_id.name == 'Portugal':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  fornecimento inter-comunitário isento de IVA"})

        elif self.partner_id.country_id.name == 'Romania':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  Livrare intracomunitara scutita de TVA."})

        elif self.partner_id.country_id.name == 'Sweden':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  skattefri gemenskapsintern leverans"})

        elif self.partner_id.country_id.name == 'Slovakia':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  od dane oslobodené intrakomunitárne dodávky"})

        elif self.partner_id.country_id.name == 'Slovenia':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  oproscena dobava znotraj skupnosti"})

        elif self.partner_id.country_id.name == 'Spain':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  entrega intracomunitaria libre de impuesto"})

        elif self.partner_id.country_id.name == 'Czech Republic':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  dodání zbozí do jiného clenského státu, osvobozené od DPH"})

        elif self.partner_id.country_id.name == 'Hungary':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  forgalmiadó-mentes, Közösségenbelülrol történo áruszállítás"})

        elif self.partner_id.country_id.name == 'Cyprus':
            self.update({'reverse_charg_note': "steuerfreie innergemeinschaftliche Lieferung gem. § 4 Nr. 1b UStG /  tax free intracommunity delivery"})

