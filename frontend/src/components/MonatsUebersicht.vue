<template>
  <div>
    <div class="monats-uebersicht">
    <div class="month-selector">
      <div class="selectors">
        <select v-model="selectedMonth" @change="updateRoute">
          <option v-for="(monatName, index) in monate" :key="index" :value="index + 1">
            {{ monatName }}
          </option>
        </select>
        
        <select v-model="selectedYear" @change="updateRoute">
          <option v-for="jahr in jahre" :key="jahr" :value="jahr">
            {{ jahr }}
          </option>
        </select>
      </div>
      
      <div class="navigation-buttons">
        <button @click="previousMonth">Vorheriger Monat</button>
        <button @click="nextMonth">Nächster Monat</button>
      </div>
    </div>
   </div>
   <!-- Rest of your MonatsUebersicht component content -->
    <h1>Übersicht für {{ monate[selectedMonth - 1] }} {{ selectedYear }}</h1>

    <h2>Feste Ausgaben</h2>
    <!-- Gruppiere feste Ausgaben nach Kategorie -->
    <div v-for="(ausgaben, kategorie) in gruppiertFesteAusgaben" :key="'ausgaben-'+kategorie">
      <h3>{{ kategorie }}</h3>
      <table>
        <thead>
          <tr>
            <th>Beschreibung</th>
            <th>Soll</th>
            <th>Ist</th>
            <th>Abweichung</th>
          </tr>
        </thead>
        <tbody>	
          <tr v-for="ausgabe in ausgaben" :key="ausgabe.id">
            <td>{{ ausgabe.beschreibung }}</td>
            <td>{{ ausgabe.betrag }} €</td>
            <td>
              <input 
                type="number" 
                v-model.number="ausgabe.ist_wert"
                @blur="speichereIstWert(ausgabe.id, ausgabe.ist_wert, 'ausgabe', ausgabe.beschreibung, ausgabe.betrag)"
              />
            </td>
            <td :style="{ color: ausgabe.ist_wert > ausgabe.betrag ? 'red' : 'green' }">
              {{ ausgabe.ist_wert - ausgabe.betrag }} €
            </td>
          </tr>
          <!-- Summenzeile für jede Kategorie -->
          <tr class="summen-zeile">
            <td><strong>Summe {{ kategorie }}</strong></td>
            <td><strong>{{ berechneSummeSoll(ausgaben) }} €</strong></td>
            <td><strong>{{ berechneSummeIst(ausgaben) }} €</strong></td>
            <td :style="{ color: berechneSummeAbweichung(ausgaben) > 0 ? 'red' : 'green' }">
              <strong>{{ berechneSummeAbweichung(ausgaben) }} €</strong>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Gesamtsummenzeile für feste Ausgaben -->
    <table class="gesamtsumme">
      <tbody>
        <tr class="summen-zeile">
          <td><strong>Gesamtsumme Ausgaben</strong></td>
          <td><strong>{{ summeFesteAusgabenSoll }} €</strong></td>
          <td><strong>{{ summeFesteAusgabenIst }} €</strong></td>
          <td :style="{ color: summeFesteAusgabenAbweichung > 0 ? 'red' : 'green' }">
            <strong>{{ summeFesteAusgabenAbweichung }} €</strong>
          </td>
        </tr>
      </tbody>
    </table>

    <h2>Feste Einnahmen</h2>
    <!-- Gruppiere feste Einnahmen nach Kategorie -->
    <div v-for="(einnahmen, kategorie) in gruppiertFesteEinnahmen" :key="'einnahmen-'+kategorie">
      <h3>{{ kategorie }}</h3>
      <table>
        <thead>
          <tr>
            <th>Beschreibung</th>
            <th>Soll</th>
            <th>Ist</th>
            <th>Abweichung</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="einnahme in einnahmen" :key="einnahme.id">
            <td>{{ einnahme.name }}</td>
            <td>{{ einnahme.betrag }} €</td>
            <td>
              <input 
                type="number" 
                v-model.number="einnahme.ist_wert"
                @blur="speichereIstWert(einnahme.id, einnahme.ist_wert, 'einnahme', einnahme.name, einnahme.betrag)"
              />
            </td>
            <td :style="{ color: einnahme.ist_wert < einnahme.betrag ? 'red' : 'green' }">
              {{ einnahme.ist_wert - einnahme.betrag }} €
            </td>
          </tr>
          <!-- Summenzeile für jede Kategorie -->
          <tr class="summen-zeile">
            <td><strong>Summe {{ kategorie }}</strong></td>
            <td><strong>{{ berechneSummeSoll(einnahmen) }} €</strong></td>
            <td><strong>{{ berechneSummeIst(einnahmen) }} €</strong></td>
            <td :style="{ color: berechneSummeAbweichung(einnahmen) < 0 ? 'red' : 'green' }">
              <strong>{{ berechneSummeAbweichung(einnahmen) }} €</strong>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Gesamtsummenzeile für feste Einnahmen -->
    <table class="gesamtsumme">
      <tbody>
        <tr class="summen-zeile">
          <td><strong>Gesamtsumme Einnahmen</strong></td>
          <td><strong>{{ summeFesteEinnahmenSoll }} €</strong></td>
          <td><strong>{{ summeFesteEinnahmenIst }} €</strong></td>
          <td :style="{ color: summeFesteEinnahmenAbweichung < 0 ? 'red' : 'green' }">
            <strong>{{ summeFesteEinnahmenAbweichung }} €</strong>
          </td>
        </tr>
      </tbody>
	</table>
    
    <!-- Gesamtbilanz -->
    <div class="gesamtbilanz">
      <h2>Gesamtbilanz</h2>
      <table>
        <thead>
          <tr>
            <th></th>
            <th>Soll</th>
            <th>Ist</th>
            <th>Abweichung</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><strong>Einnahmen - Ausgaben</strong></td>
            <td><strong>{{ gesamtbilanzSoll }} €</strong></td>
            <td><strong>{{ gesamtbilanzIst }} €</strong></td>
            <td :style="{ color: gesamtbilanzAbweichung < 0 ? 'red' : 'green' }">
              <strong>{{ gesamtbilanzAbweichung }} €</strong>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Ungeplante Transaktionen wie zuvor -->
    <div class="ungeplante-transaktionen">
      <h2>Ungeplante Transaktionen</h2>
      
      <div class="row">
        <!-- Ausgaben-Spalte -->
        <div class="col">
          <h3>Ungeplante Ausgaben</h3>
          <form @submit.prevent="addAusgabe">
            <input v-model="newAusgabe.beschreibung" placeholder="Beschreibung" required>
            <input v-model.number="newAusgabe.betrag" type="number" placeholder="Betrag" required>
            <textarea v-model="newAusgabe.kommentar" placeholder="Kommentar (optional)"></textarea>
            <button type="submit">Ausgabe hinzufügen</button>
          </form>

          <table>
            <thead>
              <tr>
                <th>Beschreibung</th>
                <th>Betrag</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="ausgabe in ungeplannteAusgaben" :key="ausgabe.id">
                <td>{{ ausgabe.beschreibung }}</td>
                <td>{{ ausgabe.betrag }}€</td>
                <td>
                  <button @click="createAusgleich(ausgabe)">Ausgleich</button>
                </td>
              </tr>
              <!-- Summenzeile für ungeplante Ausgaben -->
              <tr class="summen-zeile" v-if="ungeplannteAusgaben.length > 0">
                <td><strong>Summe</strong></td>
                <td><strong>{{ summeUngeplannteAusgaben }} €</strong></td>
                <td></td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Einnahmen-Spalte -->
        <div class="col">
          <h3>Ungeplante Einnahmen</h3>
          <form @submit.prevent="addEinnahme">
            <input v-model="newEinnahme.beschreibung" placeholder="Beschreibung" required>
            <input v-model.number="newEinnahme.betrag" type="number" placeholder="Betrag" required>
            <button type="submit">Einnahme hinzufügen</button>
          </form>

          <table>
            <thead>
              <tr>
                <th>Beschreibung</th>
                <th>Betrag</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="einnahme in ungeplannteEinnahmen" :key="einnahme.id">
                <td>{{ einnahme.beschreibung }}</td>
                <td>{{ einnahme.betrag }}€</td>
              </tr>
              <!-- Summenzeile für ungeplante Einnahmen -->
              <tr class="summen-zeile" v-if="ungeplannteEinnahmen.length > 0">
                <td><strong>Summe</strong></td>
                <td><strong>{{ summeUngeplannteEinnahmen }} €</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
