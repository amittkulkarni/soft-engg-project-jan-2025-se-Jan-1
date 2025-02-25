<template>
  <div>
    <AppNavbar />
    <div class="dashboard-layout">
      <AppSidebar />

      <div class="main-content">
        <div class="content-wrapper">
          <div class="welcome-section text-center mb-4">
            <h1>
              <span><img :src="StudentIcon" height="40px" class="me-2" /></span> Hello, Amit!
            </h1>
            <p>I am KIA, your virtual companion at SEEK.</p>
            <p>You may click on one of the options below or use the button at the bottom to chat with me.</p>
          </div>

          <div class="cards-container d-flex justify-content-center gap-4 mb-5">
            <div class="card shadow-sm p-3" @click.stop="showContent('week-summary')">
              <i class="bi bi-calendar-week card-icon"></i>
              <h2>Generate Week Summary</h2>
              <p>Generate summarized notes for every week</p>
            </div>

            <div class="card shadow-sm p-3" @click.stop="showContent('generate-notes')">
              <i class="bi bi-journal-text card-icon"></i>
              <h2>Generate Topic Notes</h2>
              <p>Get topic-specific bullet-point notes</p>
            </div>
          </div>

          <!-- Generate Notes Section -->
          <div v-if="activeContent === 'generate-notes'" class="dynamic-content">
            <h2 class="d-flex justify-content-center mb-4">Generate Topic-Specific Notes</h2>
            <div class="input-group mb-3">
              <input
                type="text"
                v-model="searchQuery"
                @input="fetchSuggestions"
                placeholder="Search for a topic..."
                class="form-control"
              />
              <button class="btn btn-dark" @click="generateNotes" :disabled="!selectedTopic">Generate</button>
            </div>
            <ul v-if="suggestions.length > 0" class="list-group mb-3">
              <li
                v-for="(suggestion, index) in suggestions"
                :key="index"
                @click="selectSuggestion(suggestion)"
                class="list-group-item list-group-item-action"
              >
                {{ suggestion }}
              </li>
            </ul>
            <!-- Markdown Output for Notes -->
            <div v-if="generatedNotes" class="markdown-output bg-light p-3 rounded shadow-sm mt-4">
              <vue-markdown :source="generatedNotes" />
              <button @click="downloadPDF" class="btn btn-success mt-3">Download PDF</button>
            </div>
          </div>

          <!-- Week Summary Section -->
          <div v-if="activeContent === 'week-summary'" class="dynamic-content">
            <h2 class="d-flex justify-content-center">Select a Week to Generate Summary</h2>
            <div class="d-flex align-items-center justify-content-center gap-3 mb-3">
              <select v-model="selectedWeek" class="form-select w-auto">
                <option v-for="week in weeks" :key="'Week ' + week" :value="'Week ' + week">Week {{ week }}</option>
              </select>
              <button @click="generateWeekSummary" class="btn btn-dark">Generate Summary</button>
            </div>
          </div>

          <!-- Markdown Output -->
          <div v-if="generatedSummary" class="markdown-output bg-light p-3 rounded shadow-sm mt-4">
            <vue-markdown :source="generatedSummary" />
            <button @click="downloadPDF" class="btn btn-success mt-3">Download PDF</button>
          </div>
        </div>
        <ChatWindow />
      </div>
    </div>
  </div>
</template>

<script>
import AppNavbar from "@/components/AppNavbar.vue";
import AppSidebar from "@/components/AppSidebar.vue";
import ChatWindow from "@/components/ChatWindow.vue";
import StudentIcon from "@/assets/student.png";
import VueMarkdown from "vue-markdown-render";
import { jsPDF } from "jspdf";

