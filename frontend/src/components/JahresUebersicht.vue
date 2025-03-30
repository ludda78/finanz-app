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
          <span class="label">Monatliches Ausgaben-Mittel:</span>
          <span class="value">{{ formatCurrency(jahresUebersicht.monatliches_mittel_ausgaben) }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Monatliches Einnahmen-Mittel:</span>
          <span class="value">{{ formatCurrency(jahresUebersicht.monatliches_mittel_einnahmen) }}</span>
        </div>
        <div class="summary-item">
          <span class="label">Jahres-Saldo:</span>
          <span class="value" :class="jahresSaldo >= 0 ? 'positive' : 'negative'">
            {{ formatCurrency(jahresSaldo) }}
          </span>
        </div>
      </div>
      
      <!-- Neue Tabelle mit Monaten als Spalten und Posten als Zeilen -->
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
            <!-- Gruppiere nach Kategorie und dann nach Posten -->
            <template v-for="(kategorieItems, kategorie) in gruppiertNachKategorie" :key="kategorie">
              <tr class="kategorie-header">
                <td colspan="14">{{ kategorie }}</td>
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
            <!-- Summen pro Monat -->
            <tr class="summe-zeile">
              <td><strong>Summe Ausgaben</strong></td>
              <td v-for="monat in 12" :key="'summe-'+monat">
                {{ getMonatsSumme(monat, 'ausgaben') }}
              </td>
              <td><strong>{{ formatCurrency(jahresUebersicht.monatliches_mittel_ausgaben) }}</strong></td>
            </tr>
            
            <!-- Virtuelle Kontostände -->
            <tr>
              <td><strong>Virtueller Kontostand</strong></td>
              <td v-for="monat in 12" :key="'kontostand-'+monat" 
                  :class="getVirtuellerKontostand(monat) >= 0 ? 'positive' : 'negative'">
                {{ formatCurrency(getVirtuellerKontostand(monat)) }}
              </td>
              <td></td>
            </tr>
            
            <!-- Delta zum Mittel -->
            <tr>
              <td><strong>Delta zum Mittel</strong></td>
              <td v-for="monat in 12" :key="'delta-'+monat" 
                  :class="getDeltaZumMittel(monat) >= 0 ? 'positive' : 'negative'">
                {{ formatCurrency(getDeltaZumMittel(monat)) }}
              </td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
      
      <!-- Quartals- und Halbjahresübersicht -->
      <div class="periode-uebersicht">
        <h3>Periodenübersicht</h3>
        
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
                  <td>{{ formatCurrency(getQuartalsSumme(i, 'ausgaben')) }}</td>
                  <td>{{ formatCurrency(getQuartalsSumme(i, 'einnahmen')) }}</td>
                  <td :class="getQuartalsSaldo(i) >= 0 ? 'positive' : 'negative'">
                    {{ formatCurrency(getQuartalsSaldo(i)) }}
                  </td>
                  <td>{{ formatCurrency(getQuartalsMittel(i, 'ausgaben')) }}</td>
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
                  <td>{{ formatCurrency(getHalbjahrSumme(i, 'ausgaben')) }}</td>
                  <td>{{ formatCurrency(getHalbjahrSumme(i, 'einnahmen')) }}</td>
                  <td :class="getHalbjahrSaldo(i) >= 0 ? 'positive' : 'negative'">
                    {{ formatCurrency(getHalbjahrSaldo(i)) }}
                  </td>
                  <td>{{ formatCurrency(getHalbjahrMittel(i, 'ausgaben')) }}</td>
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
      allePosten: [] // Hier speichern wir alle Posten für die Matrix-Ansicht
    };
  },
  computed: {
    jahresSaldo() {
      if (!this.jahresUebersicht) return 0;
      return this.jahresUebersicht.jahres_summe_einnahmen - this.jahresUebersicht.jahres_summe_ausgaben;
    },
    // Gruppieren der Posten nach Kategorie für die Tabelle
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
      } catch (err) {
        console.error('Fehler beim Laden der Jahresübersicht:', err);
        this.error = err.message || 'Unbekannter Fehler';
      } finally {
        this.loading = false;
      }
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
        currency: 'EUR' 
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
    // Gibt den virtuellen Kontostand für einen Monat zurück
    getVirtuellerKontostand(monat) {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return 0;
      
      const monatsDaten = this.jahresUebersicht.monats_daten.find(m => m.monat === monat);
      if (!monatsDaten) return 0;
      
      return monatsDaten.virtueller_kontostand;
    },
    // Gibt das Delta zum Mittel für einen Monat zurück
    getDeltaZumMittel(monat) {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return 0;
      
      const monatsDaten = this.jahresUebersicht.monats_daten.find(m => m.monat === monat);
      if (!monatsDaten) return 0;
      
      return monatsDaten.delta_zum_mittel;
    },
    // Berechnet die Summen für ein Quartal
    getQuartalsSumme(quartal, typ) {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return 0;
      
      const startMonat = (quartal - 1) * 3 + 1;
      const endMonat = startMonat + 2;
      
      let summe = 0;
      for (let monat = startMonat; monat <= endMonat; monat++) {
        const monatsDaten = this.jahresUebersicht.monats_daten.find(m => m.monat === monat);
        if (monatsDaten) {
          summe += typ === 'ausgaben' ? monatsDaten.ausgaben_summe : monatsDaten.einnahmen_summe;
        }
      }
      
      return summe;
    },
    // Berechnet den Saldo für ein Quartal
    getQuartalsSaldo(quartal) {
      return this.getQuartalsSumme(quartal, 'einnahmen') - this.getQuartalsSumme(quartal, 'ausgaben');
    },
    // Berechnet das monatliche Mittel für ein Quartal
    getQuartalsMittel(quartal, typ) {
      return this.getQuartalsSumme(quartal, typ) / 3; // Durch 3 Monate teilen
    },
    // Berechnet die Summen für ein Halbjahr
    getHalbjahrSumme(halbjahr, typ) {
      if (!this.jahresUebersicht || !this.jahresUebersicht.monats_daten) return 0;
      
      const startMonat = (halbjahr - 1) * 6 + 1;
      const endMonat = startMonat + 5;
      
      let summe = 0;
      for (let monat = startMonat; monat <= endMonat; monat++) {
        const monatsDaten = this.jahresUebersicht.monats_daten.find(m => m.monat === monat);
        if (monatsDaten) {
          summe += typ === 'ausgaben' ? monatsDaten.ausgaben_summe : monatsDaten.einnahmen_summe;
        }
      }
      
      return summe;
    },
    // Berechnet den Saldo für ein Halbjahr
    getHalbjahrSaldo(halbjahr) {
      return this.getHalbjahrSumme(halbjahr, 'einnahmen') - this.getHalbjahrSumme(halbjahr, 'ausgaben');
    },
    // Berechnet das monatliche Mittel für ein Halbjahr
    getHalbjahrMittel(halbjahr, typ) {
      return this.getHalbjahrSumme(halbjahr, typ) / 6; // Durch 6 Monate teilen
    }
  }
};
</script>