const apiBaseUrl = process.env.VUE_APP_API_BASE_URL;

// API-Endpunkte für die verschiedenen Funktionen
const monatsuebersichtUrl = `${apiBaseUrl}/monatsuebersicht`;
const monatswerteUrl = `${apiBaseUrl}/monatswerte`;
const ungeplanteTrxUrl = `${apiBaseUrl}/ungeplante-transaktionen`;


export default {
  name: "MonatsUebersicht",
  props: ["monat", "jahr"],
  data() {
    return {
      // Your existing data properties
      festeAusgaben: [],
      festeEinnahmen: [],
      ungeplannteAusgaben: [],
      ungeplannteEinnahmen: [],
      newAusgabe: {
        beschreibung: '',
        betrag: null,
        kommentar: '',
        typ: 'ausgabe',
        monat: null,
        jahr: null
      },
      newEinnahme: {
        beschreibung: '',
        betrag: null,
        typ: 'einnahme',
        monat: null,
        jahr: null
      },
      
      // New properties for month/year selection
      selectedMonth: parseInt(this.monat),
      selectedYear: parseInt(this.jahr),
      monate: [
        'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 
        'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
      ],
      jahre: [],
      kategorienReihenfolge: ['Versicherungen', 'Autos', 'Kredite', 'Haus', 'Kinder', 'Hund', 'Sonstiges', 'Anteile Andrea'],
    };
  },
  computed: {
	// Neue Computed Properties für gruppierte Ansichten
    gruppiertFesteAusgaben() {
      const gruppiert = {};
      this.festeAusgaben.forEach(ausgabe => {
        // Fallback-Kategorie, falls keine vorhanden ist
        const kategorie = ausgabe.kategorie || 'Sonstige';
        
        if (!gruppiert[kategorie]) {
          gruppiert[kategorie] = [];
        }
        gruppiert[kategorie].push(ausgabe);
      });
      // Erstellt ein neues Objekt mit sortierter Reihenfolge
      const sortiert = {};
      // Zuerst die definierten Kategorien in der gewünschten Reihenfolge
      this.kategorienReihenfolge.forEach(kategorie => {
        if (gruppiert[kategorie]) {
          sortiert[kategorie] = gruppiert[kategorie];
        }
      });
      // Dann alle übrigen Kategorien, die nicht in der Reihenfolge definiert sind
      Object.keys(gruppiert).forEach(kategorie => {
        if (!sortiert[kategorie]) {
          sortiert[kategorie] = gruppiert[kategorie];
        }
      });
      return sortiert;
    },
    
    gruppiertFesteEinnahmen() {
      const gruppiert = {};
      this.festeEinnahmen.forEach(einnahme => {
        // Fallback-Kategorie, falls keine vorhanden ist
        const kategorie = einnahme.kategorie || 'Sonstige';
        
        if (!gruppiert[kategorie]) {
          gruppiert[kategorie] = [];
        }
        gruppiert[kategorie].push(einnahme);
      });
		// Erstellt ein neues Objekt mit sortierter Reihenfolge
      const sortiert = {};
      // Zuerst die definierten Kategorien in der gewünschten Reihenfolge
      this.kategorienReihenfolge.forEach(kategorie => {
        if (gruppiert[kategorie]) {
          sortiert[kategorie] = gruppiert[kategorie];
        }
      });
      // Dann alle übrigen Kategorien, die nicht in der Reihenfolge definiert sind
      Object.keys(gruppiert).forEach(kategorie => {
        if (!sortiert[kategorie]) {
          sortiert[kategorie] = gruppiert[kategorie];
        }
      });
      return sortiert;
    },
    // Your existing computed properties remain unchanged
    summeFesteAusgabenSoll() {
      return this.festeAusgaben.reduce((sum, ausgabe) => sum + ausgabe.betrag, 0).toFixed(2);
    },
    summeFesteAusgabenIst() {
      return this.festeAusgaben.reduce((sum, ausgabe) => sum + (ausgabe.ist_wert || 0), 0).toFixed(2);
    },
    summeFesteAusgabenAbweichung() {
      return (parseFloat(this.summeFesteAusgabenIst) - parseFloat(this.summeFesteAusgabenSoll)).toFixed(2);
    },
    summeFesteEinnahmenSoll() {
      return this.festeEinnahmen.reduce((sum, einnahme) => sum + einnahme.betrag, 0).toFixed(2);
    },
    summeFesteEinnahmenIst() {
      return this.festeEinnahmen.reduce((sum, einnahme) => sum + (einnahme.ist_wert || 0), 0).toFixed(2);
    },
    summeFesteEinnahmenAbweichung() {
      return (parseFloat(this.summeFesteEinnahmenIst) - parseFloat(this.summeFesteEinnahmenSoll)).toFixed(2);
    },
    summeUngeplannteAusgaben() {
      return this.ungeplannteAusgaben.reduce((sum, ausgabe) => sum + ausgabe.betrag, 0).toFixed(2);
    },
    summeUngeplannteEinnahmen() {
      return this.ungeplannteEinnahmen.reduce((sum, einnahme) => sum + einnahme.betrag, 0).toFixed(2);
    },
    gesamtbilanzSoll() {
      return (parseFloat(this.summeFesteEinnahmenSoll) - parseFloat(this.summeFesteAusgabenSoll)).toFixed(2);
    },
    gesamtbilanzIst() {
      return (parseFloat(this.summeFesteEinnahmenIst) - parseFloat(this.summeFesteAusgabenIst)).toFixed(2);
    },
    gesamtbilanzAbweichung() {
      return (parseFloat(this.gesamtbilanzIst) - parseFloat(this.gesamtbilanzSoll)).toFixed(2);
    }
  },
  created() {
    // Generate a range of years (e.g., last 5 years to next 5 years)
    const currentYear = new Date().getFullYear();
    for (let i = currentYear - 5; i <= currentYear + 5; i++) {
      this.jahre.push(i);
    }
  },
  mounted() {
    this.ladeMonatsUebersicht();
  },
  methods: {
    // New methods for month/year navigation
    updateRoute() {
      this.$router.push({
        name: 'MonatsUebersicht',
        params: {
          monat: this.selectedMonth,
          jahr: this.selectedYear
        }
      });
    },
    previousMonth() {
      if (this.selectedMonth === 1) {
        this.selectedMonth = 12;
        this.selectedYear--;
      } else {
        this.selectedMonth--;
      }
      this.updateRoute();
    },
    nextMonth() {
      if (this.selectedMonth === 12) {
        this.selectedMonth = 1;
        this.selectedYear++;
      } else {
        this.selectedMonth++;
      }
      this.updateRoute();
    },
    
    // Your existing methods
    async ladeMonatsUebersicht() {
      try {
		const response = await axios.get(`${monatsuebersichtUrl}/${this.monat}/${this.jahr}`);

        console.log("API Response:", response.data);
        
        this.festeAusgaben = response.data.feste_ausgaben.map(ausgabe => ({ ...ausgabe, ist_wert: 0 }));
        this.festeEinnahmen = response.data.feste_einnahmen.map(einnahme => ({ ...einnahme, ist_wert: 0 }));
        
        await this.ladeIstWerte();
        await this.ladeUngeplannteTransaktionen();
        
      } catch (error) {
        console.error("Fehler beim Laden der Daten:", error);
      }
    },
    
    async ladeIstWerte() {
      try {
		const istWerteResponse = await axios.get(`${monatswerteUrl}/${this.monat}/${this.jahr}`);

        const istWerte = istWerteResponse.data.monatswerte;
        
        istWerte.forEach(wert => {
          if (wert.kategorie === "ausgabe") {
            let eintrag = this.festeAusgaben.find(a => a.id === wert.eintrag_id);
            if (eintrag) eintrag.ist_wert = wert.ist;
          } else {
            let eintrag = this.festeEinnahmen.find(e => e.id === wert.eintrag_id);
            if (eintrag) eintrag.ist_wert = wert.ist;
          }
        });
      } catch (error) {
        console.error("Fehler beim Laden der Ist-Werte:", error);
      }
    },
    
    async ladeUngeplannteTransaktionen() {
      try {
        const ungeplannteResponse = await axios.get(`${ungeplanteTrxUrl}/${this.monat}/${this.jahr}`);
        this.ungeplannteAusgaben = ungeplannteResponse.data.filter(t => t.typ === 'ausgabe');
        this.ungeplannteEinnahmen = ungeplannteResponse.data.filter(t => t.typ === 'einnahme');
      } catch (error) {
        console.error("Fehler beim Laden der ungeplanten Transaktionen:", error);
      }
    },

    async speichereIstWert(eintrag_id, wert, kategorie, beschreibung, betrag) {
      try {
        const response = await axios.post(`${monatswerteUrl}/`, {
          eintrag_id,
          monat: this.monat,
          jahr: this.jahr,
          kategorie,
          beschreibung,
          soll: betrag,
          ist: wert
        });
        console.log("Ist-Wert gespeichert:", wert);
        console.log("Antwort vom Server:", response.data);
      } catch (error) {
        console.error("Fehler beim Speichern:", error);
      }
    },

    async addAusgabe() {
      try {
        this.newAusgabe.monat = this.monat;
        this.newAusgabe.jahr = this.jahr;
		const response = await axios.post(ungeplanteTrxUrl, this.newAusgabe);

        this.ungeplannteAusgaben.push(response.data);
        
        this.newAusgabe = {
          beschreibung: '',
          betrag: null,
          kommentar: '',
          typ: 'ausgabe',
          monat: this.monat,
          jahr: this.jahr
        };
      } catch (error) {
        console.error("Fehler beim Hinzufügen der Ausgabe:", error);
      }
    },
    
    async addEinnahme() {
      try {
        this.newEinnahme.monat = this.monat;
        this.newEinnahme.jahr = this.jahr;
        
		const response = await axios.post(ungeplanteTrxUrl, this.newEinnahme);
        this.ungeplannteEinnahmen.push(response.data);
        
        this.newEinnahme = {
          beschreibung: '',
          betrag: null,
          typ: 'einnahme',
          monat: this.monat,
          jahr: this.jahr
        };
      } catch (error) {
        console.error("Fehler beim Hinzufügen der Einnahme:", error);
      }
    },
    
    createAusgleich(ausgabe) {
      this.newEinnahme.beschreibung = `Ausgleich: ${ausgabe.beschreibung}`;
      this.newEinnahme.betrag = ausgabe.betrag;
    },
	
	berechneSummeSoll(items) {
      return items.reduce((sum, item) => sum + item.betrag, 0).toFixed(2);
    },

    berechneSummeIst(items) {
       return items.reduce((sum, item) => sum + (item.ist_wert || 0), 0).toFixed(2);
    },

    berechneSummeAbweichung(items) {
      const soll = parseFloat(this.berechneSummeSoll(items));
      const ist = parseFloat(this.berechneSummeIst(items));
      return (ist - soll).toFixed(2);
    } 
  },
  watch: {
    // Watch for route changes to reload data
    $route(to) {
      if (to.params.monat && to.params.jahr) {
        this.selectedMonth = parseInt(to.params.monat);
        this.selectedYear = parseInt(to.params.jahr);
        this.ladeMonatsUebersicht();
      }
    }
  }
};

</script>
<style scoped>
.month-selector {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selectors {
  display: flex;
  gap: 10px;
}

.navigation-buttons {
  display: flex;
  gap: 10px;
}

select, button {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

button {
  cursor: pointer;
  background-color: #f0f0f0;
}

button:hover {
  background-color: #e0e0e0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}
th, td {
  padding: 8px;
  border: 1px solid #ddd;
}
.text-red-500 {
  color: red;
}
.text-green-500 {
  color: green;
}
.row {
  display: flex;
  gap: 20px;
}
.col {
  flex: 1;
}
.summen-zeile {
  background-color: #f3f3f3;
  font-weight: bold;
}
.gesamtbilanz {
  margin-top: 20px;
  margin-bottom: 30px;
}
input[type="number"] {
  width: 100px;
}
</style>