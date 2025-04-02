<template>
  <div class="konfiguration-container">
    <h1>Konfiguration fester Posten</h1>
    
    <!-- Tabs für Ausgaben/Einnahmen -->
    <div class="tabs">
      <button 
        :class="{ active: activeTab === 'ausgaben' }" 
        @click="activeTab = 'ausgaben'"
      >
        Feste Ausgaben
      </button>
      <button 
        :class="{ active: activeTab === 'einnahmen' }" 
        @click="activeTab = 'einnahmen'"
      >
        Feste Einnahmen
      </button>
    </div>
    
    <!-- Feste Ausgaben -->
    <div v-if="activeTab === 'ausgaben'" class="tab-content">
      <div class="header-with-button">
        <h2>Feste Ausgaben</h2>
        <button @click="showNeueAusgabeForm = true" class="add-button">Neue Ausgabe hinzufügen</button>
      </div>
      
      <!-- Popup-Formular für neue Ausgabe -->
      <div v-if="showNeueAusgabeForm" class="modal">
        <div class="modal-content">
          <h3>Neue feste Ausgabe</h3>
          <form @submit.prevent="addFesteAusgabe">
            <div class="form-group">
              <label for="beschreibung">Beschreibung:</label>
              <input id="beschreibung" v-model="neueAusgabe.beschreibung" required />
            </div>
            
            <div class="form-group">
              <label for="betrag">Betrag (€):</label>
              <input id="betrag" type="number" step="0.01" v-model.number="neueAusgabe.betrag" required />
            </div>
            
            <div class="form-group">
              <label for="kategorie">Kategorie:</label>
              <select id="kategorie" v-model="neueAusgabe.kategorie" required>
				<option v-for="kategorie in kategorienReihenfolge" :key="kategorie" :value="kategorie">
					{{ kategorie }}
				</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="zahlungsintervall">Zahlungsintervall:</label>
              <select id="zahlungsintervall" v-model="neueAusgabe.zahlungsintervall" required>
                <option value="monatlich">Monatlich</option>
                <option value="zweimonatlich">Zweimonatlich</option>
                <option value="vierteljährlich">Vierteljährlich</option>
                <option value="halbjährlich">Halbjährlich</option>
                <option value="jährlich">Jährlich</option>
                <option value="benutzerdefiniert">Benutzerdefiniert</option>
              </select>
            </div>
			
			<div class="form-group" v-if="neueAusgabe.zahlungsintervall === 'vierteljährlich'">
				<label for="vierteljahr-startmonat">Startmonat für vierteljährliche Zahlung:</label>
				<select 
					id="vierteljahr-startmonat" 
					v-model="vierteljahrStartmonat" 
					@change="setQuarterlyPaymentMonths">
					<option value="1">Januar</option>
					<option value="2">Februar</option>
					<option value="3">März</option>
				</select>
			</div>

			<!-- Direkt nach dem Zahlungsintervall-Dropdown -->
			<div class="form-group" v-if="neueAusgabe.zahlungsintervall === 'jährlich'">
				<label for="jaehrlicher-monat">Zahlungsmonat für jährliche Zahlung:</label>
				<select 
					id="jaehrlicher-monat" 
					v-model="jahresZahlungsmonat" 
					@change="setYearlyPaymentMonth">
					<option v-for="n in 12" :key="n" :value="n">{{ getMonthName(n) }}</option>
				</select>
			</div>
            
            <!-- Im Formular für neue Ausgaben -->
            <div class="form-group" v-if="neueAusgabe.zahlungsintervall !== 'jährlich' && neueAusgabe.zahlungsintervall !== 'vierteljährlich'">
            <label>Zahlungsmonate:</label>
              <div class="monate-grid">
                <label v-for="n in 12" :key="n" class="monat-checkbox">
                  <input 
                    type="checkbox" 
                    :value="n" 
                    v-model="neueAusgabe.zahlungsmonate"
                    :disabled="neueAusgabe.zahlungsintervall !== 'benutzerdefiniert' && 
                     !isMonthIncludedInInterval(n)"
                  />
                 {{ getMonthName(n) }}
                </label>
              </div>
            </div>
            
            <div class="form-group">
              <label for="startdatum">Startdatum:</label>
              <input id="startdatum" type="date" v-model="neueAusgabe.startdatum" required />
            </div>
            
            <div class="form-actions">
              <button type="submit" class="save-button">Speichern</button>
              <button type="button" @click="showNeueAusgabeForm = false" class="cancel-button">Abbrechen</button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- Liste der festen Ausgaben -->
      <div class="data-table-container">
        <table v-if="sortierteFesteAusgaben.length > 0">
          <thead>
            <tr>
              <th>Beschreibung</th>
              <th>Betrag</th>
              <th>Kategorie</th>
              <th>Zahlungsintervall</th>
              <th>Monate</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ausgabe in sortierteFesteAusgaben" :key="ausgabe.id">
              <td>{{ ausgabe.beschreibung }}</td>
              <td>{{ ausgabe.betrag }} €</td>
              <td>{{ ausgabe.kategorie }}</td>
              <td>{{ ausgabe.zahlungsintervall }}</td>
              <td>
                <div class="monate-tags">
                  <span v-for="monat in formatZahlungsmonate(ausgabe.zahlungsmonate)" :key="monat" class="monat-tag">
                    {{ monat }}
                  </span>
                </div>
              </td>
              <td>
                <button @click="editAusgabe(ausgabe)" class="edit-button">Bearbeiten</button>
                <button @click="deleteAusgabe(ausgabe.id)" class="delete-button">Löschen</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="no-data">
          Keine festen Ausgaben konfiguriert.
        </div>
      </div>
      
      <!-- Bearbeiten-Modal -->
      <div v-if="showEditAusgabeForm" class="modal">
        <div class="modal-content">
          <h3>Ausgabe bearbeiten</h3>
          <form @submit.prevent="updateFesteAusgabe">
            <!-- Gleiche Felder wie beim Hinzufügen -->
            <div class="form-group">
              <label for="edit-beschreibung">Beschreibung:</label>
              <input id="edit-beschreibung" v-model="editedAusgabe.beschreibung" required />
            </div>
            
            <div class="form-group">
              <label for="edit-betrag">Betrag (€):</label>
              <input id="edit-betrag" type="number" step="0.01" v-model.number="editedAusgabe.betrag" required />
            </div>
            
            <div class="form-group">
              <label for="edit-kategorie">Kategorie:</label>
              <select id="edit-kategorie" v-model="editedAusgabe.kategorie" required>
                <option v-for="kategorie in kategorienReihenfolge" :key="kategorie" :value="kategorie">
                   {{ kategorie }}
                </option>
              </select>
              
            </div>
            
            <div class="form-group">
              <label for="edit-zahlungsintervall">Zahlungsintervall:</label>
              <select id="edit-zahlungsintervall" v-model="editedAusgabe.zahlungsintervall" required>
                <option value="monatlich">Monatlich</option>
                <option value="zweimonatlich">Zweimonatlich</option>
                <option value="vierteljährlich">Vierteljährlich</option>
                <option value="halbjährlich">Halbjährlich</option>
                <option value="jährlich">Jährlich</option>
                <option value="benutzerdefiniert">Benutzerdefiniert</option>
              </select>
            </div>
			
			<div class="form-group" v-if="editedAusgabe.zahlungsintervall === 'vierteljährlich'">
				<label for="edit-vierteljahr-startmonat">Startmonat für vierteljährliche Zahlung:</label>
				<select 
					id="edit-vierteljahr-startmonat" 
					v-model="editVierteljahrStartmonat" 
					@change="setEditQuarterlyPaymentMonths">
					<option value="1">Januar</option>
					<option value="2">Februar</option>
					<option value="3">März</option>
				</select>
			</div>
			
            <div class="form-group" v-if="editedAusgabe.zahlungsintervall === 'jährlich'">
              <label for="edit-jaehrlicher-monat">Zahlungsmonat für jährliche Zahlung:</label>
              <select 
                id="edit-jaehrlicher-monat" 
                v-model="editJahresZahlungsmonat" 
                @change="setEditYearlyPaymentMonth">
               <option v-for="n in 12" :key="n" :value="n">{{ getMonthName(n) }}</option>
              </select>
            </div>
            
			<div class="form-group" v-if="editedAusgabe.zahlungsintervall !== 'jährlich' && editedAusgabe.zahlungsintervall !== 'vierteljährlich'">
            <label>Zahlungsmonate:</label>
				<div class="monate-grid">
					<label v-for="n in 12" :key="n" class="monat-checkbox">
						<input 
							type="checkbox" 
							:value="n" 
							v-model="editedAusgabe.zahlungsmonate"
							:disabled="editedAusgabe.zahlungsintervall !== 'benutzerdefiniert' && 
										!isMonthIncludedInInterval(n, editedAusgabe.zahlungsintervall)"
						/>
						{{ getMonthName(n) }}
					</label>
				</div>
			</div>
            
            <div class="form-group">
              <label for="edit-startdatum">Startdatum:</label>
              <input id="edit-startdatum" type="date" v-model="editedAusgabe.startdatum" required />
            </div>
            
            <div class="form-actions">
              <button type="submit" class="save-button">Speichern</button>
              <button type="button" @click="showEditAusgabeForm = false" class="cancel-button">Abbrechen</button>
            </div>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Feste Einnahmen -->
    <div v-if="activeTab === 'einnahmen'" class="tab-content">
      <div class="header-with-button">
        <h2>Feste Einnahmen</h2>
        <button @click="showNeueEinnahmeForm = true" class="add-button">Neue Einnahme hinzufügen</button>
      </div>
      
      <!-- Popup-Formular für neue Einnahme -->
      <div v-if="showNeueEinnahmeForm" class="modal">
        <div class="modal-content">
          <h3>Neue feste Einnahme</h3>
          <form @submit.prevent="addFesteEinnahme">
            <div class="form-group">
              <label for="name">Name:</label>
              <input id="name" v-model="neueEinnahme.name" required />
            </div>
            
            <div class="form-group">
              <label for="einnahme-betrag">Betrag (€):</label>
              <input id="einnahme-betrag" type="number" step="0.01" v-model.number="neueEinnahme.betrag" required />
            </div>
            
            <div class="form-group">
              <label>Zahlungsmonate:</label>
              <div class="monate-grid">
                <label v-for="n in 12" :key="n" class="monat-checkbox">
                  <input type="checkbox" :value="n" v-model="neueEinnahme.zahlungsmonate" />
                  {{ getMonthName(n) }}
                </label>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="submit" class="save-button">Speichern</button>
              <button type="button" @click="showNeueEinnahmeForm = false" class="cancel-button">Abbrechen</button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- Liste der festen Einnahmen -->
      <div class="data-table-container">
        <table v-if="festeEinnahmen.length > 0">
          <thead>
            <tr>
              <th>Name</th>
              <th>Betrag</th>
              <th>Monate</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="einnahme in festeEinnahmen" :key="einnahme.id">
              <td>{{ einnahme.name }}</td>
              <td>{{ einnahme.betrag }} €</td>
              <td>
                <div class="monate-tags">
                  <span v-for="monat in formatZahlungsmonate(einnahme.zahlungsmonate)" :key="monat" class="monat-tag">
                    {{ monat }}
                  </span>
                </div>
              </td>
              <td>
                <button @click="editEinnahme(einnahme)" class="edit-button">Bearbeiten</button>
                <button @click="deleteEinnahme(einnahme.id)" class="delete-button">Löschen</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="no-data">
          Keine festen Einnahmen konfiguriert.
        </div>
      </div>
      
      <!-- Bearbeiten-Modal für Einnahmen -->
      <div v-if="showEditEinnahmeForm" class="modal">
        <div class="modal-content">
          <h3>Einnahme bearbeiten</h3>
          <form @submit.prevent="updateFesteEinnahme">
            <div class="form-group">
              <label for="edit-name">Name:</label>
              <input id="edit-name" v-model="editedEinnahme.name" required />
            </div>
            
            <div class="form-group">
              <label for="edit-einnahme-betrag">Betrag (€):</label>
              <input id="edit-einnahme-betrag" type="number" step="0.01" v-model.number="editedEinnahme.betrag" required />
            </div>
            
            <div class="form-group">
              <label>Zahlungsmonate:</label>
              <div class="monate-grid">
                <label v-for="n in 12" :key="n" class="monat-checkbox">
                  <input type="checkbox" :value="n" v-model="editedEinnahme.zahlungsmonate" />
                  {{ getMonthName(n) }}
                </label>
              </div>
            </div>
            
            <div class="form-actions">
              <button type="submit" class="save-button">Speichern</button>
              <button type="button" @click="showEditEinnahmeForm = false" class="cancel-button">Abbrechen</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

