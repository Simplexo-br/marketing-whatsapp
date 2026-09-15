# -*- coding: utf-8 -*-
import re

def extract_best_brazilian_mobile(raw_number):
    if not raw_number:
        return False
    digits = re.sub(r'[^0-9]', '', str(raw_number))
    
    # Se começar com 55 e tiver 12 ou 13 dígitos, já está correto
    if digits.startswith('55') and len(digits) in [12, 13]:
        # Validar se após 55 tem DDD válido (11 a 99)
        ddd = int(digits[2:4])
        if 11 <= ddd <= 99:
            return f"+{digits}"
            
    # Se tiver 10 ou 11 dígitos sem 55
    if len(digits) in [10, 11]:
        ddd = int(digits[0:2])
        if 11 <= ddd <= 99:
            return f"+55{digits}"
            
    # Se tiver mais de 11 dígitos (múltiplos números concatenados)
    # Procurar primeiro padrão de celular brasileiro: DDD (11-99) + 9 + 8 dígitos = 11 dígitos
    mobiles = re.findall(r'(?:55)?([1-9][1-9]9[0-9]{8})', digits)
    if mobiles:
        return f"+55{mobiles[0]}"
        
    # Se não achou celular com 9, procurar fixo: DDD (11-99) + [2-5] + 7 dígitos = 10 dígitos
    landlines = re.findall(r'(?:55)?([1-9][1-9][2-5][0-9]{7})', digits)
    if landlines:
        return f"+55{landlines[0]}"
        
    return False

# Testes com os números encontrados
samples = [
    '+1198796280011999812398',
    '+153263525715997723172',
    '+9898161237099981761612',
    '+179883040041732324466',
    '+1730110602179882854341732324466',
    '+313362205631988078573',
    '+114594641011993983121'
]

for s in samples:
    print(f"{s} => {extract_best_brazilian_mobile(s)}")
