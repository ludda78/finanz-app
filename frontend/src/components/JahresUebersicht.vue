<template>
  <div class="jahresuebersicht-container">
    <h2>Jahresübersicht der festen Ausgaben und Einnahmen</h2>
    
    <div v-if="loading" class="loading">
      Daten werden geladen...
    </div>
    
    <div v-else-if="error" class="error">
      Fehler beim Laden der Daten: {{ error }}
    </div>
    
    <div v-else class="jahresuebersicht">
      <div class="summary-box">
        <div class="summary-item">
          <span class="label">Monatliches Ausgaben-Mittel (ohne Anteile Andrea):</span>
          <span class="value">{{ formatCurrency(monatlicheAusgabenOhneAndrea) }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Monatliches Einnahmen-Mittel (ohne Anteile Andrea):</span>
          <span class="value">{{ formatCurrency(monatlicheEinnahmenOhneAndrea) }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Jahres-Saldo (ohne Anteile Andrea):</span>
          <span class="value" :class="jahresSaldoOhneAndrea >= 0 ? 'positive' : 'negative'">
            {{ formatCurrency(jahresSaldoOhneAndrea) }}
          </span>
        </div>
		<div class="summary-item">
          <span class="label">Monatlicher Saldo (ohne Anteile Andrea):</span>
          <span class="value" :class="saldoProMonat >= 0 ? 'positive' : 'negative'">
            {{ formatCurrency(saldoProMonat) }}
          </span>
        </div>
      </div>
      
      <!-- Haupt-Tabelle mit Monaten als Spalten und Posten als Zeilen (ohne Anteile Andrea) -->
      <div class="table-container">
        <table class="posten-matrix-tabelle">
          <thead>
            <tr>
              <th>Posten / Monat</th>
              <th v-for="monat in 12" :key="'monat-'+monat">{{ getMonatName(monat) }}</th>
              <th>Durchschn. monatl. Kosten</th>
            </tr>
          </thead>
          <tbody>
            <!-- Gruppiere nach Kategorie und dann nach Posten (ohne Anteile Andrea) -->
            <template v-for="(kategorieItems, kategorie) in gruppiertNachKategorieOhneAndrea" :key="kategorie">
              <tr class="kategorie-header">
                <td>{{ kategorie }}</td>
                <td colspan="12"></td>
                <td>{{ formatCurrency(getKategorieDurchschnitt(kategorie)) }}</td>
              </tr>
  
              <tr v-for="posten in kategorieItems" :key="posten.id">
                <td>{{ posten.beschreibung }}</td>
                <td v-for="monat in 12" :key="'posten-'+posten.id+'-'+monat">
                  {{ getPostenBetragFuerMonat(posten.id, monat) }}
                </td>
                <td>{{ formatCurrency(getPostenDurchschnitt(posten.id)) }}</td>
              </tr>
            </template>
          </tbody>
          <tfoot>
            <!-- Summen pro Monat (ohne Anteile Andrea) -->
            <tr class="summe-zeile">
              <td><strong>Summe Ausgaben</strong></td>
              <td v-for="monat in 12" :key="'summe-'+monat">
                {{ getMonatsSummeOhneAndrea(monat, 'ausgaben') }}
              </td>
              <td><strong>{{ formatCurrency(monatlicheAusgabenOhneAndrea) }}</strong></td>
            </tr>
            
            <!-- Virtuelle Kontostände (ohne Anteile Andrea) -->
            <tr>
              <td><strong>Virtueller Kontostand</strong></td>
              <td v-for="monat in 12" :key="'kontostand-'+monat" 
                  :class="getVirtuellerKontostandOhneAndrea(monat) >= 0 ? 'positive' : 'negative'">
                {{ formatCurrency(getVirtuellerKontostandOhneAndrea(monat)) }}
              </td>
              <td></td>
            </tr>
            
            <!-- Delta zum Mittel (ohne Anteile Andrea) -->
            <tr>
              <td><strong>Delta zum Mittel</strong></td>
              <td v-for="monat in 12" :key="'delta-'+monat" 
                  :class="getDeltaZumMittelOhneAndrea(monat) >= 0 ? 'positive' : 'negative'">
                {{ formatCurrency(getDeltaZumMittelOhneAndrea(monat)) }}
              </td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
      
      <!-- Separate Tabelle für Anteile Andrea -->
      <div class="anteile-andrea-section">
        <h3>Anteile Andrea</h3>
        <div class="summary-box">
          <div class="summary-item">
            <span class="label">Monatliches Ausgaben-Mittel:</span>
            <span class="value">{{ formatCurrency(monatlicheAusgabenAndrea) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">Monatliches Einnahmen-Mittel:</span>
            <span class="value">{{ formatCurrency(monatlicheEinnahmenAndrea) }}</span>
          </div>
          <div class="summary-item">
            <span class="label">Jahres-Saldo:</span>
            <span class="value" :class="jahresSaldoAndrea >= 0 ? 'positive' : 'negative'">
              {{ formatCurrency(jahresSaldoAndrea) }}
            </span>
          </div>
        </div>
        
        <div class="table-container">
          <table class="posten-matrix-tabelle">
            <thead>
              <tr>
                <th>Posten / Monat</th>
                <th v-for="monat in 12" :key="'andrea-monat-'+monat">{{ getMonatName(monat) }}</th>
                <th>Durchschn. monatl. Kosten</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="posten in gruppiertNachKategorie['Anteile Andrea'] || []" :key="'andrea-'+posten.id">
                <td>{{ posten.beschreibung }}</td>
                <td v-for="monat in 12" :key="'andrea-posten-'+posten.id+'-'+monat">
                  {{ getPostenBetragFuerMonat(posten.id, monat) }}
                </td>
                <td>{{ formatCurrency(getPostenDurchschnitt(posten.id)) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="summe-zeile">
                <td><strong>Summe Anteile Andrea</strong></td>
                <td v-for="monat in 12" :key="'andrea-summe-'+monat">
                  {{ getMonatsSummeAndrea(monat) }}
                </td>
				<td><strong>{{ formatCurrency(monatlicheAusgabenAndrea) }}</strong></td>
              </tr>
              <tr class="summe-zeile">
				<td><strong>Summe Einnahmen Andrea</strong></td>
				<td v-for="monat in 12" :key="'andrea-einnahmen-summe-'+monat">
					{{ getMonatsSummeAndreaEinnahmen(monat) }}
				</td>
				<td><strong>{{ formatCurrency(monatlicheEinnahmenAndrea) }}</strong></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
      
      <!-- Quartals- und Halbjahresübersicht (ohne Anteile Andrea) -->
      <div class="periode-uebersicht">
        <h3>Periodenübersicht (ohne Anteile Andrea)</h3>
        
        <div class="perioden-container">
          <div class="periode-box">
            <h4>Quartale</h4>
            <table class="periode-tabelle">
              <thead>
                <tr>
                  <th>Quartal</th>
                  <th>Ausgaben</th>
                  <th>Einnahmen</th>
                  <th>Saldo</th>
                  <th>Monatliches Mittel</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="i in 4" :key="'q-'+i">
                  <td>Q{{ i }}</td>
                  <td>{{ formatCurrency(getQuartalsSummeOhneAndrea(i, 'ausgaben')) }}</td>
                  <td>{{ formatCurrency(getQuartalsSummeOhneAndrea(i, 'einnahmen')) }}</td>
                  <td :class="getQuartalsSaldoOhneAndrea(i) >= 0 ? 'positive' : 'negative'">
                    {{ formatCurrency(getQuartalsSaldoOhneAndrea(i)) }}
                  </td>
                  <td>{{ formatCurrency(getQuartalsMittelOhneAndrea(i, 'ausgaben')) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div class="periode-box">
            <h4>Halbjahre</h4>
            <table class="periode-tabelle">
              <thead>
                <tr>
                  <th>Halbjahr</th>
                  <th>Ausgaben</th>
                  <th>Einnahmen</th>
                  <th>Saldo</th>
                  <th>Monatliches Mittel</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="i in 2" :key="'h-'+i">
                  <td>H{{ i }}</td>
                  <td>{{ formatCurrency(getHalbjahrSummeOhneAndrea(i, 'ausgaben')) }}</td>
                  <td>{{ formatCurrency(getHalbjahrSummeOhneAndrea(i, 'einnahmen')) }}</td>
                  <td :class="getHalbjahrSaldoOhneAndrea(i) >= 0 ? 'positive' : 'negative'">
                    {{ formatCurrency(getHalbjahrSaldoOhneAndrea(i)) }}
                  </td>
                  <td>{{ formatCurrency(getHalbjahrMittelOhneAndrea(i, 'ausgaben')) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

const apiBaseUrl = process.env.VUE_APP_API_BASE_URL;
const jahresUebersichtUrl = `${apiBaseUrl}/jahresuebersicht`;
const KATEGORIE_AUSGABEN_ANDREA = 'Anteile Andrea'; // Für Ausgaben
const KATEGORIE_EINNAHMEN_ANDREA = 'Andrea'; // Für Einnahmen

export default {
  name: 'JahresUebersicht',
  props: {
    jahr: {
      type: Number,
      default() {
        return new Date().getFullYear();
      }
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      jahresUebersicht: null,
      expandedMonths: [],
      allePosten: [], // Hier speichern wir alle Posten für die Matrix-Ansicht
      andreaDaten: {
        monatsAusgaben: Array(12).fill(0),
        monatsEinnahmen: Array(12).fill(0)
      }
    };
  },
  computed: {
	// Daten ohne Andrea-Anteile - KORRIGIERT
    monatlicheAusgabenOhneAndrea() {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return 0;
      // Direkte Berechnung der Ausgaben ohne Andrea-Anteile
      let summeOhneAndrea = 0;
      this.jahresUebersicht.monats_daten.forEach(monat => {
        monat.ausgaben.forEach(ausgabe => {
          if (ausgabe.kategorie !== KATEGORIE_AUSGABEN_ANDREA) {
            summeOhneAndrea += ausgabe.betrag;
          }
        });
      });
      return summeOhneAndrea / 12; // Monatlicher Durchschnitt
    },
	monatlicheEinnahmenOhneAndrea() {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return 0;
      
      // Direkte Berechnung der Einnahmen ohne Andrea
      let summeOhneAndrea = 0;
      this.jahresUebersicht.monats_daten.forEach(monat => {
        if (monat.einnahmen) {
          monat.einnahmen.forEach(einnahme => {
            if (einnahme.kategorie !== KATEGORIE_EINNAHMEN_ANDREA) {
              summeOhneAndrea += einnahme.betrag;
            }
          });
        }
      });
      return summeOhneAndrea / 12; // Monatlicher Durchschnitt
    },
    jahresSaldoOhneAndrea() {
      return (this.monatlicheEinnahmenOhneAndrea * 12) - (this.monatlicheAusgabenOhneAndrea * 12);
    },
    saldoProMonat() {
      return this.jahresSaldoOhneAndrea / 12;
    },
   // Daten nur für Andrea-Anteile
    monatlicheAusgabenAndrea() {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return 0;
      
      // Direkte Berechnung aus Monatsdaten
      let summeAndrea = 0;
      this.jahresUebersicht.monats_daten.forEach(monat => {
        monat.ausgaben.forEach(ausgabe => {
          if (ausgabe.kategorie === KATEGORIE_AUSGABEN_ANDREA) {
            summeAndrea += ausgabe.betrag;
          }
        });
      });
      
      return summeAndrea / 12; // Monatlicher Durchschnitt
    },
    monatlicheEinnahmenAndrea() {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return 0;
      
      let summe = 0;
      this.jahresUebersicht.monats_daten.forEach(monat => {
        if (monat.einnahmen) {
          monat.einnahmen.forEach(einnahme => {
            if (einnahme.kategorie === KATEGORIE_EINNAHMEN_ANDREA) {
              summe += einnahme.betrag;
            }
          });
        }
      });
      
      return summe / 12; // Monatlicher Durchschnitt
    },
    jahresSaldoAndrea() {
      return (this.monatlicheEinnahmenAndrea * 12) - (this.monatlicheAusgabenAndrea * 12);
    },
    // Gruppieren der Posten nach Kategorie für die Tabelle (ohne Andrea)
    gruppiertNachKategorie() {
      const gruppen = {};
      if (!this.allePosten || this.allePosten.length === 0) return gruppen;
      
      this.allePosten.forEach(posten => {
        if (!gruppen[posten.kategorie]) {
          gruppen[posten.kategorie] = [];
        }
        gruppen[posten.kategorie].push(posten);
      });
      return gruppen;
    },
    // Gruppieren der Posten nach Kategorie für die Tabelle (ohne Andrea)
    gruppiertNachKategorieOhneAndrea() {
      const gruppen = {};
      if (!this.allePosten || this.allePosten.length === 0) return gruppen;
  
      // Definiere Reihenfolge der Kategorien
      const kategorienReihenfolge = [
        'Versicherungen', 
        'Kredite', 
        'Haus', 
        'Kinder', 
        'Hund', 
        'Sonstiges'
      ];
  
      // Gruppiere Posten nach Kategorie
      this.allePosten.forEach(posten => {
        if (posten.kategorie !== KATEGORIE_AUSGABEN_ANDREA) {
          if (!gruppen[posten.kategorie]) {
            gruppen[posten.kategorie] = [];
          }
          gruppen[posten.kategorie].push(posten);
        }
      });
  
      // Sortierte Kategorien erstellen
      const sortiertGruppen = {};
      kategorienReihenfolge.forEach(kategorie => {
        if (gruppen[kategorie]) {
          sortiertGruppen[kategorie] = gruppen[kategorie];
        }
      });
  
      // Kategorien, die nicht in der Reihenfolge definiert sind, am Ende anfügen
      Object.keys(gruppen).forEach(kategorie => {
        if (!kategorienReihenfolge.includes(kategorie)) {
           sortiertGruppen[kategorie] = gruppen[kategorie];
        }
       });
  
      return sortiertGruppen;
    }
  },
  created() {
    this.loadJahresUebersicht();
  },
  watch: {
    jahr() {
      // Neu laden wenn sich das Jahr ändert
      this.loadJahresUebersicht();
    }
  },
  methods: {
    async loadJahresUebersicht() {
      this.loading = true;
      try {
        const response = await axios.get(`${jahresUebersichtUrl}/${this.jahr}`);
        this.jahresUebersicht = response.data;
        
        // Alle einzigartigen Posten aus den Monatsdaten extrahieren
        this.allePosten = this.extrahiereAllePosten();
        
        // Ausgaben und Einnahmen der Anteile Andrea pro Monat berechnen
        this.berechneMontlicheWerteAndrea();
      } catch (err) {
        console.error('Fehler beim Laden der Jahresübersicht:', err);
        this.error = err.message || 'Unbekannter Fehler';
      } finally {
        this.loading = false;
      }
    },
	getKategorieDurchschnitt(kategorie) {
      if (!this.allePosten || this.allePosten.length === 0) return 0;
  
      let summe = 0;
      this.allePosten.forEach(posten => {
        if (posten.kategorie === kategorie) {
          summe += this.getPostenDurchschnitt(posten.id);
        }
      });
  
      return summe;
    },
     // Berechnet die Ausgaben und Einnahmen der Anteile Andrea pro Monat
    berechneMontlicheWerteAndrea() {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return;

      // Zurücksetzen der Werte
      this.andreaDaten.monatsAusgaben = Array(12).fill(0);
      this.andreaDaten.monatsEinnahmen = Array(12).fill(0);
  
      this.jahresUebersicht.monats_daten.forEach(monat => {
        const monatIndex = monat.monat - 1; // 0-basierter Index
    
        // Alle Ausgaben der Kategorie "Anteile Andrea" für diesen Monat summieren
        monat.ausgaben.forEach(ausgabe => {
         if (ausgabe.kategorie === KATEGORIE_AUSGABEN_ANDREA) {
            this.andreaDaten.monatsAusgaben[monatIndex] += ausgabe.betrag;
        }
        });
    
        // Einnahmen in der Kategorie "Anteile Andrea" summieren
        if (monat.einnahmen) {
          monat.einnahmen.forEach(einnahme => {
          if (einnahme.kategorie === KATEGORIE_EINNAHMEN_ANDREA) {
            this.andreaDaten.monatsEinnahmen[monatIndex] += einnahme.betrag;
            }
          });
        }
      });
    },
    // Extrahiert alle einzigartigen Posten aus allen Monaten
    extrahiereAllePosten() {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return [];
      
      const postenMap = new Map();
      
      this.jahresUebersicht.monats_daten.forEach(monat => {
        monat.ausgaben.forEach(ausgabe => {
          if (!postenMap.has(ausgabe.id)) {
            postenMap.set(ausgabe.id, {
              id: ausgabe.id,
              beschreibung: ausgabe.beschreibung,
              kategorie: ausgabe.kategorie,
              monatsBetraege: {}
            });
          }
          
          // Betrag für den jeweiligen Monat speichern
          postenMap.get(ausgabe.id).monatsBetraege[monat.monat] = ausgabe.betrag;
        });
      });
      
      return Array.from(postenMap.values());
    },
    // Formatiert einen Betrag als Währung
    formatCurrency(value) {
      if (value === 0) return '';
      return new Intl.NumberFormat('de-DE', { 
        style: 'currency', 
        currency: 'EUR',
		minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    },
    // Holt den deutschen Monatsnamen
    getMonatName(monatNummer) {
      const monate = [
        'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
        'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
      ];
      return monate[monatNummer - 1];
    },
    // Zeigt/versteckt die Details eines Monats
    toggleMonthDetails(monat) {
      if (this.expandedMonths.includes(monat)) {
        this.expandedMonths = this.expandedMonths.filter(m => m !== monat);
      } else {
        this.expandedMonths.push(monat);
      }
    },
    // Gibt den Betrag eines Postens für einen bestimmten Monat zurück
    getPostenBetragFuerMonat(postenId, monat) {
      const posten = this.allePosten.find(p => p.id === postenId);
      if (!posten || !posten.monatsBetraege[monat] || posten.monatsBetraege[monat] === 0) return '';
      return this.formatCurrency(posten.monatsBetraege[monat]);
    },
    // Berechnet den Durchschnitt für einen Posten über alle Monate
    getPostenDurchschnitt(postenId) {
      const posten = this.allePosten.find(p => p.id === postenId);
      if (!posten) return 0;
      
      const betraege = Object.values(posten.monatsBetraege);
      if (betraege.length === 0) return 0;
      
      const summe = betraege.reduce((sum, betrag) => sum + betrag, 0);
      return summe / 12; // Teilen durch 12 Monate
    },
    // Berechnet die Summe aller Ausgaben für einen Monat
    getMonatsSumme(monat, typ) {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return '';
      
      const monatsDaten = this.jahresUebersicht.monats_daten.find(m => m.monat === monat);
      if (!monatsDaten) return '';
      
      const summe = typ === 'ausgaben' ? monatsDaten.ausgaben_summe : monatsDaten.einnahmen_summe;
      if (summe === 0) return '';
      return this.formatCurrency(summe);
    },
    // Berechnet die Summe aller Ausgaben für einen Monat (ohne Anteile Andrea)
 // Aktualisierte Methode zur Berechnung der Monats-Ausgaben ohne Andrea
    getMonatsSummeOhneAndrea(monat, typ) {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return '';
      
      const monatsDaten = this.jahresUebersicht.monats_daten.find(m => m.monat === monat);
      if (!monatsDaten) return '';
      
      let summe = 0;
      if (typ === 'ausgaben') {
        // Summe aller Ausgaben außer der Kategorie "Anteile Andrea"
        summe = monatsDaten.ausgaben.reduce((sum, ausgabe) => {
          if (ausgabe.kategorie !== KATEGORIE_AUSGABEN_ANDREA) {
            return sum + ausgabe.betrag;
          }
          return sum;
        }, 0);
      } else { // einnahmen
        // Summe aller Einnahmen außer der Kategorie "Andrea"
        if (monatsDaten.einnahmen) {
          summe = monatsDaten.einnahmen.reduce((sum, einnahme) => {
            if (einnahme.kategorie !== KATEGORIE_EINNAHMEN_ANDREA) {
              return sum + einnahme.betrag;
            }
            return sum;
          }, 0);
        }
      }
      
      if (summe === 0) return '';
      return this.formatCurrency(summe);
    },
     // Methode für Ausgaben von Andrea
    getMonatsSummeAndrea(monat) {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return '';
  
      const monatsDaten = this.jahresUebersicht.monats_daten.find(m => m.monat === monat);
      if (!monatsDaten) return '';
  
      const ausgabenSumme = monatsDaten.ausgaben.reduce((sum, ausgabe) => {
        if (ausgabe.kategorie === KATEGORIE_AUSGABEN_ANDREA) {
          return sum + ausgabe.betrag;
        }
        return sum;
      }, 0);
  
      if (ausgabenSumme === 0) return '';
      return this.formatCurrency(ausgabenSumme);
    },
	// Methode für Einnahmen von Andrea
    getMonatsSummeAndreaEinnahmen(monat) {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return '';
  
      const monatsDaten = this.jahresUebersicht.monats_daten.find(m => m.monat === monat);
      if (!monatsDaten || !monatsDaten.einnahmen) return '';
  
      const summe = monatsDaten.einnahmen.reduce((sum, einnahme) => {
        if (einnahme.kategorie === KATEGORIE_EINNAHMEN_ANDREA) {
          return sum + einnahme.betrag;
        }
        return sum;
      }, 0);
  
      if (summe === 0) return '';
      return this.formatCurrency(summe);
    },
    // Aktualisierte Methode für virtuellen Kontostand ohne Andrea
    getVirtuellerKontostandOhneAndrea(monat) {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return 0;
      
      const monatsDaten = this.jahresUebersicht.monats_daten.find(m => m.monat === monat);
      if (!monatsDaten) return 0;
      
      // Summe der Anteile Andrea für diesen Monat (nur Ausgaben)
      const andreaSummeAusgaben = monatsDaten.ausgaben.reduce((sum, ausgabe) => {
        if (ausgabe.kategorie === KATEGORIE_AUSGABEN_ANDREA) {
          return sum + ausgabe.betrag;
        }
        return sum;
      }, 0);
      
      // Summe der Andrea-Einnahmen für diesen Monat
      let andreaSummeEinnahmen = 0;
      if (monatsDaten.einnahmen) {
        andreaSummeEinnahmen = monatsDaten.einnahmen.reduce((sum, einnahme) => {
          if (einnahme.kategorie === KATEGORIE_EINNAHMEN_ANDREA) {
            return sum + einnahme.betrag;
          }
          return sum;
        }, 0);
      }
      
      // Virtuellen Kontostand ohne Andreas Anteile berechnen
      return monatsDaten.virtueller_kontostand + andreaSummeAusgaben - andreaSummeEinnahmen;
    },
    // Aktualisierte Methode für Delta zum Mittel ohne Andrea
    getDeltaZumMittelOhneAndrea(monat) {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return 0;
      
      const monatsDaten = this.jahresUebersicht.monats_daten.find(m => m.monat === monat);
      if (!monatsDaten) return 0;
      
      // Ausgaben Andrea in diesem Monat
      const andreaAusgaben = monatsDaten.ausgaben.reduce((sum, ausgabe) => {
        if (ausgabe.kategorie === KATEGORIE_AUSGABEN_ANDREA) {
          return sum + ausgabe.betrag;
        }
        return sum;
      }, 0);
      
      // Einnahmen Andrea in diesem Monat
      let andreaEinnahmen = 0;
      if (monatsDaten.einnahmen) {
        andreaEinnahmen = monatsDaten.einnahmen.reduce((sum, einnahme) => {
          if (einnahme.kategorie === KATEGORIE_EINNAHMEN_ANDREA) {
            return sum + einnahme.betrag;
          }
          return sum;
        }, 0);
      }
      
      // Delta zum Mittel ohne Andreas Anteile
      return monatsDaten.delta_zum_mittel + (andreaAusgaben - andreaEinnahmen);
    },
 
    // Ähnliche Aktualisierungen sind in allen anderen Methoden nötig, 
    // die mit Andrea-Kategorien arbeiten
    getQuartalsSummeOhneAndrea(quartal, typ) {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return 0;
      
      const startMonat = (quartal - 1) * 3 + 1;
      const endMonat = startMonat + 2;
      
      let summe = 0;
      for (let monat = startMonat; monat <= endMonat; monat++) {
        const monatsDaten = this.jahresUebersicht.monats_daten.find(m => m.monat === monat);
        if (monatsDaten) {
          if (typ === 'ausgaben') {
            summe += monatsDaten.ausgaben.reduce((sum, ausgabe) => {
              if (ausgabe.kategorie !== KATEGORIE_AUSGABEN_ANDREA) {
                return sum + ausgabe.betrag;
              }
              return sum;
            }, 0);
          } else { // einnahmen
            if (monatsDaten.einnahmen) {
              summe += monatsDaten.einnahmen.reduce((sum, einnahme) => {
                if (einnahme.kategorie !== KATEGORIE_EINNAHMEN_ANDREA) {
                  return sum + einnahme.betrag;
                }
                return sum;
              }, 0);
            }
          }
        }
      }
      
      return summe;
    },
    // Berechnet den Saldo für ein Quartal (ohne Anteile Andrea)
    getQuartalsSaldoOhneAndrea(quartal) {
      return this.getQuartalsSummeOhneAndrea(quartal, 'einnahmen') - this.getQuartalsSummeOhneAndrea(quartal, 'ausgaben');
    },
    // Berechnet das monatliche Mittel für ein Quartal (ohne Anteile Andrea)
    getQuartalsMittelOhneAndrea(quartal, typ) {
      return this.getQuartalsSummeOhneAndrea(quartal, typ) / 3; // Durch 3 Monate teilen
    },
     // Und auch hier für die Halbjahresmethoden...
    getHalbjahrSummeOhneAndrea(halbjahr, typ) {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return 0;
      
      const startMonat = (halbjahr - 1) * 6 + 1;
      const endMonat = startMonat + 5;
      
      let summe = 0;
      for (let monat = startMonat; monat <= endMonat; monat++) {
        const monatsDaten = this.jahresUebersicht.monats_daten.find(m => m.monat === monat);
        if (monatsDaten) {
          if (typ === 'ausgaben') {
            summe += monatsDaten.ausgaben.reduce((sum, ausgabe) => {
              if (ausgabe.kategorie !== KATEGORIE_AUSGABEN_ANDREA) {
                return sum + ausgabe.betrag;
              }
              return sum;
            }, 0);
          } else { // einnahmen
            if (monatsDaten.einnahmen) {
              summe += monatsDaten.einnahmen.reduce((sum, einnahme) => {
                if (einnahme.kategorie !== KATEGORIE_EINNAHMEN_ANDREA) {
                  return sum + einnahme.betrag;
                }
                return sum;
              }, 0);
            }
          }
        }
      }
      
      return summe;
    },
    // Berechnet den Saldo für ein Halbjahr (ohne Anteile Andrea)
    getHalbjahrSaldoOhneAndrea(halbjahr) {
      return this.getHalbjahrSummeOhneAndrea(halbjahr, 'einnahmen') - this.getHalbjahrSummeOhneAndrea(halbjahr, 'ausgaben');
    },
	// Berechnet das monatliche Mittel für ein Halbjahr (ohne Anteile Andrea)
    getHalbjahrMittelOhneAndrea(halbjahr, typ) {
      return this.getHalbjahrSummeOhneAndrea(halbjahr, typ) / 6; // Durch 6 Monate teilen
    }
  }
};
</script>

<style scoped>
.jahresuebersicht-container {
  margin: 20px;
}

.loading, .error {
  padding: 20px;
  text-align: center;
}

.summary-box {
  background-color: #f5f5f5;
  border-radius: 5px;
  padding: 15px;
  margin-bottom: 20px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.label {
  font-weight: bold;
}

.table-container {
  overflow-x: auto;
  margin-bottom: 30px;
}

.posten-matrix-tabelle {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.posten-matrix-tabelle th,
.posten-matrix-tabelle td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: right;
}

.posten-matrix-tabelle th:first-child,
.posten-matrix-tabelle td:first-child {
  text-align: left;
}

.kategorie-header td {
  background-color: #f0f0f0;
  font-weight: bold;
  text-align: left;
}

.summe-zeile {
  background-color: #f9f9f9;
}

.positive {
  color: green;
}

.negative {
  color: red;
}

.anteile-andrea-section {
  margin-top: 40px;
  border-top: 2px solid #ccc;
  padding-top: 20px;
}

.periode-uebersicht {
  margin-top: 40px;
}

.perioden-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.periode-box {
  flex: 1;
  min-width: 300px;
}

.periode-tabelle {
  width: 100%;
  border-collapse: collapse;
}

.periode-tabelle th,
.periode-tabelle td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: right;
}

.periode-tabelle th:first-child,
.periode-tabelle td:first-child {
  text-align: center;
}
</style>