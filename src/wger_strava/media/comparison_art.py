"""Original local SVG illustrations for the reference-weight catalog."""
from html import escape

from .art import elephant


def wheels(*centers, radius=30):
    return ''.join(f'<circle cx="{x}" cy="285" r="{radius}" fill="var(--ear)"/>'
                   f'<circle cx="{x}" cy="285" r="{radius // 2}" fill="var(--muted)"/>' for x in centers)


def windows(xs, y=160, width=40, height=45):
    return ''.join(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="5" fill="var(--panel)"/>' for x in xs)


def whale(kind):
    dorsal = 'M390 151Q410 53 448 140Z' if kind == 'orca' else 'M390 151L422 105 442 145Z'
    extra = {
        'orca': '<ellipse cx="259" cy="176" rx="33" ry="17" fill="#dcecff"/><path d="M179 227Q295 235 431 207Q352 288 196 245Z" fill="#dcecff"/>',
        'whale_shark': ''.join(f'<circle cx="{x}" cy="{y}" r="4" fill="#dcecff"/>' for x in range(220,490,35) for y in (159,185,211)),
        'humpback': '<path d="M321 224Q360 345 453 309L374 220Z" fill="var(--ear)"/>',
        'blue_whale': '<path d="M175 225Q319 264 472 203" fill="none" stroke="var(--ear)" stroke-width="9"/>',
    }[kind]
    return f'<path d="M139 198Q172 113 340 135Q482 131 568 204L637 133 625 205 666 254 569 236Q409 288 224 260Q150 249 139 198Z"/><path d="{dorsal}"/>{extra}<circle cx="185" cy="191" r="5" fill="var(--panel)"/>'


def illustration(key, label=''):
    if key == 'elephant':
        return elephant().replace('Original elephant illustration', escape(label or 'African elephant', quote=True)+' illustration')
    if key in {'orca', 'whale_shark', 'humpback', 'blue_whale'}:
        shapes = whale(key)
    else:
        shapes = SHAPES[key] if key is not None else '<path d="M260 165V245M285 140V270M310 205H450M475 140V270M500 165V245" fill="none" stroke="var(--animal)" stroke-width="20" stroke-linecap="round"/>'
    return ('<svg viewBox="0 0 760 370" role="img" aria-label="'+escape(label, quote=True)+' illustration">'
            '<ellipse cx="380" cy="337" rx="275" ry="11" fill="currentColor" opacity=".07"/>'
            '<g fill="var(--animal)" stroke-linejoin="round" stroke-linecap="round">'+shapes+'</g></svg>')


SHAPES = {
    'hippo': '<rect x="175" y="140" width="350" height="150" rx="73"/><rect x="433" y="166" width="178" height="111" rx="46"/><path d="M218 250V319H265V250M425 250V319H472V250"/><circle cx="492" cy="157" r="18"/><circle cx="552" cy="197" r="6" fill="var(--panel)"/><path d="M511 245H580" stroke="var(--ear)" stroke-width="5"/>',
    'container': '<path d="M133 125L574 93 627 125V295L185 315 133 286Z"/><path d="M185 148L627 125M185 148V315" fill="none" stroke="var(--ear)" stroke-width="8"/>'+''.join(f'<path d="M{x} 153V293" stroke="var(--ear)" stroke-width="6"/>' for x in range(215,610,33)),
    'pickup': '<path d="M129 203H329L368 134H492L553 200H609L634 268H128Z"/><path d="M382 151H478L521 199H354Z" fill="var(--panel)"/>'+wheels(232,533),
    'forklift': '<path d="M209 208H413V279H184V239Z"/><path d="M266 207V116H389V211M448 100V287H580M469 100V268" fill="none" stroke="var(--ear)" stroke-width="15"/><path d="M281 194V137H371V194Z" fill="var(--panel)"/>'+wheels(237,393),
    'tractor': '<path d="M182 277V171L217 125H323V207H424L477 256V277Z"/><path d="M218 145H301V193H203Z" fill="var(--panel)"/><path d="M326 216H552V269H326Z" fill="var(--ear)"/>'+wheels(239,440,514),
    'bus': '<rect x="112" y="126" width="540" height="153" rx="26"/>'+windows(range(144,603,60))+ '<path d="M118 233H642" stroke="var(--ear)" stroke-width="8"/>'+wheels(214,554),
    'bell': '<path d="M344 83Q344 48 380 48Q416 48 416 83L405 103H355Z" fill="var(--ear)"/><path d="M306 124Q312 91 380 91Q448 91 454 124L483 254 528 281Q540 303 507 305H253Q220 303 232 281L277 254Z"/><path d="M251 280H510M300 140H460" stroke="var(--ear)" stroke-width="9"/><circle cx="380" cy="310" r="21" fill="var(--ear)"/>',
    'excavator': '<rect x="170" y="269" width="350" height="57" rx="28" fill="var(--ear)"/><path d="M200 262V195H342V135H425V262Z"/><path d="M356 151H411V212H356Z" fill="var(--panel)"/><path d="M443 183L503 104 587 154 609 242" fill="none" stroke="var(--animal)" stroke-width="29"/><path d="M568 236L635 225 651 274Q612 309 576 279Z" fill="var(--ear)"/>',
    'stonehenge': '<path d="M215 137L287 126 278 319 204 319Z M448 126L521 139 537 319H451Z"/><path d="M189 93L539 84 559 141 185 155Z" fill="var(--ear)"/>',
    'semi': '<rect x="90" y="120" width="380" height="139" rx="8"/><path d="M485 165H573L630 216V276H485Z"/><path d="M503 178H562L601 215H503Z" fill="var(--panel)"/>'+wheels(170,234,482,588, radius=25),
    'subway': '<rect x="99" y="126" width="563" height="157" rx="24"/>'+windows([125,181,311,367,497,553],width=42)+'<path d="M244 151H288V277H244Z M430 151H474V277H430Z" fill="var(--ear)"/><path d="M96 309H665M110 325H650" stroke="var(--ear)" stroke-width="6"/>',
    'locomotive': '<path d="M115 260V191H167V132H290V170H589L632 260Z"/><path d="M185 150H265V199H185Z" fill="var(--panel)"/>'+windows(range(328,560,46),y=188,width=23,height=43)+'<path d="M99 274H653" stroke="var(--ear)" stroke-width="13"/>'+wheels(180,242,492,554,radius=22),
    'liberty': '<path d="M306 320L328 159 361 142H397L434 319Z M330 164L272 108 282 89 358 146Z M399 166L444 187 432 230 404 202Z"/><circle cx="378" cy="120" r="25"/><path d="M350 105L338 84 363 95 367 70 379 94 395 73 396 100 418 88 404 113Z" fill="var(--ear)"/><path d="M266 91V58H292V91Z M263 54Q256 26 281 12Q300 41 290 54Z"/><path d="M352 193L341 305M380 178V310M403 225L416 305" stroke="var(--ear)" stroke-width="7"/>',
    'iss': '<g transform="rotate(-16 380 190)"><rect x="293" y="167" width="173" height="47" rx="18"/><path d="M380 116V270M162 191H600" stroke="var(--ear)" stroke-width="15"/>'+''.join(f'<rect x="{x}" y="{y}" width="92" height="100" rx="3" fill="var(--ear)" stroke="var(--accent)" stroke-width="3"/>' for x in (160,255,415,510) for y in (70,215))+'<path d="M286 190H474M380 141V237" stroke="var(--animal)" stroke-width="16"/></g>',
    'a380': '<path d="M104 219Q128 193 211 190H356L285 91H330L448 190H550L591 128H625L607 202Q680 213 641 232L441 242 323 314H269L351 243H189L151 273H119L135 235Z"/><path d="M217 207H540" stroke="var(--ear)" stroke-width="6"/><path d="M590 152L598 198H573Z" fill="var(--ear)"/>',
    'mining_truck': '<path d="M133 126H447L419 221H175Z M429 214V165H535L575 214H620V278H171V234Z"/><path d="M447 179H523L547 214H447Z" fill="var(--panel)"/>'+wheels(242,539,radius=44),
    'saturn_v': '<path d="M349 269V80L380 24 411 80V269L431 317H329Z"/><path d="M349 109H411V126H349Z M349 189H411V219H349Z M349 251H411V270H349Z" fill="var(--ear)"/><path d="M350 296L332 323H350M410 296L428 323H410" fill="var(--ear)"/>',
    'bunker_hill': '<path d="M322 309L337 96 380 33 423 96 438 309Z"/><path d="M311 310H449V329H311Z" fill="var(--ear)"/><path d="M380 39V309" stroke="var(--ear)" stroke-width="5"/>',
    'eiffel': '<path d="M372 30H388L404 130 429 202 493 323H447Q416 238 380 238Q344 238 313 323H267L331 202 356 130Z"/><path d="M325 194H435M349 133H412M305 250H455M350 148L411 191M405 148L341 191" stroke="var(--ear)" stroke-width="9"/>',
    'pisa': '<g transform="rotate(9 380 320)"><path d="M319 313V107Q380 77 441 107V313Z"/><path d="M333 98V66Q380 46 427 66V98Z" fill="var(--ear)"/>'+''.join(f'<path d="M315 {y}H445" stroke="var(--ear)" stroke-width="8"/>' for y in range(119,310,32))+''.join(f'<path d="M{x} 122V303" stroke="var(--panel)" stroke-width="5"/>' for x in range(330,440,21))+'</g>',
    'washington': '<path d="M337 309L352 89 380 27 408 89 423 309Z"/><path d="M307 311H453V333H307Z M380 28L408 89 423 309H380Z" fill="var(--ear)"/>',
    'carrier': '<path d="M99 216L660 216 606 290H175Z"/><path d="M112 198L642 177 668 215H98Z" fill="var(--ear)"/><path d="M458 179V124H527V178Z M477 125V98H507V125Z"/><path d="M493 98V65" stroke="var(--accent)" stroke-width="7"/><path d="M180 207L397 198M244 192L286 190" stroke="var(--muted)" stroke-width="4"/>',
    'empire_state': '<path d="M282 325V196H311V134H335V84H360V52H400V84H425V134H449V196H478V325Z"/><path d="M380 16V59" stroke="var(--accent)" stroke-width="7"/>'+''.join(f'<path d="M{x} 156V309" stroke="var(--ear)" stroke-width="6"/>' for x in range(329,443,18)),
    'golden_gate': '<path d="M220 93V320M259 93V320M500 93V320M539 93V320M220 129H259M220 189H259M500 129H539M500 189H539" stroke="var(--animal)" stroke-width="15"/><path d="M89 278H671" stroke="var(--ear)" stroke-width="16"/><path d="M89 249Q148 219 239 101Q380 365 519 101Q609 219 671 249" fill="none" stroke="var(--accent)" stroke-width="6"/>'+''.join(f'<path d="M{x} {int(110+155*(1-((x-380)/140)**2))}V271" stroke="var(--ear)" stroke-width="3"/>' for x in range(280,500,25)),
    'pyramid': '<path d="M124 316L380 52 639 316Z"/><path d="M380 52L433 316H639Z" fill="var(--ear)"/><path d="M205 274H418M247 231H408M290 187H400M332 143H392" stroke="var(--ear)" stroke-width="4"/>',
}