export default {
  name: "KiaPage",
  data() {
    return {
      StudentIcon,
      activeContent: null,
      searchQuery: "",
      suggestions: [],
      generatedNotes: "",
      weeks: Array.from({ length: 12 }, (_, i) => i + 1),
      selectedWeek: "Week 1",
      selectedTopic: "",
      generatedSummary: "",
    };
  },
  components: {
    AppSidebar,
    AppNavbar,
    ChatWindow,
    VueMarkdown
  },
  methods: {
    showContent(content) {
      this.activeContent = content;
      this.generatedNotes = "";
      this.generatedSummary = "";
    },
    fetchSuggestions() {
      const topics = ["Regression", "Linear Regression", "Logistic Regression", "Auto-regressive model"];
      this.suggestions = topics.filter(topic =>
        topic.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    },
    selectSuggestion(suggestion) {
      this.selectedTopic = suggestion;
      this.searchQuery = suggestion;
      this.suggestions = [];
    },
    downloadPDF() {
      const doc = new jsPDF();
      const content = this.activeContent === "generate-notes" ? this.generatedNotes : this.generatedSummary;
      doc.text(content, 10, 10);
      const fileName = this.activeContent === "generate-notes"
        ? `Notes_${this.searchQuery || "Topic"}.pdf`
        : `Week_${this.selectedWeek.replace("Week ", "")}_Summary.pdf`;
      doc.save(fileName);
    },
    generateNotes() {
      this.generatedNotes = "";
      this.generatedNotes = `
## Alas certa receptus volentem

Lorem markdownum festa. Radiis collo imagine ille, **quibus sine Syrtis** certa
pectore; quod ultoresque cornum: fuga. Adfatur potuisset qualem **membra fugit
perspicit** undas.

    var property = boot_data.mountain.office(1, 1, baseband_css_cache(30, 1)) +
            cssArchiePhreaking;
    if (dsl_bare_sram.logSoapPeopleware(pcb, 1, cpc_clone_function) < mac + ppl
            - client) {
        ios += engine(ppmFormatFavicon + favicon, rom(teraflops_ripcording, 18,
                pageTrojanApache));
    }
    var import_repository_ipod = voipBrouterWaveform(recursionWysiwyg) /
            interactive * linkPasteMode + 3 + backupSubnetBurn;
    webTokenPrint(bugAbendCarrier, partyRte);
    installBurn -= samba_sms_cps;

## Si unius ignis formam undas memorantur clamore

Sua opprimere sagax, vias pavor, me alii, ad mihi. Non prece requirere nequiquam
manu satum mox me causa ingemuit! Ait utque et silvae selige, nisi quos qui: me?
Celas et deducit Heliadum flores tetendi festumque fidem generosaque sitvs
inveniesque velis.

1. Tacitus superbus utraque fecit cernentem cladibus neutra
2. Facinus hoc fratre duraeque turba
3. Forsitan nos corpora
4. Arma vixque

## Ipse quae agiturque commissa

Color se gerit deplorata meruisse ruris quo quam gaudere: deerat moderere
Silenum abire, mihi eundem secum diversas circumfusaeque. Siccis retro. Totusque
[non vultus](http://www.visa.net/tamen.html) credas ducunt, debueram quibus
proferre. Animum crescere in tollor at teneros siquis, gentis unum insuperabile
capiti.

Crudelis sit aut sunt Nile finiat nepotis paenitet vident Pallada vertunt
pectora dum nequeat audire capillis ostendit. Iactarique est namque, cum ait
Graias *Silenum locus*.

## Haec est Perseus voles locum constitit dicique

Labefactum aetas; et stella, reserabo solvit, sic exercet ultima orbes sola
dabimus falsaque. Lumina rupit sororum Danaeius, quin donec adlabimur ferax
[parte](http://www.que.net/), me sequar. Non horrent **Alcithoe** aestibus, quas
duri novena in undas capillo? Alias ille detrahis coniuge.

Et vidit, loca *fessa* isdem penetrabit; mittat pulsa suspectum iaculum dapes in
haec, dea Phoebe. Et inquit feror quam auctor exsiluere et ait. Post virgo
infecta Oebalide adest tria, ut potuisse puto levatae scelus sumit; ut. In non
tormenti tecti! Coniunx fugae taurus transfert nolet et vaga protinus, et, me
carmen poteras parvo, et tamen, Autonoeius.
`;
    },
    generateWeekSummary() {
      this.generatedSummary = "";
      this.generatedSummary = `
# Summary of ${this.selectedWeek}


Lorem ipsum dolor sit amet consectetur adipiscing elit, non porttitor nec dictum sodales posuere, natoque orci class habitant ultricies semper. In condimentum vel blandit ante dis phasellus nunc vivamus aptent tempor metus, eget nibh congue morbi eu neque nascetur gravida aenean interdum. Risus convallis hac suscipit per ligula donec laoreet curabitur lectus aptent tellus proin vel dignissim gravida habitasse tincidunt maecenas odio rutrum, non torquent neque porta ullamcorper magna faucibus velit taciti est etiam sapien consequat interdum eros quam nullam fusce bibendum.

Sodales leo morbi auctor rhoncus purus arcu torquent dis, natoque quis cursus tortor lacinia eget tellus primis fusce, vivamus porttitor lacus senectus integer curabitur tempus. Netus platea consequat eu posuere velit porttitor suspendisse at proin, bibendum nisi dapibus pellentesque quam luctus semper mi, donec in hendrerit primis nisl sed porta pharetra.

## Posuere felis non scelerisque scelerisque

- Potenti nam id ridiculus, quam mollis, convallis accumsan.

- Magnis morbi aliquet nisl nullam, ante faucibus eget.

- Ad hendrerit praesent rutrum fames, laoreet hac purus.

- Nulla nisl massa eu iaculis, enim ac a.

Auctor nascetur condimentum sollicitudin laoreet proin faucibus nostra imperdiet, nunc metus aptent hac varius arcu cum ullamcorper, eget magna placerat ligula curabitur vulputate odio.

Netus dignissim placerat cum leo non class iaculis facilisi, habitasse sapien rutrum habitant tristique pellentesque curabitur cubilia, at nullam donec tempus metus nibh tempor. Pulvinar condimentum sociis vivamus egestas erat luctus sodales, convallis ad litora urna porttitor dignissim, netus cursus justo cubilia proin hendrerit. Tortor nam interdum montes ultrices parturient sapien sociis gravida, commodo conubia sem consequat tincidunt auctor taciti at, dignissim curabitur luctus congue aenean neque donec. `;
    },
  }
};
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  height: 100vh;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  padding: 2rem;
  overflow-y: auto;
}

.cards-container {
  display: flex;
  gap: 2rem;
  justify-content: center;
}

.card {
  background-color: white;
  border-radius: 16px;
  box-shadow: rgba(0, 0, 0, 0.1) 0px 4px 6px;
  width: calc(50% - 1rem);
  max-width: 300px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}

.card-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.dynamic-content {
  max-width: 800px;
  margin: 0 auto;
}

.markdown-output {
  max-width: 800px;
  margin: 0 auto;
}
</style>
