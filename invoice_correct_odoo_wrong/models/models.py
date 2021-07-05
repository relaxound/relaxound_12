from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class CustomInvoiceCorrect(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_correct(self, vals_list):
        invoice_idd = [self.id]
        for rec in invoice_idd:
            obj = self.env['account.invoice.line'].search([('invoice_id','=',rec)])
            obj._compute_price()
        return vals_list
        # return super(CustomInvoiceCorrect,self).invoice_correct(vals_list)

class UpdateNewPricelist(models.Model):
    _inherit = 'res.partner'

    def new_pricelist(self):
        list = [345519, 505780, 474071, 474073, 474072, 345516, 345517, 345518, 457605, 457606, 502836, 504416, 441856, 445935, 499833, 499835, 499834, 483026, 483027, 505912, 505913, 403426, 488125, 488127, 488126, 345522, 498447, 345523, 345521, 345524, 345525, 345526, 345527, 472996, 345533, 345539, 345540, 345621, 345622, 468363, 345659, 345660, 345661, 346973, 346974, 486918, 486919, 345528, 345529, 471577, 471578, 347003, 483366, 483367, 459557, 497727, 345633, 501413, 501414, 345663, 454114, 404291, 482307, 487261, 428484, 347098, 479314, 483403, 479315, 483404, 345586, 345624, 345623, 403440, 472113, 442319, 419070, 419071, 419072, 347095, 347096, 429658, 429659, 457607, 457608, 402502, 482325, 482306, 480350, 480351, 345625, 499487, 428442, 458729, 345838, 455659, 490432, 490433, 441862, 441863, 441861, 455660, 455661, 443771, 443772, 403458, 345881, 490794, 490795, 346039, 443775, 441868, 502218, 502219, 346695, 487964, 487965, 498861, 498862, 490834, 490835, 495617, 495618, 346848, 346849, 445957, 488577, 417050, 417051, 483455, 417052, 482727, 346913, 346914, 346915, 428481, 346916, 346917, 346955, 346954, 462182, 463192, 463193, 458013, 457638, 346976, 346977, 346980, 498103, 488788, 488794, 488795, 501510, 500809, 488789, 485999, 486000, 457639, 457640, 495803, 434832, 414469, 464550, 464551, 499186, 499187, 480223, 480224, 439465, 505738, 505739, 482851, 482852, 345530, 345531, 345532, 459084, 459085, 458727, 471754, 471755, 345534, 443768, 345535, 503299, 434811, 462095, 462093, 462094, 498759, 434812, 345541, 345542, 417044, 479661, 417045, 468644, 345543, 470352, 478293, 478295, 478294, 345545, 439466, 345546, 489231, 489232, 406396, 345547, 345548, 501549, 501550, 345549, 416513, 474983, 474984, 345552, 490255, 490256, 474569, 474570, 345553, 345554, 345556, 487863, 487864, 345555, 504064, 504065, 345557, 345558, 470369, 470370, 345559, 496119, 496120, 345561, 473567, 473568, 470412, 470413, 470809, 470810, 497527, 497528, 345563, 494767, 494768, 345562, 498335, 498336, 492282, 492283, 493253, 472070, 493254, 472071, 457609, 505791, 505792, 478429, 478430, 478433, 478434, 345564, 345565, 345566, 345567, 345568, 496262, 496263, 504011, 504012, 345569, 345570, 489646, 489647, 478704, 478705, 345571, 345572, 463609, 463610, 499974, 499975, 470726, 470727, 495370, 495371, 468362, 504430, 504431, 459556, 484065, 484066, 466248, 466249, 445936, 469438, 469439, 345573, 450705, 476139, 476140, 503191, 402503, 403355, 403356, 482379, 480680, 345574, 345575, 345579, 485885, 485886, 470828, 470829, 502212, 502213, 345580, 456468, 487357, 487358, 345584, 345583, 345582, 345581, 345576, 345577, 345578, 479083, 479084, 498916, 498918, 498917, 498919, 496012, 496013, 345585, 480263, 480264, 417046, 462096, 345588, 345589, 345590, 447887, 440952, 345591, 345592, 464217, 464218, 491242, 491243, 345593, 459558, 488411, 498265, 497537, 488412, 498264, 345595, 345596, 345597, 479301, 406397, 491223, 406398, 345598, 345599, 345600, 345601, 345603, 345604, 414428, 503241, 503242, 451956, 345606, 484163, 484164, 465291, 465292, 416514, 345607, 345608, 345609, 345610, 476721, 476722, 345611, 459559, 345612, 345613, 345614, 472761, 472762, 450976, 345616, 454072, 345617, 345618, 345605, 497602, 497603, 477548, 477549, 440175, 4439467, 478199, 345619, 345620, 455650, 474114, 474115, 345626, 490506, 490507, 463479, 468870, 469125, 463480, 469126, 468871, 345627, 345628, 502561, 495682, 502562, 495683, 462097, 441857, 480086, 480087, 479037, 479038, 345629, 403439, 457610, 345630, 345631, 345632, 345634, 345635, 345636, 345637, 345638, 455651, 455652, 345640, 345641, 473963, 473964, 345639, 495407, 495408, 345643, 505354, 505355, 500212, 485239, 485240, 345644, 492523, 492524, 345645, 345646, 499662, 499663, 345647, 345648, 345649, 463421, 463422, 428440, 464656, 464657, 504114, 504115, 487716, 487717, 345651, 503571, 503572, 345652, 455653, 416515, 345653, 472284, 472285, 502615, 502616, 491625, 491626, 428441, 493039, 493040, 345654, 451957, 479150, 479151, 345655, 458728, 442318, 345656, 345657, 419058, 463577, 463578, 490693, 490694, 487567, 487568, 345662, 501643, 501644, 470439, 470440, 505114, 505115, 475782, 475783, 497693, 497694, 402504, 496912, 496913, 505445, 505446, 345664, 345665, 494302, 494303, 500926, 500927, 345773, 497022, 497023, 493600, 493601, 480578, 480579, 500782, 500783, 345779, 495741, 495742, 466600, 466601, 345781, 440804, 464007, 464008, 345782, 485021, 485022, 443769, 345666, 478411, 476686, 478412, 476687, 498163, 498164, 497049, 497050, 345667, 345668, 486443, 486444, 464211, 464212, 489004, 345772, 441858, 441859, 345669, 466701, 502534, 466702, 502535, 345670, 494735, 494736, 345671, 345672, 505169, 505170, 345673, 441081, 505080, 505081, 503255, 503256, 498353, 498354, 488278, 488279, 475610, 475611, 345674, 481414, 481415, 483903, 483904, 345675, 462098, 500885, 500886, 414429, 428443, 468364, 431267, 431268, 504652, 504653, 501431, 501432, 345676, 493726, 493727, 487278, 487279, 345677, 500558, 500559, 345678, 345679, 450707, 447888, 493324, 493325, 345680, 345681, 473777, 473778, 495379, 495380, 345682, 480597, 480598, 481073, 345683, 502681, 502682, 345684, 487207, 487208, 466018, 466019, 439470, 489537, 497416, 489538, 345685, 495937, 495938, 454466, 454073, 454467, 345686, 450977, 345687, 345688, 476438, 476439, 483490, 483491, 484731, 485512, 484732, 485513, 459560, 498832, 493143, 498833, 493144, 345689, 345690, 462099, 463270, 345691, 428444, 345692, 492617, 492618, 464517, 464518, 345693, 345694, 345696, 345697, 466695, 466696, 345695, 345698, 402505, 495607, 495608, 345700, 345701, 345699, 458730, 496474, 496475, 482373, 492020, 482374, 470084, 470085, 345702, 403441, 345703, 503740, 503741, 345704, 434813, 402506, 345705, 495826, 495827, 345706, 345707, 471524, 471525, 345708, 345709, 492983, 492984, 408743, 464283, 464284, 497038, 497039, 498301, 498302, 466936, 466937, 464598, 464599, 463617, 463618, 494357, 494358, 428445, 496818, 496819, 485111, 485112, 345710, 464746, 464747, 462100, 414430, 487903, 484775, 484776, 487904, 471420, 471421, 428446, 474136, 474137, 345711, 494668, 494669, 440857, 345712, 501459, 501460, 345713, 345714, 471711, 471712, 480699, 480700, 475405, 475406, 504490, 504491, 345716, 468365, 345715, 478933, 478934, 345717, 476301, 503663, 503664, 345718, 345719, 419059, 488650, 488651, 495571, 495572, 345720, 482637, 482638, 345721, 502111, 502112, 457611, 345722, 482404, 482405, 345723, 495541, 495542, 484371, 484372, 445937, 499982, 499983, 497689, 500578, 497690, 500579, 467088, 491224, 491225, 477307, 477308, 345726, 472218, 472219, 500197, 500198, 345724, 463703, 463704, 345725, 450978, 402507, 450708, 495206, 495207, 439471, 345727, 501595, 501596, 434814, 345728, 491719, 491720, 444452, 404357, 404285, 404286, 455654, 492509, 492510, 345729, 345730, 503071, 503072, 472038, 472039, 499692, 499693, 504881, 504882, 473038, 473039, 471939, 471940, 345731, 475324, 475325, 490936, 490937, 500393, 500394, 481388, 481389, 454074, 471996, 471997, 480124, 480869, 480125, 480870, 345732, 345733, 345734, 479148, 479149, 478690, 478691, 477812, 477837, 477813, 477838, 345735, 345736, 487845, 487846, 444453, 345737, 494897, 494898, 500916, 500917, 402508, 345739, 442058, 345740, 470207, 470208, 445938, 464285, 494554, 464286, 464513, 464514, 462101, 345741, 466368, 466369, 345742, 480126, 480127, 466950, 466951, 345743, 345744, 494654, 494655, 494929, 494930, 463995, 463996, 345745, 345746, 345747, 475953, 451408, 487255, 487256, 503259, 503260, 502032, 444454, 345748, 462102, 463232, 463233, 471083, 471084, 502565, 502566, 472232, 472233, 492551, 492552, 495224, 495225, 345749, 345750, 345751, 495659, 495660, 466012, 466013, 481524, 481525, 499340, 499341, 345752, 345753, 414431, 473200, 473201, 345754, 474759, 474760, 474597, 474598, 471162, 471163, 490326, 490327, 462103, 491211, 491212, 345755, 481514, 345756, 345757, 476334, 476335, 505640, 505641, 345758, 505394, 505395, 481324, 486346, 481325, 486347, 505224, 505225, 489793, 493987, 489794, 493988, 494152, 494153, 481945, 481946, 345759, 345760, 504252, 504253, 485174, 485175, 466458, 466459, 345761, 345764, 487563, 487657, 487564, 487658, 345765, 479023, 479024, 444455, 345766, 345767, 345768, 345769, 462104, 456469, 462105, 470934, 470935, 470544, 470545, 345770, 402509, 478310, 478311, 499486, 490482, 494388, 490483, 494389, 402510, 345771, 450979, 495761, 495762, 476952, 476953, 505265, 505266, 487440, 487441, 345774, 462106, 463238, 463239, 345775, 345777, 345776, 345778, 345780, 501553, 501554, 480433, 480434, 345783, 477951, 477952, 402511, 482237, 482238, 345785, 345786, 492886, 492887, 485756, 485757, 484933, 484934, 345787, 345788, 469292, 469293, 467016, 467017, 345789, 345791, 480829, 480830, 502019, 502020, 462107, 485077, 485078, 345792, 345794, 475991, 475992, 455655, 455656, 472901, 472902, 345795, 345796, 468366, 439472, 345797, 451409, 345798, 345799, 492280, 492281, 492158, 492159, 498552, 498553, 486926, 486927, 502639, 502640, 345800, 483472, 483473, 495896, 495897, 471478, 471479, 489533, 489534, 489727, 489728, 345801, 455657, 345802, 503838, 503839, 484006, 484007, 486129, 486130, 345803, 345804, 502997, 502998, 485452, 485453, 484834, 493629, 484835, 503116, 503117, 484980, 484981, 493888, 493889, 491085, 491086, 345805, 503269, 503270, 492555, 492556, 345806, 493497, 493498, 474344, 474345, 439473, 464097, 464098, 496828, 496829, 480884, 480885, 481220, 481221, 345808, 497513, 497514, 345809, 455658, 493792, 493793, 345815, 496346, 496347, 345810, 345811, 505100, 505101, 495663, 495664, 501804, 501805, 428447, 345812, 345813, 345814, 345817, 345816, 464243, 464244, 464666, 464667, 472506, 472507, 494333, 494334, 345818, 474575, 474576, 345819, 345820, 416516, 416517, 468525, 496866, 496867, 475679, 475680, 480602, 406399, 419061, 419060, 465688, 465689, 482778, 482779, 345822, 501940, 501941]
        for j in list:
            p = int(j)
            all_customers = self.env['res.partner'].search([('id','=',p)])
            error_msg1 = _('all customer====== (%s)') % (all_customers)
            _logger.info(error_msg1)
            for i in all_customers:
                try:
                    if i.customer == True and i.supplier == False and i.is_retailer == False and i.property_product_pricelist.name == "Public Pricelist":
                        change_pricelist =self.env['product.pricelist'].search([('id','=',824)]).id
                        i.property_product_pricelist = change_pricelist
                        error_msg = _('property_product_pricelist====== (%s)') % (i.property_product_pricelist.name)
                        _logger.info(error_msg)
                except Exception:
                    error_msg2 = _('INVALID ID====== (%s)') % (i)
                    _logger.info(error_msg2)
                    pass
