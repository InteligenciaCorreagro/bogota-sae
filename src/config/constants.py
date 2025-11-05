"""
Constantes y configuración para el procesador de facturas
"""

# Namespaces UBL estándar para Colombia
NAMESPACES = {
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'sts': 'dian:gov:co:facturaelectronica:Structures-2-1',
}

# Mapeo de códigos de moneda
CURRENCY_CODE_MAP = {
    'COP': '1',
    'USD': '2',
    'EUR': '3'
}

# Mapeo de unidades de medida
UNIT_MAP = {
    'KG': 'Kg',
    'KGM': 'Kg',
    'LBR': 'Kg',
    'LTR': 'Lt',
    'LT': 'Lt',
    'NIU': 'Un',
    'EA': 'Un',
    'EV': 'Un',
    'JR': 'Un',
    'UN': 'Un'
}

# Encabezados de Excel para formato REGGIS
REGGIS_HEADERS = [
    'N° Factura',
    'Nombre Producto',
    'Codigo Subyacente',
    'Unidad Medida en Kg,Un,Lt',
    'Cantidad (5 decimales - separdor coma)',
    'Precio Unitario (5 decimales - separdor coma)',
    'Fecha Factura Año-Mes-Dia',
    'Fecha Pago Año-Mes-Dia',
    'Nit Comprador (Existente)',
    'Nombre Comprador',
    'Nit Vendedor (Existente)',
    'Nombre Vendedor',
    'Principal V,C',
    'Municipio (Nombre Exacto de la Ciudad)',
    'Iva (N°%)',
    'Descripción',
    'Activa Factura',
    'Activa Bodega',
    'Incentivo',
    'Cantidad Original (5 decimales - separdor coma)',
    'Moneda (1,2,3)',
    'Total Sin IVA',
    'Total IVA',
    'Total Con IVA'
]
