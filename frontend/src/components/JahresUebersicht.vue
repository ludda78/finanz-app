<template>
  <div class="jahresuebersicht container my-4">
  <div class="d-flex justify-content-between align-items-center mb-3">
  <button class="btn btn-outline-secondary btn-sm" @click="jahrMinus">
    ‹ Vorheriges Jahr
  </button>
   <h2 class="fw-semibold text-center flex-grow-1 m-0">Jahresübersicht {{ jahr }}</h2>
  <button class="btn btn-outline-secondary btn-sm" @click="jahrPlus">
    Nächstes Jahr ›
  </button>
</div>

   <!-- Fehler / Ladezustand -->
    <div v-if="loading" class="text-center text-muted py-5">
      <div class="spinner-border text-secondary" role="status"></div>
      <div>Lade Daten...</div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else>
      <!-- Feste Ausgaben -->
      <div class="card mb-4 shadow-sm">
        <div class="card-header bg-light fw-semibold">
          Feste Ausgaben
        </div>
        <div class="card-body p-0">
          <div class="table-responsive" style="max-height: 500px; overflow-y: auto;">
            <table class="table table-sm table-bordered m-0">
              <thead class="table-light sticky-top">
                <tr>
                  <th>Kategorie / Posten</th>
                  <th v-for="m in headerMonate" :key="m" class="text-end">{{ m }}</th>
                  <th class="text-end">Summe</th>
                  <th class="text-end">Ø</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="(posten, kategorie) in aggregierteAusgaben" :key="kategorie">
                  <tr class="table-secondary fw-semibold">
                    <td :colspan="headerMonate.length + 2">{{ kategorie }}</td>
                  </tr>
                 <tr
                    v-for="([name, werte]) in Object.entries(posten).filter(([k]) => !k.startsWith('_'))"
                     :key="name"
                    >
                    <td class="ps-4">{{ name }}</td>
                    <td
                      v-for="(betrag, idx) in werte.monate"
                      :key="idx"
                      class="text-end"
                    >
                      {{ formatCurrency(betrag) }}
                    </td>
                    <td class="text-end fw-semibold">{{ formatCurrency(werte.summe) }}</td>
                    <td class="text-end text-muted">{{ formatCurrency(werte.durchschnitt) }}</td>
                  </tr>
                  <tr class="table-light">
                    <td class="ps-4 fst-italic">Summe {{ kategorie }}</td>
                    <td
                      v-for="(v, idx) in posten._kategorieSummen"
                      :key="idx"
                      class="text-end"
                    >
                      {{ formatCurrency(v) }}
                    </td>
                    <td class="text-end fw-semibold">
                      {{ formatCurrency(posten._kategorieGesamt) }}
                    </td>
                     <td class="text-end text-muted">
                       {{ formatCurrency(posten._kategorieGesamt / 12) }}
                     </td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Feste Einnahmen -->
      <div class="card mb-4 shadow-sm">
        <div class="card-header bg-light fw-semibold">
          Feste Einnahmen
        </div>
        <div class="card-body p-0">
          <div class="table-responsive" style="max-height: 500px; overflow-y: auto;">
            <table class="table table-sm table-bordered m-0">
              <thead class="table-light sticky-top">
                <tr>
                  <th>Kategorie / Quelle</th>
                  <th v-for="m in headerMonate" :key="m" class="text-end">{{ m }}</th>
                  <th class="text-end">Summe</th>
                  <th class="text-end">Ø</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="(posten, kategorie) in aggregierteEinnahmen" :key="kategorie">
                  <tr class="table-secondary fw-semibold">
                    <td :colspan="headerMonate.length + 2">{{ kategorie }}</td>
                  </tr>
                  <tr
                     v-for="([name, werte]) in Object.entries(posten).filter(([k]) => !k.startsWith('_'))"
                     :key="name"
                   >
                    <td class="ps-4">{{ name }}</td>
                    <td
                      v-for="(betrag, idx) in werte.monate"
                      :key="idx"
                      class="text-end"
                    >
                      {{ formatCurrency(betrag) }}
                    </td>
                    <td class="text-end fw-semibold">{{ formatCurrency(werte.summe) }}</td>
                    <td class="text-end text-muted">{{ formatCurrency(werte.durchschnitt) }}</td>
                  </tr>
                  <tr class="table-light">
                    <td class="ps-4 fst-italic">Summe {{ kategorie }}</td>
                    <td
                      v-for="(v, idx) in posten._kategorieSummen"
                      :key="idx"
                      class="text-end"
                    >
                      {{ formatCurrency(v) }}
                    </td>
                    <td class="text-end fw-semibold">
                      {{ formatCurrency(posten._kategorieGesamt) }}
                    </td>
                    <td></td>
                  </tr>
                </template>
              </tbody>
            </table>
          </div>
        </div>
      </div>

