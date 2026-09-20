<template>
  <div class="kredite container my-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="fw-semibold m-0">Kredite & Darlehen</h2>
      <button class="btn btn-primary btn-sm" @click="startCreate">+ Neuer Kredit</button>
    </div>

    <div v-if="loading" class="text-center text-muted py-5">
      <div class="spinner-border text-secondary" role="status"></div>
      <div class="mt-2">Lade Daten...</div>
    </div>
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <div v-else-if="kredite.length === 0" class="text-center text-muted py-5">
      Noch keine Kredite angelegt.
    </div>

    <div v-else>
      <div v-for="kredit in kredite" :key="kredit.id" class="card shadow-sm mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
          <div>
            <span class="fw-semibold fs-5">{{ kredit.bezeichnung }}</span>
            <span class="badge bg-secondary ms-2">{{ kredit.kategorie }}</span>
          </div>
          <div class="d-flex gap-2">
            <button class="btn btn-outline-secondary btn-sm" @click="startEdit(kredit)">Bearbeiten</button>
            <button class="btn btn-outline-danger btn-sm" @click="confirmDelete(kredit)">Löschen</button>
          </div>
        </div>

        <div class="card-body">
          <!-- Kennzahlen -->
          <div class="row g-3 mb-4">
            <div class="col-6 col-md-3">
              <div class="kennzahl-box kbox-neutral-neg">
                <div class="kennzahl-label">Darlehensbetrag</div>
                <div class="kennzahl-wert">{{ formatCurrency(kredit.darlehensbetrag) }}</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box kbox-neutral">
                <div class="kennzahl-label">Zinssatz (p.a.)</div>
                <div class="kennzahl-wert">{{ kredit.zinssatz.toFixed(2) }} %</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box kbox-neutral">
                <div class="kennzahl-label">Monatliche Rate</div>
                <div class="kennzahl-wert">{{ formatCurrency(kredit.monatliche_rate) }}</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box kbox-neutral">
                <div class="kennzahl-label">Startdatum</div>
                <div class="kennzahl-wert">{{ formatDate(kredit.startdatum) }}</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box kbox-neutral-pos">
                <div class="kennzahl-label">Aktuelle Restschuld</div>
                <div class="kennzahl-wert">{{ formatCurrency(aktuelleRestschuld(kredit)) }}</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box kbox-neutral-pos">
                <div class="kennzahl-label">Laufzeitende</div>
                <div class="kennzahl-wert">{{ laufzeitende(kredit) }}</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box kbox-neutral">
                <div class="kennzahl-label">Laufzeit</div>
                <div class="kennzahl-wert">{{ laufzeit(kredit) }}</div>
              </div>
            </div>
            <div class="col-6 col-md-3">
              <div class="kennzahl-box kbox-neutral-neg">
                <div class="kennzahl-label">Gesamtkosten</div>
                <div class="kennzahl-wert">{{ formatCurrency(gesamtkosten(kredit)) }}</div>
                <div class="kennzahl-sub">davon {{ formatCurrency(gesamtzinsen(kredit)) }} Zinsen</div>
              </div>
            </div>
          </div>

          <!-- Restschuld-Verlauf -->
          <div class="mb-1 text-muted" style="font-size: 0.8rem;">Restschuld-Verlauf</div>
          <div class="restschuld-chart-wrap">
            <svg :viewBox="`0 0 560 130`" class="w-100" style="max-height: 160px;">
              <g transform="translate(10, 10)">
                <!-- Y-axis line -->
                <line x1="0" y1="0" x2="0" y2="100" stroke="#ddd" stroke-width="1"/>
                <!-- X-axis line -->
                <line x1="0" y1="100" x2="540" y2="100" stroke="#ddd" stroke-width="1"/>
                <!-- Area fill -->
                <polygon
                  :points="'0,100 ' + chartPoints(kredit) + ' 540,100'"
                  fill="rgba(220, 53, 69, 0.12)"
                />
                <!-- Line -->
                <polyline
                  :points="chartPoints(kredit)"
                  fill="none"
                  stroke="#dc3545"
                  stroke-width="2"
                  stroke-linejoin="round"
                />
                <!-- Today marker -->
                <template v-if="todayX(kredit) !== null">
                  <line
                    :x1="todayX(kredit)" y1="0"
                    :x2="todayX(kredit)" y2="100"
                    stroke="#0d6efd" stroke-width="1" stroke-dasharray="4,3"
                  />
                  <circle
                    :cx="todayX(kredit)"
                    :cy="todayY(kredit)"
                    r="4" fill="#0d6efd"
                  />
                </template>
                <!-- Year labels -->
                <text
                  v-for="label in chartLabels(kredit)"
                  :key="label.year"
                  :x="label.x"
                  y="115"
                  text-anchor="middle"
                  font-size="9"
                  fill="#888"
                >{{ label.year }}</text>
                <!-- Y-axis labels -->
                <text x="-4" y="4" text-anchor="end" font-size="9" fill="#888">{{ formatCurrencyShort(kredit.darlehensbetrag) }}</text>
                <text x="-4" y="102" text-anchor="end" font-size="9" fill="#888">0</text>
              </g>
            </svg>
          </div>

          <div v-if="kredit.notiz" class="text-muted mt-2" style="font-size: 0.85rem;">
            <span class="fw-semibold">Notiz:</span> {{ kredit.notiz }}
          </div>
        </div>
      </div>
    </div>

    <!-- Form Modal -->
    <div v-if="showForm" class="modal-overlay" @click.self="cancelForm">
      <div class="modal-box">
        <h5 class="fw-semibold mb-3">{{ editingId ? 'Kredit bearbeiten' : 'Neuer Kredit' }}</h5>
        <form @submit.prevent="submitForm">
          <div class="mb-3">
            <label class="form-label">Bezeichnung</label>
            <input v-model="form.bezeichnung" class="form-control" required placeholder="z.B. Autokredit" />
          </div>
          <div class="row g-3 mb-3">
            <div class="col-6">
              <label class="form-label">Kategorie</label>
              <input v-model="form.kategorie" class="form-control" placeholder="z.B. Auto, Immobilie" />
            </div>
            <div class="col-6">
              <label class="form-label">Startdatum</label>
              <input v-model="form.startdatum" type="date" class="form-control" required />
            </div>
          </div>
          <div class="row g-3 mb-3">
            <div class="col-4">
              <label class="form-label">Darlehensbetrag (€)</label>
              <input v-model.number="form.darlehensbetrag" type="number" step="0.01" min="0" class="form-control" required />
            </div>
            <div class="col-4">
              <label class="form-label">Zinssatz p.a. (%)</label>
              <input v-model.number="form.zinssatz" type="number" step="0.001" min="0" class="form-control" required placeholder="z.B. 3.25" />
            </div>
            <div class="col-4">
              <label class="form-label">Monatliche Rate (€)</label>
              <input v-model.number="form.monatliche_rate" type="number" step="0.01" min="0" class="form-control" required />
            </div>
          </div>
          <div class="mb-3">
            <label class="form-label">Notiz (optional)</label>
            <textarea v-model="form.notiz" class="form-control" rows="2"></textarea>
          </div>
          <!-- Vorschau -->
          <div v-if="formPreview" class="alert alert-secondary py-2 mb-3" style="font-size: 0.85rem;">
            <strong>Vorschau:</strong>
            Laufzeit ca. {{ formPreview.monate }} Monate ({{ formPreview.jahre }} Jahre),
            Laufzeitende {{ formPreview.ende }},
            Gesamtzinsen {{ formatCurrency(formPreview.zinsen) }}
          </div>
          <div v-if="formError" class="alert alert-danger py-2 mb-3">{{ formError }}</div>
          <div class="d-flex gap-2 justify-content-end">
            <button type="button" class="btn btn-secondary btn-sm" @click="cancelForm">Abbrechen</button>
            <button type="submit" class="btn btn-primary btn-sm" :disabled="saving">
              {{ saving ? 'Speichern...' : 'Speichern' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirm -->
    <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
      <div class="modal-box" style="max-width: 400px;">
        <h5 class="fw-semibold mb-3">Kredit löschen?</h5>
        <p class="text-muted mb-3">
          Soll „<strong>{{ deleteTarget.bezeichnung }}</strong>" wirklich gelöscht werden?
        </p>
        <div class="d-flex gap-2 justify-content-end">
          <button class="btn btn-secondary btn-sm" @click="deleteTarget = null">Abbrechen</button>
          <button class="btn btn-danger btn-sm" @click="doDelete">Löschen</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

const API = '/api';

function berechnePlan(kredit) {
  const monatszins = kredit.zinssatz / 12 / 100;
  let restschuld = kredit.darlehensbetrag;
  const plan = [];

  const [sy, sm] = kredit.startdatum.split('-').map(Number);
  let year = sy;
  let month = sm;

  while (restschuld > 0.005 && plan.length < 600) {
    const zinsen = restschuld * monatszins;
    const tilgung = Math.min(kredit.monatliche_rate - zinsen, restschuld);
    if (tilgung <= 0.005) break;
    restschuld = Math.max(0, restschuld - tilgung);

    plan.push({
      monat: plan.length + 1,
      year,
      month,
      zinsen: Math.round(zinsen * 100) / 100,
      tilgung: Math.round(tilgung * 100) / 100,
      restschuld: Math.round(restschuld * 100) / 100,
    });

    month++;
    if (month > 12) { month = 1; year++; }
  }
  return plan;
}

export default {
  name: 'KreditUebersicht',
  data() {
    return {
      kredite: [],
      loading: true,
      error: null,
      showForm: false,
      editingId: null,
      saving: false,
      formError: null,
      deleteTarget: null,
      form: this.emptyForm(),
      planCache: {},
    };
  },
  computed: {
    formPreview() {
      const f = this.form;
      if (!f.darlehensbetrag || !f.zinssatz || !f.monatliche_rate || !f.startdatum) return null;
      const plan = berechnePlan({ ...f });
      if (plan.length === 0) return null;
      const last = plan[plan.length - 1];
      const gesamtzinsen = plan.reduce((s, e) => s + e.zinsen, 0);
      const monate = plan.length;
      const jahre = Math.floor(monate / 12);
      const ende = `${String(last.month).padStart(2, '0')}/${last.year}`;
      return { monate, jahre, ende, zinsen: Math.round(gesamtzinsen * 100) / 100 };
    },
  },
  async mounted() {
    await this.loadKredite();
  },
  methods: {
    emptyForm() {
      return { bezeichnung: '', kategorie: 'Sonstige', darlehensbetrag: null, zinssatz: null, monatliche_rate: null, startdatum: '', notiz: '' };
    },

    async loadKredite() {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axios.get(`${API}/kredite`);
        this.kredite = data;
        // Precompute plans
        const plans = {};
        for (const k of data) plans[k.id] = berechnePlan(k);
        this.planCache = plans;
      } catch (e) {
        this.error = 'Fehler beim Laden der Kredite.';
      } finally {
        this.loading = false;
      }
    },

    getPlan(kredit) {
      return this.planCache[kredit.id] || [];
    },

    aktuelleRestschuld(kredit) {
      const plan = this.getPlan(kredit);
      const today = new Date();
      const ty = today.getFullYear();
      const tm = today.getMonth() + 1;
      let result = kredit.darlehensbetrag;
      for (const e of plan) {
        if (e.year < ty || (e.year === ty && e.month <= tm)) {
          result = e.restschuld;
        } else {
          break;
        }
      }
      return result;
    },

    laufzeitende(kredit) {
      const plan = this.getPlan(kredit);
      if (!plan.length) return '—';
      const last = plan[plan.length - 1];
      return `${String(last.month).padStart(2, '0')}/${last.year}`;
    },

    laufzeit(kredit) {
      const plan = this.getPlan(kredit);
      if (!plan.length) return '—';
      const m = plan.length;
      const jahre = Math.floor(m / 12);
      const monate = m % 12;
      if (jahre === 0) return `${monate} Mon.`;
      if (monate === 0) return `${jahre} J.`;
      return `${jahre} J. ${monate} Mon.`;
    },

    gesamtkosten(kredit) {
      const plan = this.getPlan(kredit);
      if (!plan.length) return 0;
      return Math.round(plan.reduce((s, e) => s + e.tilgung + e.zinsen, 0) * 100) / 100;
    },

    gesamtzinsen(kredit) {
      const plan = this.getPlan(kredit);
      return Math.round(plan.reduce((s, e) => s + e.zinsen, 0) * 100) / 100;
    },

    // SVG chart helpers
    chartSamples(kredit) {
      const plan = this.getPlan(kredit);
      if (!plan.length) return [];
      const samples = [];
      let lastYear = -1;
      for (const e of plan) {
        if (e.year !== lastYear) { samples.push(e); lastYear = e.year; }
      }
      if (samples[samples.length - 1] !== plan[plan.length - 1]) {
        samples.push(plan[plan.length - 1]);
      }
      return samples;
    },

    chartPoints(kredit) {
      const samples = this.chartSamples(kredit);
      if (samples.length < 2) return '';
      const W = 540, H = 100;
      const max = kredit.darlehensbetrag;
      const n = samples.length;
      return samples.map((e, i) => {
        const x = (i / (n - 1)) * W;
        const y = H - (e.restschuld / max) * H;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      }).join(' ');
    },

    chartLabels(kredit) {
      const samples = this.chartSamples(kredit);
      if (samples.length < 2) return [];
      const W = 540;
      const n = samples.length;
      return samples.map((e, i) => ({
        year: e.year,
        x: (i / (n - 1)) * W,
      }));
    },

    todayX(kredit) {
      const samples = this.chartSamples(kredit);
      if (samples.length < 2) return null;
      const plan = this.getPlan(kredit);
      const today = new Date();
      const ty = today.getFullYear();
      const tm = today.getMonth() + 1;
      // Find index of current month in plan
      const idx = plan.findIndex(e => e.year > ty || (e.year === ty && e.month > tm));
      if (idx <= 0) return null;
      const W = 540;
      return ((idx / (plan.length - 1)) * W).toFixed(1);
    },

    todayY(kredit) {
      const plan = this.getPlan(kredit);
      const today = new Date();
      const ty = today.getFullYear();
      const tm = today.getMonth() + 1;
      let rs = kredit.darlehensbetrag;
      for (const e of plan) {
        if (e.year < ty || (e.year === ty && e.month <= tm)) rs = e.restschuld;
        else break;
      }
      const H = 100;
      return (H - (rs / kredit.darlehensbetrag) * H).toFixed(1);
    },

    startCreate() {
      this.form = this.emptyForm();
      this.editingId = null;
      this.formError = null;
      this.showForm = true;
    },

    startEdit(kredit) {
      this.form = {
        bezeichnung: kredit.bezeichnung,
        kategorie: kredit.kategorie,
        darlehensbetrag: kredit.darlehensbetrag,
        zinssatz: kredit.zinssatz,
        monatliche_rate: kredit.monatliche_rate,
        startdatum: kredit.startdatum,
        notiz: kredit.notiz || '',
      };
      this.editingId = kredit.id;
      this.formError = null;
      this.showForm = true;
    },

    cancelForm() {
      this.showForm = false;
      this.editingId = null;
      this.formError = null;
    },

    async submitForm() {
      this.formError = null;
      const plan = berechnePlan({ ...this.form });
      if (plan.length === 0) {
        this.formError = 'Die monatliche Rate reicht nicht aus, um die Zinsen zu decken.';
        return;
      }
      this.saving = true;
      try {
        if (this.editingId) {
          await axios.put(`${API}/kredite/${this.editingId}`, this.form);
        } else {
          await axios.post(`${API}/kredite`, this.form);
        }
        this.cancelForm();
        await this.loadKredite();
      } catch (e) {
        this.formError = e.response?.data?.detail || 'Fehler beim Speichern.';
      } finally {
        this.saving = false;
      }
    },

    confirmDelete(kredit) {
      this.deleteTarget = kredit;
    },

    async doDelete() {
      if (!this.deleteTarget) return;
      try {
        await axios.delete(`${API}/kredite/${this.deleteTarget.id}`);
        this.deleteTarget = null;
        await this.loadKredite();
      } catch {
        this.deleteTarget = null;
      }
    },

    formatCurrency(v) {
      if (v == null) return '—';
      return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR', maximumFractionDigits: 0 }).format(v);
    },

    formatCurrencyShort(v) {
      if (v >= 1000) return `${Math.round(v / 1000)}k`;
      return `${Math.round(v)}`;
    },

    formatDate(d) {
      if (!d) return '—';
      const [y, m, day] = d.split('-');
      return `${day}.${m}.${y}`;
    },
  },
};
</script>

<style scoped>
.kennzahl-box {
  border-radius: 6px;
  padding: 10px 14px;
  text-align: center;
}
.kennzahl-label {
  font-size: 0.72rem;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 4px;
}
.kennzahl-wert {
  font-size: 1.1rem;
  font-weight: 600;
}
.kennzahl-sub {
  font-size: 0.72rem;
  color: #888;
  margin-top: 2px;
}
.kbox-neutral { background: #f8f9fa; }
.kbox-neutral-pos { background: #e8f5e9; }
.kbox-neutral-neg { background: #fdecea; }

.restschuld-chart-wrap {
  background: #fafafa;
  border-radius: 6px;
  padding: 8px 4px 2px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
}
.modal-box {
  background: #fff;
  border-radius: 10px;
  padding: 28px 32px;
  max-width: 640px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}
</style>
