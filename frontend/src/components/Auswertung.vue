<template>
  <div class="auswertung container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <button class="btn btn-outline-secondary btn-sm" @click="jahrMinus">‹ Vorheriges Jahr</button>
      <h2 class="fw-semibold text-center flex-grow-1 m-0">Auswertung {{ jahr }}</h2>
      <button class="btn btn-outline-secondary btn-sm" @click="jahrPlus">Nächstes Jahr ›</button>
    </div>

    <div v-if="loading" class="text-center text-muted py-5">
      <div class="spinner-border text-secondary" role="status"></div>
      <div>Lade Daten...</div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else>

      <!-- Monatlicher Saldo -->
      <div class="card shadow-sm mb-4">
        <div class="card-header bg-light fw-semibold">Monatlicher Saldo (feste Posten)</div>
        <div class="card-body">
          <div class="chart-scroll">
            <div class="chart-bars">
              <div v-for="m in monate" :key="m.monat" class="chart-col">
                <div class="chart-value-top" :class="m.saldo > 0 ? 'pos' : 'invis'">
                  {{ m.saldo > 0 ? formatCurrency(m.saldo) : '' }}
                </div>
                <div class="chart-top">
                  <div
                    v-if="m.saldo > 0"
                    class="bar bar-pos"
                    :style="{ height: barHeight(m.saldo) + 'px' }"
                    :title="formatCurrencyFull(m.saldo)"
                  ></div>
                </div>
                <div class="chart-monat">{{ monatKurz(m.monat) }}</div>
                <div class="chart-bottom">
                  <div
                    v-if="m.saldo < 0"
                    class="bar bar-neg"
                    :style="{ height: barHeight(m.saldo) + 'px' }"
                    :title="formatCurrencyFull(m.saldo)"
                  ></div>
                </div>
                <div class="chart-value-bottom" :class="m.saldo < 0 ? 'neg' : 'invis'">
                  {{ m.saldo < 0 ? formatCurrency(m.saldo) : '' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Jahresbilanz Kennzahlen -->
      <div class="card shadow-sm mb-4">
        <div class="card-header bg-light fw-semibold">Jahresbilanz {{ jahr }}</div>
        <div class="card-body">
          <div class="row g-3">
            <div class="col-6 col-md-3">
              <div class="kennzahl-box" :class="gesamtsaldo >= 0 ? 'kbox-pos' : 'kbox-neg'">
                <div class="kennzahl-label">Gesamtsaldo</div>
                <div class="kennzahl-wert">{{ formatCurrencyFull(gesamtsaldo) }}</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box" :class="durchschnitt >= 0 ? 'kbox-pos' : 'kbox-neg'">
                <div class="kennzahl-label">Ø pro Monat</div>
                <div class="kennzahl-wert">{{ formatCurrencyFull(durchschnitt) }}</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box kbox-neutral-pos">
                <div class="kennzahl-label">Positive Monate</div>
                <div class="kennzahl-wert">{{ positiveMonate }} / 12</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box kbox-neutral-neg">
                <div class="kennzahl-label">Negative Monate</div>
                <div class="kennzahl-wert">{{ negativeMonate }} / 12</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Variable Kosten -->
      <div class="card shadow-sm mb-4">
        <div class="card-header bg-light fw-semibold">Variable Ausgaben (ungeplant)</div>
        <div class="card-body">
          <div class="chart-scroll">
            <div class="chart-bars">
              <div v-for="m in variableMonate" :key="m.monat" class="chart-col">
                <div class="chart-value-top" :class="m.saldo > 0 ? 'pos' : 'invis'">
                  {{ m.saldo > 0 ? formatCurrency(m.saldo) : '' }}
                </div>
                <div class="chart-top">
                  <div
                    v-if="m.saldo > 0"
                    class="bar bar-pos"
                    :style="{ height: varBarHeight(m.saldo) + 'px' }"
                    :title="'Einnahmen: ' + formatCurrencyFull(m.einnahmen) + ' | Ausgaben: ' + formatCurrencyFull(m.ausgaben)"
                  ></div>
                </div>
                <div class="chart-monat">{{ monatKurz(m.monat) }}</div>
                <div class="chart-bottom">
                  <div
                    v-if="m.saldo < 0"
                    class="bar bar-neg"
                    :style="{ height: varBarHeight(m.saldo) + 'px' }"
                    :title="'Ausgaben: ' + formatCurrencyFull(m.ausgaben) + ' | Einnahmen: ' + formatCurrencyFull(m.einnahmen)"
                  ></div>
                </div>
                <div class="chart-value-bottom" :class="m.saldo < 0 ? 'neg' : 'invis'">
                  {{ m.saldo < 0 ? formatCurrency(m.ausgaben * -1) : '' }}
                </div>
              </div>
            </div>
          </div>

          <!-- Jahressumme + Kategorien -->
          <div class="row g-3 mt-3">
            <div class="col-6 col-md-3">
              <div class="kennzahl-box" :class="varGesamtsaldo >= 0 ? 'kbox-pos' : 'kbox-neg'">
                <div class="kennzahl-label">Gesamtausgaben variabel</div>
                <div class="kennzahl-wert">{{ formatCurrencyFull(varGesamtausgaben) }}</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box kbox-neutral-pos">
                <div class="kennzahl-label">Gesamteinnahmen variabel</div>
                <div class="kennzahl-wert">{{ formatCurrencyFull(varGesamteinnahmen) }}</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box" :class="varGesamtsaldo >= 0 ? 'kbox-pos' : 'kbox-neg'">
                <div class="kennzahl-label">Saldo variabel</div>
                <div class="kennzahl-wert">{{ formatCurrencyFull(varGesamtsaldo) }}</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box kbox-neutral-neg">
                <div class="kennzahl-label">Ø Ausgaben / Monat</div>
                <div class="kennzahl-wert">{{ formatCurrencyFull(varGesamtausgaben / 12) }}</div>
              </div>
            </div>
          </div>

          <!-- Kategorienübersicht -->
          <div v-if="varKategorien.length > 0" class="mt-4">
            <div class="fw-semibold mb-2" style="font-size:0.85rem;">Ausgaben nach Kategorie (Jahressumme)</div>
            <table class="table table-sm table-bordered">
              <thead class="table-light">
                <tr>
                  <th>Kategorie</th>
                  <th v-for="(_, idx) in Array(12)" :key="idx" class="text-end" style="font-size:0.75rem;">
                    {{ monatKurz(idx + 1) }}
                  </th>
                  <th class="text-end">Summe</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="kat in varKategorien" :key="kat.name">
                  <td>{{ kat.name }}</td>
                  <td v-for="(v, idx) in kat.monate" :key="idx" class="text-end text-muted" style="font-size:0.8rem;">
                    {{ v ? formatCurrency(v) : '' }}
                  </td>
                  <td class="text-end fw-semibold">{{ formatCurrencyFull(kat.summe) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="text-muted fst-italic mt-3">Keine variablen Ausgaben in {{ jahr }} erfasst.</div>
        </div>
      </div>

      <!-- Veränderungen feste Posten -->
      <div class="card shadow-sm mb-4">
        <div class="card-header bg-light fw-semibold">Veränderungen feste Posten {{ jahr }}</div>
        <div class="card-body">
          <div v-if="verlaufJahr.length === 0" class="text-muted fst-italic">
            Keine Veränderungen in {{ jahr }} erfasst.
          </div>
          <div v-else>

            <div v-if="neuErstellt.length > 0" class="mb-4">
              <div class="verlauf-header text-success">✚ Neu hinzugekommen</div>
              <table class="table table-sm table-bordered">
                <tbody>
                  <tr v-for="e in neuErstellt" :key="e.beschreibung + e.datum + e.aktion">
                    <td class="ps-2">
                      <span class="badge" :class="e.typ === 'einnahme' ? 'bg-success' : 'bg-danger'">
                        {{ e.typ }}
                      </span>
                    </td>
                    <td>{{ e.beschreibung }}</td>
                    <td class="text-muted">{{ e.kategorie }}</td>
                    <td class="text-end fw-semibold">{{ formatCurrencyFull(e.betrag) }}</td>
                    <td class="text-muted">{{ e.details }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-if="geaendert.length > 0" class="mb-4">
              <div class="verlauf-header text-primary">✎ Betragsänderungen</div>
              <table class="table table-sm table-bordered">
                <tbody>
                  <tr v-for="e in geaendert" :key="e.beschreibung + e.datum + e.aktion">
                    <td class="ps-2">
                      <span class="badge" :class="e.typ === 'einnahme' ? 'bg-success' : 'bg-danger'">
                        {{ e.typ }}
                      </span>
                    </td>
                    <td>{{ e.beschreibung }}</td>
                    <td class="text-muted">{{ e.kategorie }}</td>
                    <td class="text-end fw-semibold">{{ formatCurrencyFull(e.betrag) }}</td>
                    <td class="text-muted">{{ e.details }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div v-if="beendet.length > 0">
              <div class="verlauf-header text-secondary">✖ Weggefallen / Beendet</div>
              <table class="table table-sm table-bordered">
                <tbody>
                  <tr v-for="e in beendet" :key="e.beschreibung + e.datum + e.aktion">
                    <td class="ps-2">
                      <span class="badge" :class="e.typ === 'einnahme' ? 'bg-success' : 'bg-danger'">
                        {{ e.typ }}
                      </span>
                    </td>
                    <td>{{ e.beschreibung }}</td>
                    <td class="text-muted">{{ e.kategorie }}</td>
                    <td class="text-end fw-semibold">{{ formatCurrencyFull(e.betrag) }}</td>
                    <td class="text-muted">{{ e.details }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import api from "@/api";

const MONATE_KURZ = ['Jan','Feb','Mär','Apr','Mai','Jun','Jul','Aug','Sep','Okt','Nov','Dez'];
const BAR_MAX_PX = 120;

export default {
  name: 'JahresAuswertung',
  data() {
    return {
      jahr: new Date().getFullYear(),
      loading: true,
      error: null,
      monate: [],
      variableMonate: [],
      verlauf: [],
    };
  },
  created() {
    this.loadDaten();
  },
  watch: {
    jahr() { this.loadDaten(); }
  },
  computed: {
    maxAbsSaldo() {
      return Math.max(...this.monate.map(m => Math.abs(m.saldo || 0)), 1);
    },
    gesamtsaldo() {
      return this.monate.reduce((s, m) => s + (m.saldo || 0), 0);
    },
    durchschnitt() {
      return this.gesamtsaldo / 12;
    },
    positiveMonate() {
      return this.monate.filter(m => m.saldo > 0).length;
    },
    negativeMonate() {
      return this.monate.filter(m => m.saldo < 0).length;
    },
    verlaufJahr() {
      return this.verlauf.filter(e => e.datum && e.datum.startsWith(String(this.jahr)));
    },
    neuErstellt() {
      return this.verlaufJahr.filter(e => e.aktion === 'erstellt');
    },
    geaendert() {
      return this.verlaufJahr.filter(e => e.aktion === 'aenderung');
    },
    beendet() {
      return this.verlaufJahr.filter(e => e.aktion === 'endet');
    },
    maxAbsVarSaldo() {
      return Math.max(...this.variableMonate.map(m => Math.abs(m.saldo || 0)), 1);
    },
    varGesamtausgaben() {
      return this.variableMonate.reduce((s, m) => s + (m.ausgaben || 0), 0);
    },
    varGesamteinnahmen() {
      return this.variableMonate.reduce((s, m) => s + (m.einnahmen || 0), 0);
    },
    varGesamtsaldo() {
      return this.varGesamteinnahmen - this.varGesamtausgaben;
    },
    varKategorien() {
      const kat = {};
      this.variableMonate.forEach(m => {
        Object.entries(m.kategorien || {}).forEach(([name, betrag]) => {
          if (!kat[name]) kat[name] = { name, monate: Array(12).fill(0), summe: 0 };
          kat[name].monate[m.monat - 1] = betrag;
          kat[name].summe += betrag;
        });
      });
      return Object.values(kat).sort((a, b) => b.summe - a.summe);
    },
  },
  methods: {
    async loadDaten() {
      this.loading = true;
      this.error = null;
      try {
        const [jahresRes, verlaufRes, variableRes] = await Promise.all([
          api.get(`/jahresuebersicht/${this.jahr}`),
          api.get('/feste-posten-verlauf'),
          api.get(`/variable-jahresuebersicht/${this.jahr}`),
        ]);
        const byMon = new Map((jahresRes.data.monate || []).map(m => [m.monat, m]));
        this.monate = Array.from({ length: 12 }, (_, i) => ({
          monat: i + 1,
          saldo: 0,
          ...byMon.get(i + 1),
        }));
        this.verlauf = verlaufRes.data;
        this.variableMonate = variableRes.data.monate || [];
      } catch (e) {
        this.error = e.message || 'Fehler beim Laden';
      } finally {
        this.loading = false;
      }
    },
    barHeight(saldo) {
      return Math.round((Math.abs(saldo) / this.maxAbsSaldo) * BAR_MAX_PX);
    },
    varBarHeight(saldo) {
      return Math.round((Math.abs(saldo) / this.maxAbsVarSaldo) * BAR_MAX_PX);
    },
    monatKurz(n) {
      return MONATE_KURZ[n - 1];
    },
    formatCurrency(v) {
      return new Intl.NumberFormat('de-DE', {
        style: 'currency', currency: 'EUR', maximumFractionDigits: 0
      }).format(v);
    },
    formatCurrencyFull(v) {
      return new Intl.NumberFormat('de-DE', {
        style: 'currency', currency: 'EUR'
      }).format(v);
    },
    jahrMinus() { if (this.jahr > 2020) this.jahr--; },
    jahrPlus() { this.jahr++; },
  },
};
</script>

<style scoped>
.auswertung { font-size: 0.9rem; }

/* Balkendiagramm */
.chart-scroll { overflow-x: auto; }

.chart-bars {
  display: flex;
  gap: 6px;
  min-width: 540px;
  padding: 0 4px;
}

.chart-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chart-top {
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  width: 100%;
}

.chart-bottom {
  height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  width: 100%;
}

.bar {
  width: 100%;
  min-height: 2px;
}
.bar-pos {
  background-color: #4caf50;
  border-radius: 3px 3px 0 0;
}
.bar-neg {
  background-color: #e53935;
  border-radius: 0 0 3px 3px;
}

.chart-monat {
  font-size: 0.72rem;
  text-align: center;
  color: #555;
  padding: 3px 0;
  border-top: 2px solid #aaa;
  border-bottom: 1px solid #ddd;
  width: 100%;
  background: #f8f9fa;
}

.chart-value-top,
.chart-value-bottom {
  font-size: 0.68rem;
  text-align: center;
  height: 18px;
  white-space: nowrap;
}
.chart-value-top.pos { color: #2e7d32; }
.chart-value-bottom.neg { color: #b71c1c; }
.invis { visibility: hidden; }

/* Kennzahl-Boxen */
.kennzahl-box {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 14px 16px;
  text-align: center;
}
.kbox-pos  { background: #e8f5e9; border-color: #a5d6a7; }
.kbox-neg  { background: #ffebee; border-color: #ef9a9a; }
.kbox-neutral-pos { background: #f1f8f1; border-color: #c8e6c9; }
.kbox-neutral-neg { background: #fdf3f3; border-color: #ffcdd2; }

.kennzahl-label { font-size: 0.75rem; color: #666; margin-bottom: 4px; }
.kennzahl-wert  { font-size: 1.15rem; font-weight: 600; }

/* Verlauf */
.verlauf-header {
  font-weight: 600;
  margin-bottom: 6px;
  font-size: 0.9rem;
}

.table td { vertical-align: middle; }
</style>