<!-- Jahreskennzahlen -->
<div class="card shadow-sm mt-4">
  <div class="card-header bg-light">
    <h5 class="m-0">📊 Jahreskennzahlen</h5>
  </div>
  <div class="card-body table-responsive">
    <table class="table table-sm align-middle text-end">
      <thead>
        <tr>
          <th class="text-start">Kennzahl</th>
          <th v-for="(m, idx) in headerMonate" :key="idx">{{ m }}</th>
          <th>Summe</th>
          <th>Ø</th>
        </tr>
      </thead>
      <tbody>
        <!-- Ausgaben -->
        <tr class="text-danger">
          <td class="text-start">Ausgaben</td>
          <td v-for="m in monate" :key="'a'+m.monat">
            {{ formatCurrency(m.ausgaben) }}
          </td>
          <td>{{ formatCurrency(sumAusgaben) }}</td>
          <td>{{ formatCurrency(avgAusgaben) }}</td>
        </tr>

        <!-- Einnahmen -->
        <tr class="text-success">
          <td class="text-start">Einnahmen</td>
          <td v-for="m in monate" :key="'e'+m.monat">
            {{ formatCurrency(m.einnahmen) }}
          </td>
          <td>{{ formatCurrency(sumEinnahmen) }}</td>
          <td>{{ formatCurrency(avgEinnahmen) }}</td>
        </tr>

        <!-- Saldo -->
        <tr class="table-light fw-semibold">
          <td class="text-start">Saldo</td>
          <td v-for="m in monate" :key="'s'+m.monat">
            {{ formatCurrency(m.saldo) }}
          </td>
          <td>{{ formatCurrency(sumSaldo) }}</td>
          <td>{{ formatCurrency(avgSaldo) }}</td>
        </tr>

        <!-- Virtueller Kontostand -->
        <tr>
          <td class="text-start">Virtueller Kontostand</td>
          <td v-for="m in monate" :key="'vk'+m.monat">
            {{ formatCurrency(m.virtueller_kontostand) }}
          </td>
        </tr>

        <!-- Soll-Kontostand -->
        <tr>
          <td class="text-start">Soll-Kontostand</td>
          <td v-for="m in monate" :key="'sk'+m.monat">
            {{ formatCurrency(m.soll_kontostand) }}
          </td>
        </tr>

        <!-- Delta zum Mittel -->
        <tr>
          <td class="text-start">Δ zum Mittel</td>
          <td v-for="m in monate" :key="'dm'+m.monat">
            {{ formatCurrency(m.delta_mittel) }}
          </td>
        </tr>
      </tbody>
    </table>
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
  /* props: {
    jahr: {
      type: Number,
      default() {
        return new Date().getFullYear();
      }
    }
  }, */
  data() {
    return {
      jahr: new Date().getFullYear(), // Lokale Jahresvariable
      loading: true,
      error: null,
      // Neue Struktur: Backend liefert ein fertiges Array mit allen Kennzahlen
      monate: [], // [{monat, ausgaben, einnahmen, saldo, virtueller_kontostand, delta_mittel, soll_kontostand}]
      mittelAusgabenOhneAndrea: null, // kommt jetzt vom Backend, nicht aus manueller Berechnung

      // ❌ Alt: war nötig für clientseitige Aggregationen, jetzt überflüssig
      jahresUebersicht: null,
      // expandedMonths: [],
      // allePosten: [],
      // andreaDaten: { monatsAusgaben: Array(12).fill(0), monatsEinnahmen: Array(12).fill(0) }
    };
  },
  created() {
    this.loadJahresdaten();
  },
  watch: {
    jahr() {
      this.loadJahresdaten();
    }
  },
  computed: {
    headerMonate() {
      const names = ["Jan","Feb","Mär","Apr","Mai","Jun","Jul","Aug","Sep","Okt","Nov","Dez"];
      return names;
    },
    // Summen für Fuß-/Kopfzeilen
    sumAusgaben()  { return this.monate.reduce((s,m)=>s+(m.ausgaben||0), 0); },
    sumEinnahmen() { return this.monate.reduce((s,m)=>s+(m.einnahmen||0), 0); },
    sumSaldo()     { return this.monate.reduce((s,m)=>s+(m.saldo||0), 0); },
	avgAusgaben() { return this.sumAusgaben / 12; },
	avgEinnahmen() { return this.sumEinnahmen / 12; },
	avgSaldo()     { return this.sumSaldo / 12; },

    // ❌ Alt: diese Computed-Properties haben Summen ohne Andrea clientseitig berechnet.
    // Die Logik steckt jetzt im Backend → sauberere Quelle, daher auskommentiert.
    /*
    monatlicheAusgabenOhneAndrea() { ... },
    monatlicheEinnahmenOhneAndrea() { ... },
    jahresSaldoOhneAndrea() { ... },
    saldoProMonat() { ... },
    monatlicheAusgabenAndrea() { ... },
    monatlicheEinnahmenAndrea() { ... },
    jahresSaldoAndrea() { ... },
    gruppiertNachKategorie() { ... },
    gruppiertNachKategorieOhneAndrea() { ... },
    */
      // Aggregiert die festen Ausgaben aus monats_daten
  aggregierteAusgaben() {
    if (!this.jahresUebersicht?.monats_daten) return {};

    const daten = this.jahresUebersicht.monats_daten;
    const matrix = {};

    daten.forEach((monatObj) => {
      const monatIndex = monatObj.monat - 1;

      monatObj.ausgaben.forEach((a) => {
        // Kategorie erzeugen
        if (!matrix[a.kategorie]) matrix[a.kategorie] = {};
        const kat = matrix[a.kategorie];

        // Beschreibung erzeugen
        if (!kat[a.beschreibung]) {
          kat[a.beschreibung] = {
            monate: Array(12).fill(0),
            summe: 0,
            durchschnitt: 0,
          };
        }

        // Wert eintragen
        kat[a.beschreibung].monate[monatIndex] = a.betrag;
      });
    });

    // Summen pro Posten + pro Kategorie berechnen
    for (const [, posten] of Object.entries(matrix)) {
      const kategorieSummen = Array(12).fill(0);
      let kategorieGesamt = 0;
      let rowCount = 0;

      for (const [beschr, werte] of Object.entries(posten)) {
        if (beschr === '_rowspan') continue;

        // Summen für diesen Posten
        werte.summe = werte.monate.reduce((s, v) => s + v, 0);
        werte.durchschnitt = werte.summe / 12;

        // In die Kategorie-Summen einrechnen
        werte.monate.forEach((v, i) => (kategorieSummen[i] += v));
        kategorieGesamt += werte.summe;
        rowCount++;
      }

      posten._kategorieSummen = kategorieSummen;
      posten._kategorieGesamt = kategorieGesamt;
      posten._rowspan = rowCount + 2; // +2 = Header + Zwischensumme
    }

    return matrix;
  },

  // Aggregiert die festen Einnahmen aus monats_daten
  aggregierteEinnahmen() {
    if (!this.jahresUebersicht?.monats_daten) return {};

    const daten = this.jahresUebersicht.monats_daten;
    const matrix = {};

    daten.forEach((monatObj) => {
      const monatIndex = monatObj.monat - 1;
      if (!monatObj.einnahmen) return;

      monatObj.einnahmen.forEach((e) => {
        // Kategorie erzeugen
        if (!matrix[e.kategorie]) matrix[e.kategorie] = {};
        const kat = matrix[e.kategorie];

        // Name/Beschreibung (je nach Feld in deiner DB)
        const name = e.beschreibung || e.name || 'Unbekannt';
        if (!kat[name]) {
          kat[name] = {
            monate: Array(12).fill(0),
            summe: 0,
            durchschnitt: 0,
          };
        }

        // Wert eintragen
        kat[name].monate[monatIndex] = e.betrag;
      });
    });

    // Summen pro Posten + Kategorie berechnen
    for (const [, posten] of Object.entries(matrix)) {
      const kategorieSummen = Array(12).fill(0);
      let kategorieGesamt = 0;
      let rowCount = 0;

      for (const [name, werte] of Object.entries(posten)) {
        if (name === '_rowspan') continue;

        werte.summe = werte.monate.reduce((s, v) => s + v, 0);
        werte.durchschnitt = werte.summe / 12;

        werte.monate.forEach((v, i) => (kategorieSummen[i] += v));
        kategorieGesamt += werte.summe;
        rowCount++;
      }

      posten._kategorieSummen = kategorieSummen;
      posten._kategorieGesamt = kategorieGesamt;
      posten._rowspan = rowCount + 2;
    }

    return matrix;
  },

  // Gesamtsummen über alle Kategorien
  gesamtSummenMonat() {
    const summen = Array(12).fill(0);
    for (const kat of Object.values(this.aggregierteAusgaben)) {
      kat._kategorieSummen.forEach((v, i) => (summen[i] += v));
    }
    return summen;
  },

  gesamtSummeJahr() {
    return this.gesamtSummenMonat.reduce((s, v) => s + v, 0);
  },

  },
  methods: {
    eur(n) {
      const v = Number(n ?? 0);
      return v.toLocaleString("de-DE", { style: "currency", currency: "EUR", maximumFractionDigits: 2 });
    },

    normMonth(m, idx) {
      // Fallback sichert, dass alle Felder existieren
      return {
        monat: m.monat ?? (idx+1),
        ausgaben: Number(m.ausgaben ?? 0),
        einnahmen: Number(m.einnahmen ?? 0),
        saldo: Number(m.saldo ?? (Number(m.einnahmen ?? 0) - Number(m.ausgaben ?? 0))),
        virtueller_kontostand: Number(m.virtueller_kontostand ?? 0),
        delta_mittel: Number(m.delta_mittel ?? 0),
        soll_kontostand: Number(m.soll_kontostand ?? 0),
      };
    },

    ensureTwelve(monatsArray) {
      const byMon = new Map(monatsArray.map(m => [m.monat, m]));
      const out = [];
      for (let i=1; i<=12; i++) out.push(byMon.get(i) || this.normMonth({ monat: i }, i-1));
      return out;
    },

    async loadJahresdaten() {
      this.loading = true; this.error = null;
     console.log("Lade Jahr:", this.jahr);

      try {
        const { data } = await axios.get(`${jahresUebersichtUrl}/${this.jahr}`);
        this.mittelAusgabenOhneAndrea = Number(data.monatliches_mittel_ausgaben_ohne_andrea ?? 0);
        this.monate = this.ensureTwelve((data.monate || []).map(this.normMonth));

        // 👇 Das ist wichtig für die neue Tabelle:
        this.jahresUebersicht = data;
      } catch (e) {
        console.error('Fehler beim Laden der Jahresübersicht:', e);
        this.error = e.message || 'Unbekannter Fehler';
      } finally {
        this.loading = false;
      }
    },
    
	getMonatName(monatNummer) {
      const monate = [
        'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
        'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
      ];
      return monate[monatNummer - 1] || '';
    },

	formatCurrency(value) {
      if (value === 0 || value === null || value === undefined) return '';
      return new Intl.NumberFormat('de-DE', { 
        style: 'currency', 
        currency: 'EUR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(value);
    },
    jahrMinus() {
      if (this.jahr > 2020) {
        this.jahr -= 1;
		console.log("Neues Jahr (Minus):", this.jahr);
        this.loadJahresdaten();
      }
    },
    jahrPlus() {
      this.jahr += 1;
      console.log("Neues Jahr (Plus):", this.jahr);
      this.loadJahresdaten();
    },
  },
    mounted() {
      console.log("Komponente geladen, lade Jahr:", this.jahr);
      this.loadJahresdaten();
	}
};


</script>


<style scoped>
.jahresuebersicht {
  font-size: 0.9rem;
}

.table thead th {
  position: sticky;
  top: 0;
  background-color: #f8f9fa;
  z-index: 1;
}

.table tbody tr:nth-child(even) {
  background-color: #fcfcfc;
}

.table td,
.table th {
  vertical-align: middle;
  white-space: nowrap;
}

.card {
  border-radius: 0.4rem;
  border: 1px solid #dee2e6;
}

.card-header {
  font-size: 1rem;
}

.ps-4 {
  padding-left: 1.5rem !important;
}

/* Dezente Summenzeilen, ohne knallige Farben */
.summe-zeile.ausgaben {
  background-color: #fdf2f2;
}
.summe-zeile.einnahmen {
  background-color: #f2fdf2;
}
.summe-zeile.saldo {
  background-color: #f5f9ff;
  font-weight: 600;
}

/* Tooltips beibehalten (wenn du sie nutzt) */
.tooltip {
  position: relative;
  cursor: help;
}
.tooltip::after {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: white;
  padding: 5px 10px;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s;
}
.tooltip:hover::after {
  opacity: 1;
}

/* Optional: leichtes Hover für Tabellenzeilen */
.table-hover tbody tr:hover {
  background-color: #f8f9fa;
}
.table td:last-child {
  background-color: #fafafa;
  font-style: italic;
}

</style>
