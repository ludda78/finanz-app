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
      
      <div class="table-container">
        <table class="uebersicht-table">
          <thead>
            <tr>
              <th>Monat</th>
              <th>Ausgaben</th>
              <th>Einnahmen</th>
              <th>Saldo</th>
              <th>Delta zum Mittel</th>
              <th>Virtueller Kontostand</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="monat in jahresUebersicht.monats_daten" :key="monat.monat">
              <td>{{ getMonatName(monat.monat) }}</td>
              <td>{{ formatCurrency(monat.ausgaben_summe) }}</td>
              <td>{{ formatCurrency(monat.einnahmen_summe) }}</td>
              <td :class="monat.saldo >= 0 ? 'positive' : 'negative'">
                {{ formatCurrency(monat.saldo) }}
              </td>
              <td :class="monat.delta_zum_mittel >= 0 ? 'positive' : 'negative'">
                {{ formatCurrency(monat.delta_zum_mittel) }}
              </td>
              <td :class="monat.virtueller_kontostand >= 0 ? 'positive' : 'negative'">
                {{ formatCurrency(monat.virtueller_kontostand) }}
              </td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td><strong>Gesamt</strong></td>
              <td>{{ formatCurrency(jahresUebersicht.jahres_summe_ausgaben) }}</td>
              <td>{{ formatCurrency(jahresUebersicht.jahres_summe_einnahmen) }}</td>
              <td :class="jahresSaldo >= 0 ? 'positive' : 'negative'">
                {{ formatCurrency(jahresSaldo) }}
              </td>
              <td></td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
      
      <div class="details-container">
        <div v-for="monat in jahresUebersicht.monats_daten" :key="'details-'+monat.monat" class="month-details">
          <h3 @click="toggleMonthDetails(monat.monat)">
            {{ getMonatName(monat.monat) }} 
            <span class="toggle-icon">{{ expandedMonths.includes(monat.monat) ? '▼' : '►' }}</span>
          </h3>
          
          <div v-if="expandedMonths.includes(monat.monat)" class="month-details-content">
            <table class="details-table">
              <thead>
                <tr>
                  <th>Beschreibung</th>
                  <th>Kategorie</th>
                  <th>Betrag</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="ausgabe in monat.ausgaben" :key="ausgabe.id">
                  <td>{{ ausgabe.beschreibung }}</td>
                  <td>{{ ausgabe.kategorie }}</td>
                  <td>{{ formatCurrency(ausgabe.betrag) }}</td>
                </tr>
                <tr v-if="monat.ausgaben.length === 0">
                  <td colspan="3">Keine Ausgaben in diesem Monat</td>
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
      expandedMonths: []
    };
  },
  computed: {
    jahresSaldo() {
      if (!this.jahresUebersicht) return 0;
      return this.jahresUebersicht.jahres_summe_einnahmen - this.jahresUebersicht.jahres_summe_ausgaben;
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
       // const response = await axios.get(`http://localhost:8000/jahresuebersicht/${this.jahr}`);
		const response = await axios.get(`${jahresUebersichtUrl}/${this.jahr}`);
        this.jahresUebersicht = response.data;
      } catch (err) {
        console.error('Fehler beim Laden der Jahresübersicht:', err);
        this.error = err.message || 'Unbekannter Fehler';
      } finally {
        this.loading = false;
      }
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('de-DE', { 
        style: 'currency', 
        currency: 'EUR' 
      }).format(value);
    },
    getMonatName(monatNummer) {
      const monate = [
        'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
        'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
      ];
      return monate[monatNummer - 1];
    },
    toggleMonthDetails(monat) {
      if (this.expandedMonths.includes(monat)) {
        this.expandedMonths = this.expandedMonths.filter(m => m !== monat);
      } else {
        this.expandedMonths.push(monat);
      }
    }
  }
};
</script>

<style scoped>
.jahresuebersicht-container {
  margin: 20px;
  font-family: Arial, sans-serif;
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
  overflow-x: auto;
  margin-bottom: 30px;
}

.uebersicht-table, .details-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #ddd;
}

th, td {
  border: 1px solid #ddd;
  padding: 10px;
  text-align: right;
}

th {
  background-color: #f2f2f2;
  text-align: center;
}

tfoot tr {
  background-color: #f2f2f2;
  font-weight: bold;
}

.positive {
  color: green;
}

.negative {
  color: red;
}

.month-details {
  margin-bottom: 15px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.month-details h3 {
  margin: 0;
  padding: 10px;
  background-color: #f2f2f2;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
}

.toggle-icon {
  font-size: 12px;
}

.month-details-content {
  padding: 15px;
}

@media (max-width: 768px) {
  .summary-item {
    min-width: 100%;
  }
}
</style>