const apiBaseUrl = process.env.VUE_APP_API_BASE_URL;
const apiUrlAusgabe = `${apiBaseUrl}/feste-ausgaben`;
const apiUrlEinnahme = `${apiBaseUrl}/feste_einnahmen`;

export default {  
  name: "FesteKonfiguration",
  data() {
    return {
		jahresZahlungsmonat: 1,
		editJahresZahlungsmonat: 1,
		vierteljahrStartmonat: 1,
		editVierteljahrStartmonat: 1,
      activeTab: "ausgaben",
      festeAusgaben: [],
      festeEinnahmen: [],
      showNeueAusgabeForm: false,
      showNeueEinnahmeForm: false,
      showEditAusgabeForm: false,
      showEditEinnahmeForm: false,
      neueAusgabe: {
        beschreibung: "",
        betrag: null,
        kategorie: "Sonstiges",
        zahlungsintervall: "monatlich",
        zahlungsmonate: [],
        startdatum: new Date().toISOString().split('T')[0]
      },
      editedAusgabe: {
        id: null,
        beschreibung: "",
        betrag: null,
        kategorie: "",
        zahlungsintervall: "",
        zahlungsmonate: [],
        startdatum: ""
      },
      neueEinnahme: {
        name: "",
        betrag: null,
        zahlungsmonate: []
      },
      editedEinnahme: {
        id: null,
        name: "",
        betrag: null,
        zahlungsmonate: []
      },
      kategorienReihenfolge: [
       "Versicherungen",
       "Autos",
       "Kredite",
       "Haus",
       "Kinder",
       "Hund",
       "Sonstiges",
       "Anteile Andrea"
      ],
    };
  },
  mounted() {
    this.fetchFesteAusgaben();
    this.fetchFesteEinnahmen();
    this.initStandardZahlungsmonate();
  },
  computed: {
    sortierteFesteAusgaben() {
      // Kopie erstellen, um die Original-Array nicht zu verändern
      return [...this.festeAusgaben].sort((a, b) => {
        const indexA = this.kategorienReihenfolge.indexOf(a.kategorie);
        const indexB = this.kategorienReihenfolge.indexOf(b.kategorie);
      
        // Falls eine Kategorie nicht in der Liste ist, ans Ende stellen
        if (indexA === -1) return 1;
        if (indexB === -1) return -1;
      
        return indexA - indexB;
      });
    }
  },
  methods: {
  setYearlyPaymentMonth() {
    if(this.neueAusgabe.zahlungsintervall === 'jährlich') {
      this.neueAusgabe.zahlungsmonate = [this.jahresZahlungsmonat];
      // Erzwinge eine Neuberechnung der Benutzeroberfläche
      this.$forceUpdate();
    }
  },
  
  setEditYearlyPaymentMonth() {
    if(this.editedAusgabe.zahlungsintervall === 'jährlich') {
      this.editedAusgabe.zahlungsmonate = [this.editJahresZahlungsmonat];
      // Erzwinge eine Neuberechnung der Benutzeroberfläche
      this.$forceUpdate();
    }
  },
  
  setQuarterlyPaymentMonths() {
    if (this.neueAusgabe.zahlungsintervall === 'vierteljährlich') {
      const start = parseInt(this.vierteljahrStartmonat);
      this.neueAusgabe.zahlungsmonate = [
        start,
        start + 3 > 12 ? start + 3 - 12 : start + 3,
        start + 6 > 12 ? start + 6 - 12 : start + 6,
        start + 9 > 12 ? start + 9 - 12 : start + 9
      ];
      this.$forceUpdate();
    }
  },
  
  setEditQuarterlyPaymentMonths() {
    if (this.editedAusgabe.zahlungsintervall === 'vierteljährlich') {
      const start = parseInt(this.editVierteljahrStartmonat);
      this.editedAusgabe.zahlungsmonate = [
        start,
        start + 3 > 12 ? start + 3 - 12 : start + 3,
        start + 6 > 12 ? start + 6 - 12 : start + 6,
        start + 9 > 12 ? start + 9 - 12 : start + 9
      ];
      this.$forceUpdate();
    }
  },
	
    // Fetch-Methoden
    async fetchFesteAusgaben() {
      try {
        // const response = await axios.get("http://192.168.178.138:8000/feste-ausgaben/");
		const response = await axios.get(`${apiUrlAusgabe}/`);

        this.festeAusgaben = response.data;
      } catch (error) {
        console.error("Fehler beim Laden der festen Ausgaben:", error);
      }
    },
    
   async fetchFesteEinnahmen() {
  try {
    //const response = await axios.get("http://192.168.178.138:8000/feste_einnahmen");
	const response = await axios.get(apiUrlEinnahme);
    if (response.data && response.data.feste_einnahmen) {
      this.festeEinnahmen = response.data.feste_einnahmen;
    } else {
      console.error("Keine festen Einnahmen im API-Response gefunden");
    }
   } catch (error) {
    console.error("Fehler beim Laden der festen Einnahmen:", error);
    // Falls API noch nicht aktualisiert wurde, versuche die alte Methode als Fallback
    try {
      //const allMonthsResponse = await axios.get("http://192.168.178.138:8000/feste_einnahmen/0");
      const allMonthsResponse = await axios.get(`${apiUrlEinnahme}/0`);
      if (allMonthsResponse.data && allMonthsResponse.data.feste_einnahmen) {
        this.festeEinnahmen = allMonthsResponse.data.feste_einnahmen;
      } else {
        // Fallback: Versuche einen beliebigen Monat (z.B. Januar)
        //const janResponse = await axios.get("http://192.168.178.138:8000/feste_einnahmen/1");
        const janResponse = await axios.get(`${apiUrlEinnahme}/1`);
        if (janResponse.data && janResponse.data.feste_einnahmen) {
          this.festeEinnahmen = janResponse.data.feste_einnahmen;
        }
      }
    } catch (fallbackError) {
      console.error("Auch Fallback fehlgeschlagen:", fallbackError);
    }
   }
  },

    // Initialisierung der Standardzahlungsmonate basierend auf dem Intervall
    initStandardZahlungsmonate() {
      // Standardmäßig monatliche Zahlung (alle Monate)
      if (this.neueAusgabe.zahlungsintervall === "monatlich") {
        this.neueAusgabe.zahlungsmonate = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
      }
    },
    
    // Überprüft, ob ein Monat in das gewählte Intervall passt
	isMonthIncludedInInterval(month, interval = this.neueAusgabe.zahlungsintervall) {
	if (interval === "benutzerdefiniert") return true;
	if (interval === "monatlich") return true;
	if (interval === "zweimonatlich") return month % 2 === 1;
	if (interval === "vierteljährlich") return month % 3 === 1;
	if (interval === "halbjährlich") return month === 1 || month === 7;
	if (interval === "jährlich") return true; // Erlaube alle Monate für jährliche Zahlungen
	return false;
	},

	// Aktualisiert die Zahlungsmonate basierend auf dem Intervall
	updateZahlungsmonate() {
    const interval = this.neueAusgabe.zahlungsintervall;
    if (interval === "benutzerdefiniert") return;
    
    if (interval === "monatlich") {
      this.neueAusgabe.zahlungsmonate = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    } else if (interval === "zweimonatlich") {
      this.neueAusgabe.zahlungsmonate = [1, 3, 5, 7, 9, 11];
    } else if (interval === "vierteljährlich") {
      // Bei vierteljährlicher Zahlung den ausgewählten Startmonat verwenden
      const start = parseInt(this.vierteljahrStartmonat);
      this.neueAusgabe.zahlungsmonate = [
        start,
        start + 3 > 12 ? start + 3 - 12 : start + 3,
        start + 6 > 12 ? start + 6 - 12 : start + 6,
        start + 9 > 12 ? start + 9 - 12 : start + 9
      ];
    } else if (interval === "halbjährlich") {
      this.neueAusgabe.zahlungsmonate = [1, 7];
    } else if (interval === "jährlich") {
      // Bei jährlicher Zahlung den aktuell ausgewählten Monat verwenden
      this.neueAusgabe.zahlungsmonate = [this.jahresZahlungsmonat];
    }
	},
	// Jährlichen Zahlungsmonat ändern
	updateYearlyPaymentMonth() {
      if (this.neueAusgabe.zahlungsintervall === "jährlich") {
		// Stellt sicher, dass nur ein Monat ausgewählt ist
		this.neueAusgabe.zahlungsmonate = [this.neueAusgabe.zahlungsmonate[0]];
      }
	},
	
	// Jährlichen Zahlungsmonat für zu bearbeitende Ausgabe ändern
	updateEditedYearlyPaymentMonth() {
      if (this.editedAusgabe.zahlungsintervall === "jährlich") {
		// Stellt sicher, dass nur ein Monat ausgewählt ist
		this.editedAusgabe.zahlungsmonate = [this.editedAusgabe.zahlungsmonate[0]];
      }
	},
    
    // Format-Hilfsfunktion
    formatZahlungsmonate(monate) {
      if (!monate || !Array.isArray(monate)) return [];
      return monate.map(m => this.getMonthName(m));
    },
    
    // Monatsname abrufen
    getMonthName(month) {
      const months = [
        "Jan", "Feb", "Mär", "Apr", "Mai", "Jun", 
        "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"
      ];
      return months[month - 1];
    },
    
    // Formular-Aktionen für Ausgaben
    async addFesteAusgabe() {
      try {
        // Aktualisiere Zahlungsmonate wenn nicht benutzerdefiniert
        if (this.neueAusgabe.zahlungsintervall !== "benutzerdefiniert") {
          this.updateZahlungsmonate();
        }
        
        const response = await axios.post(
          //"http://192.168.178.138:8000/feste-ausgaben/", 
           `${apiUrlAusgabe}/`,
          this.neueAusgabe
        );
        
        // Neue Ausgabe zur Liste hinzufügen
        this.festeAusgaben.push(response.data);
        
        // Formular zurücksetzen
        this.neueAusgabe = {
          beschreibung: "",
          betrag: null,
          kategorie: "Sonstiges",
          zahlungsintervall: "monatlich",
          zahlungsmonate: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
          startdatum: new Date().toISOString().split('T')[0]
        };
        
        // Modal schließen
        this.showNeueAusgabeForm = false;
      } catch (error) {
          console.error("Fehler beim Speichern der Ausgabe:", error);
          console.log("Response data:", error.response?.data);
          console.log("Status:", error.response?.status);
          console.log("Headers:", error.response?.headers);
          alert("Fehler beim Speichern: " + JSON.stringify(error.response?.data || error.message));
        }
    },
    
    editAusgabe(ausgabe) {
      // Tiefe Kopie der Ausgabe erstellen
      this.editedAusgabe = JSON.parse(JSON.stringify(ausgabe));
      
      // Datum-Format anpassen
      if (typeof this.editedAusgabe.startdatum === 'string' && this.editedAusgabe.startdatum.includes('T')) {
        this.editedAusgabe.startdatum = this.editedAusgabe.startdatum.split('T')[0];
      }
	// Bei jährlicher Zahlung den ausgewählten Monat ins Select-Feld übernehmen
    if (ausgabe.zahlungsintervall === 'jährlich' && ausgabe.zahlungsmonate && ausgabe.zahlungsmonate.length > 0) {
      this.editJahresZahlungsmonat = ausgabe.zahlungsmonate[0];
    }
	
	if (ausgabe.zahlungsintervall === 'vierteljährlich' && ausgabe.zahlungsmonate && ausgabe.zahlungsmonate.length > 0) {
      // Wir nehmen den ersten Monat im Array als Startmonat
      const possibleStartMonths = [1, 2, 3];
      const firstMonth = ausgabe.zahlungsmonate[0];
      
      // Prüfen, ob der erste Monat ein gültiger Startmonat ist
      if (possibleStartMonths.includes(firstMonth)) {
        this.editVierteljahrStartmonat = firstMonth;
      } else {
        // Falls nicht, versuchen wir den Startmonat anhand des Musters zu erkennen
        const sortedMonths = [...ausgabe.zahlungsmonate].sort((a, b) => a - b);
        if (sortedMonths.length === 4) {
          // Prüfen, ob die Monate einem 3-Monats-Muster folgen
          for (let start of possibleStartMonths) {
            const pattern = [
              start,
              start + 3 > 12 ? start + 3 - 12 : start + 3,
              start + 6 > 12 ? start + 6 - 12 : start + 6,
              start + 9 > 12 ? start + 9 - 12 : start + 9
            ].sort((a, b) => a - b);
            
            // Prüfen, ob die Monate dem Muster entsprechen
            if (JSON.stringify(pattern) === JSON.stringify(sortedMonths)) {
              this.editVierteljahrStartmonat = start;
              break;
            }
          }
        }
      }
    }
      
      this.showEditAusgabeForm = true;
    },
    
    async updateFesteAusgabe() {
      try {
        // Aktualisiere Zahlungsmonate wenn nicht benutzerdefiniert
        if (this.editedAusgabe.zahlungsintervall !== "benutzerdefiniert") {
          const interval = this.editedAusgabe.zahlungsintervall;
          if (interval === "monatlich") {
            this.editedAusgabe.zahlungsmonate = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
          } else if (interval === "zweimonatlich") {
            this.editedAusgabe.zahlungsmonate = [1, 3, 5, 7, 9, 11];
          } else if (interval === "vierteljährlich") {
            this.editedAusgabe.zahlungsmonate = [1, 4, 7, 10];
          } else if (interval === "halbjährlich") {
            this.editedAusgabe.zahlungsmonate = [1, 7];
          } else if (interval === "jährlich") {
            this.editedAusgabe.zahlungsmonate = [1];
          }
        }
        
        await axios.put(
          // `http://192.168.178.138:8000/feste-ausgaben/${this.editedAusgabe.id}`, 
          `${apiUrlAusgabe}/${this.editedAusgabe.id}`,
          this.editedAusgabe
        );
        
        // Aktualisierte Liste neu laden
        await this.fetchFesteAusgaben();
        
        // Modal schließen
        this.showEditAusgabeForm = false;
      } catch (error) {
        console.error("Fehler beim Aktualisieren der Ausgabe:", error);
        alert("Fehler beim Aktualisieren: " + (error._response?.data?.detail || error.message));
      }
    },
    
    async deleteAusgabe(id) {
      if (!confirm("Möchtest du diese feste Ausgabe wirklich löschen?")) return;
      
      try {
        // await axios.delete(`http://192.168.178.138:8000/feste-ausgaben/${id}`);
		await axios.delete(`${apiUrlAusgabe}/${id}`);
        
        // Ausgabe aus der Liste entfernen
        this.festeAusgaben = this.festeAusgaben.filter(a => a.id !== id);
      } catch (error) {
        console.error("Fehler beim Löschen der Ausgabe:", error);
        alert("Fehler beim Löschen: " + (error.response?.data?.detail || error.message));
      }
    },
    
    // Formular-Aktionen für Einnahmen
    async addFesteEinnahme() {
      try {
        const response = await axios.post(
          // "http://192.168.178.138:8000/feste_einnahmen/", 
          `${apiUrlEinnahme}/`,
          this.neueEinnahme
        );
        
        // Neue Einnahme zur Liste hinzufügen
        if (response.data && response.data.einnahme) {
          this.festeEinnahmen.push(response.data.einnahme);
        } else {
          // Neu laden, falls das Response-Format anders ist
          await this.fetchFesteEinnahmen();
        }
        
        // Formular zurücksetzen
        this.neueEinnahme = {
          name: "",
          betrag: null,
          zahlungsmonate: []
        };
        
        // Modal schließen
        this.showNeueEinnahmeForm = false;
      } catch (error) {
        console.error("Fehler beim Speichern der Einnahme:", error);
        alert("Fehler beim Speichern: " + (error.response?.data?.detail || error.message));
      }
    },
    
    editEinnahme(einnahme) {
      // Tiefe Kopie der Einnahme erstellen
      this.editedEinnahme = JSON.parse(JSON.stringify(einnahme));
      this.showEditEinnahmeForm = true;
    },
    
    async updateFesteEinnahme() {
      try {
       
        await axios.put(
           // `http://192.168.178.138:8000/feste_einnahmen/${this.editedEinnahme.id}`, 
           `${apiUrlEinnahme}/${this.editedEinnahme.id}`,
           this.editedEinnahme
         );
        
        // Aktualisierte Liste neu laden
        await this.fetchFesteEinnahmen();
        
        // Modal schließen
        this.showEditEinnahmeForm = false;
      } catch (error) {
        console.error("Fehler beim Aktualisieren der Einnahme:", error);
        alert("Fehler beim Aktualisieren: " + (error.response?.data?.detail || error.message));
      }
    },
    
    async deleteEinnahme(id) {
      if (!confirm("Möchtest du diese feste Einnahme wirklich löschen?")) return;
      
      try {
        // Da dein API bisher keinen Delete-Endpunkt hat, müssen wir improvisieren
        // Mit einem DELETE würde es so aussehen:
        // await axios.delete(`http://192.168.178.138:8000/feste_einnahmen/${id}`);
		await axios.delete(`${apiUrlEinnahme}/${id}`);
        
       } catch (error) {
        console.error("Fehler beim Löschen der Einnahme:", error);
        alert("Fehler beim Löschen: " + (error.response?.data?.detail || error.message));
      }
	}
  },
  
watch: {
  'neueAusgabe.zahlungsintervall': function(newVal) {
    // Bei Intervallwechsel Monate aktualisieren
    if (newVal === 'jährlich') {
      // Initialisierung für jährliche Zahlungen
      if (this.neueAusgabe.zahlungsmonate && this.neueAusgabe.zahlungsmonate.length > 0) {
        this.jahresZahlungsmonat = this.neueAusgabe.zahlungsmonate[0];
      } else {
        this.jahresZahlungsmonat = 1;
        this.neueAusgabe.zahlungsmonate = [1];
      }
    } else if (newVal === 'vierteljährlich') {
      // Initialisierung für vierteljährliche Zahlungen
      this.vierteljahrStartmonat = 1;
      this.setQuarterlyPaymentMonths();
    } else if (newVal === 'zweimonatlich') {
      this.neueAusgabe.zahlungsmonate = [1, 3, 5, 7, 9, 11];
    } else if (newVal === 'halbjährlich') {
      this.neueAusgabe.zahlungsmonate = [1, 7];
    } else if (newVal === 'monatlich') {
      this.neueAusgabe.zahlungsmonate = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    } else if (newVal === 'benutzerdefiniert') {
      // Bei benutzerdefiniert alle Checkboxen aktivieren/Monate lassen
    }
  },
  
  'editedAusgabe.zahlungsintervall': function(newVal) {
    // Ähnliche Logik für die Bearbeitung
    if (newVal === 'jährlich') {
      if (this.editedAusgabe.zahlungsmonate && this.editedAusgabe.zahlungsmonate.length > 0) {
        this.editJahresZahlungsmonat = this.editedAusgabe.zahlungsmonate[0];
      } else {
        this.editJahresZahlungsmonat = 1;
        this.editedAusgabe.zahlungsmonate = [1];
      }
    } else if (newVal === 'vierteljährlich') {
      this.editVierteljahrStartmonat = 1;
      this.setEditQuarterlyPaymentMonths();
    } else if (newVal === 'zweimonatlich') {
      this.editedAusgabe.zahlungsmonate = [1, 3, 5, 7, 9, 11];
    } else if (newVal === 'halbjährlich') {
      this.editedAusgabe.zahlungsmonate = [1, 7];
    } else if (newVal === 'monatlich') {
      this.editedAusgabe.zahlungsmonate = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    } else if (newVal === 'benutzerdefiniert') {
      // Bei benutzerdefiniert alle Checkboxen aktivieren/Monate lassen
    }
  },
  
  // Watcher für den jährlichen Zahlungsmonat
  'jahresZahlungsmonat': function(newVal) {
    if (this.neueAusgabe.zahlungsintervall === 'jährlich') {
      this.neueAusgabe.zahlungsmonate = [parseInt(newVal)];
    }
  },
  
  // Watcher für den jährlichen Zahlungsmonat im Bearbeitungsmodus
  'editJahresZahlungsmonat': function(newVal) {
    if (this.editedAusgabe.zahlungsintervall === 'jährlich') {
      this.editedAusgabe.zahlungsmonate = [parseInt(newVal)];
    }
  },
  
  // Watcher für den vierteljährlichen Startmonat
  'vierteljahrStartmonat': function(newVal) {
    if (this.neueAusgabe.zahlungsintervall === 'vierteljährlich') {
      this.setQuarterlyPaymentMonths(parseInt(newVal));
    }
  },
  
  // Watcher für den vierteljährlichen Startmonat im Bearbeitungsmodus
  'editVierteljahrStartmonat': function(newVal) {
    if (this.editedAusgabe.zahlungsintervall === 'vierteljährlich') {
      this.setEditQuarterlyPaymentMonths(parseInt(newVal));
    }
  }
 }
}
</script>