<style scoped>
.jahresuebersicht-container {
  padding: 10px; /* reduziertes Padding */
  font-family: Arial, sans-serif;
  width: 100%;
  max-width: 98vw; /* 98% der Viewport-Breite */
  margin: 0 auto; /* zentrieren */
  box-sizing: border-box;
}


.loading, .error {
  padding: 20px;
  text-align: center;
}

.error {
  color: red;
}

.summary-box {
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.summary-item {
  flex: 1;
  min-width: 200px;
}

.label {
  font-weight: bold;
  margin-right: 10px;
}

.table-container {
  width: 100%;
  overflow-x: auto;
  margin-bottom: 30px;
  max-width: 100%; /* Stellt sicher, dass der Container nicht über die Seite hinausgeht */
}

.posten-matrix-tabelle, .periode-tabelle {
  width: 100%;
  /* min-width: 100%; entfernen - das verhindert die Ausdehnung */
  table-layout: fixed; /* statt auto, um gleichmäßigere Spaltenbreiten zu bekommen */
  border-collapse: collapse;
  border: 1px solid #ddd;
  font-size: 14px;
}

th, td {
  border: 1px solid #ddd;
  padding: 6px; /* etwas weniger Padding (von 8px) */
  text-align: right;
  white-space: nowrap;
}

th {
  background-color: #f2f2f2;
  text-align: center;
  position: sticky;
  top: 0;
}

.posten-matrix-tabelle th:first-child,
.posten-matrix-tabelle td:first-child {
  position: sticky;
  left: 0;
  background-color: #fff;
  z-index: 10;
  text-align: left;
  min-width: 120px; /* reduzierte Mindestbreite von 150px */
}

.posten-matrix-tabelle th:first-child {
  background-color: #f2f2f2;
  z-index: 11;
}

.posten-matrix-tabelle th {
  font-size: 13px; /* etwas kleinere Schrift */
  padding: 6px 4px; /* reduziertes Padding */
}

tfoot tr {
  background-color: #f2f2f2;
  font-weight: bold;
}

.summe-zeile {
  border-top: 2px solid #999;
}

.kategorie-header td {
  background-color: #e6e6e6;
  font-weight: bold;
  text-align: left;
}

.positive {
  color: green;
}

.negative {
  color: red;
}

.periode-uebersicht {
  margin-top: 30px;
  width: 100%;
}

.perioden-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  width: 100%;
}

.periode-box {
  flex: 1;
  min-width: 300px;
  background-color: #f9f9f9;
  border-radius: 5px;
  padding: 15px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.periode-box h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.jahresuebersicht {
  width: 100%;
}

/* Für kleine Bildschirme */
@media (max-width: 768px) {
  .summary-item {
    min-width: 100%;
  }
  
  .periode-box {
    min-width: 100%;
  }
}
</style>