# Analysiere deine feste_ausgaben Struktur
analyze_feste_ausgaben_struktur(conn)

# Hole Jahresübersicht-Daten zur Verifikation  
get_jahresuebersicht_daten_zur_verifikation(conn, 2025)

# Berechne und verifiziere
verify_jahresuebersicht_calculation(conn, 2025)

# Berechne und speichere alles
berechne_und_speichere_soll_kontostaende(conn, 2025)