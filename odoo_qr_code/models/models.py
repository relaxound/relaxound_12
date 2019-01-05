# -*- coding: utf-8 -*-

import base64
from io import BytesIO
import pip

try:
    import qrcode
except ImportError:
    print('\n There was no such module named -qrcode- installed')
    print('xxxxxxxxxxxxxxxx installing qrcode xxxxxxxxxxxxxx')
    pip.main(['install', 'qrcode'])
    
from odoo import models, fields, api


class ProductTemplateQRCode(models.Model):
    _inherit = 'product.template'

    @api.multi
    @api.depends('product_qr_code')
    def _generate_qr_code(self):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
        if self.product_qr_code:
            name = self.product_qr_code + '_product.png'
            qr.add_data(self.product_qr_code)
            qr.make(fit=True)
            img = qr.make_image()
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qrcode_img = base64.b64encode(buffer.getvalue())
            self.update({'qr_code': qrcode_img, 'qr_code_name': name})

    product_qr_code = fields.Char('QR Code')
    qr_code = fields.Binary('QR Code Image', compute="_generate_qr_code")
    qr_code_name = fields.Char(default="qr_code.png")


class ProductProductQRCode(models.Model):
    _inherit = 'product.product'

    @api.multi
    @api.depends('product_qr_code')
    def _generate_qr_code(self):
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=20, border=4)
        if self.product_qr_code:
            name = self.product_qr_code + '_product.png'
            qr.add_data(self.product_qr_code)
            qr.make(fit=True)
            img = qr.make_image()
            buffer = cStringIO.StringIO()
            img.save(buffer, format="PNG")
            qrcode_img = base64.b64encode(buffer.getvalue())
            self.update({'qr_code': qrcode_img, 'qr_code_name': name})
