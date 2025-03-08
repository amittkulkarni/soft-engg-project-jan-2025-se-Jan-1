<template>
  <div>
    <AppNavbar />
    <div class="dashboard-layout">
      <AppSidebar />

      <div class="main-content">
        <div class="content-wrapper">
          <div class="welcome-section text-center mb-4">
            <div class="avatar-container mb-3">
              <img :src="StudentIcon" class="avatar-img" alt="KIA Avatar" />
            </div>
            <h1 class="welcome-heading">Hello, Amit!</h1>
            <div class="subtitle-container">
              <p class="lead mb-1">I am KIA, your virtual companion at SEEK.</p>
              <p class="text-muted">Select an option below or chat with me anytime.</p>
            </div>
          </div>

          <div class="cards-container">
            <div class="feature-card" @click.stop="showContent('week-summary')" :class="{ active: activeContent === 'week-summary' }">
              <div class="card-icon-wrapper">
                <i class="bi bi-calendar-week"></i>
              </div>
              <div class="card-content">
                <h3>Weekly Summaries</h3>
                <p>Generate condensed notes for any course week</p>
              </div>
            </div>

            <div class="feature-card" @click.stop="showContent('generate-notes')" :class="{ active: activeContent === 'generate-notes' }">
              <div class="card-icon-wrapper">
                <i class="bi bi-journal-text"></i>
              </div>
              <div class="card-content">
                <h3>Topic Notes</h3>
                <p>Create focused notes on specific course topics</p>
              </div>
            </div>
          </div>
          <transition name="fade" mode="out-in">
          <div v-if="activeContent" class="dynamic-content-wrapper">
          <!-- Generate Notes Section -->
          <div v-if="activeContent === 'generate-notes'" class="dynamic-content">
            <div class="section-header mb-4">
              <h2>Generate Topic-Specific Notes</h2>
              <p class="text-muted">Search for any course topic to generate comprehensive notes</p>
            </div>

            <div class="search-container position-relative mb-4">
              <div class="input-group">
                <span class="input-group-text bg-white">
                  <i class="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  v-model="searchQuery"
                  @input="fetchSuggestions"
                  placeholder="Search topics (e.g., Regression, Machine Learning)"
                  class="form-control"
                />
                <button class="btn btn-dark" @click="generateNotes" :disabled="!selectedTopic">
                  <i class="bi bi-magic me-1"></i> Generate
                </button>
              </div>

              <transition name="fade">
                <ul v-if="suggestions.length > 0" class="suggestions-list shadow-sm">
                  <li
                    v-for="(suggestion, index) in suggestions"
                    :key="index"
                    @click="selectSuggestion(suggestion)"
                    class="suggestion-item"
                  >
                    <i class="bi bi-tag-fill me-2 text-muted"></i>
                    {{ suggestion }}
                  </li>
                </ul>
              </transition>
            </div>

            <!-- Notes Generation Status -->
            <div v-if="isGenerating" class="generation-status text-center p-4">
              <div class="spinner-grow text-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p>Generating comprehensive notes for <strong>{{ selectedTopic }}</strong>...</p>
            </div>
          </div>

          <!-- Week Summary Section with improved UI -->
          <div v-if="activeContent === 'week-summary'" class="dynamic-content">
            <div class="section-header mb-4">
              <h2>Weekly Learning Summaries</h2>
              <p class="text-muted">Generate comprehensive notes for any week of your course</p>
            </div>

            <div class="week-selector">
              <div class="weeks-grid">
                <div
                  v-for="week in weeks"
                  :key="'Week ' + week"
                  @click="selectWeek('Week ' + week)"
                  :class="['week-item', selectedWeek === 'Week ' + week ? 'active' : '']"
                >
                  {{ week }}
                </div>
              </div>

              <button @click="generateWeekSummary" class="btn btn-dark mt-3 w-100">
                <i class="bi bi-file-earmark-text me-1"></i>
                Generate {{ selectedWeek }} Summary
              </button>
            </div>
          </div>
          </div>
          </transition>

          <!-- Markdown Output -->
          <div v-if="currentContent" class="markdown-output bg-light p-3 rounded shadow-sm mt-4">
            <vue-markdown :source="currentContent" />
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
      isGenerating: false,
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
  computed: {
    currentContent() {
      if (this.activeContent === 'generate-notes') return this.generatedNotes;
      if (this.activeContent === 'week-summary') return this.generatedSummary;
      return '';
    }
  },
  methods: {
    selectWeek(week) {
      this.selectedWeek = week;
    },
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
    async generateNotes() {
      this.generatedNotes = "";
      this.isGenerating = true;
      setTimeout(() => {
        this.isGenerating = false;
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
      });
    },
    generateWeekSummary() {
      this.generatedSummary = "";
      this.isGenerating = true;
      setTimeout(() => {
            this.isGenerating = false;
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
      }, 1500);
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

.dynamic-content {
  max-width: 800px;
  margin: 0 auto;
}

.markdown-output {
  max-width: 800px;
  margin: 0 auto;
}

.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f8f9fa;
}

.dynamic-content-wrapper {
  width: 100%;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  margin-bottom: 30px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  padding: 2.5rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* Welcome Section */
.welcome-section {
  padding: 2rem;
  margin-bottom: 3rem;
  background: linear-gradient(to right, #6c1b1b11, #6c1b1b22);
  border-radius: 12px;
}

.avatar-container {
  display: inline-block;
  background-color: #6c1b1b;
  padding: 1.2rem;
  border-radius: 50%;
  box-shadow: 0 8px 20px rgba(108, 27, 27, 0.2);
}

.avatar-img {
  height: 50px;
  width: 50px;
}

.welcome-heading {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #6c1b1b;
}

.subtitle-container {
  max-width: 500px;
  margin: 0 auto;
}

/* Feature Cards */
.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.feature-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 8px rgba(0,0,0,0.05);
  border-left: 5px solid transparent;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.feature-card.active {
  border-left: 5px solid #6c1b1b;
  background-color: #fcf8f8;
}

.card-icon-wrapper {
  background-color: #f0e5e5;
  color: #6c1b1b;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.card-icon-wrapper i {
  font-size: 1.8rem;
}

.card-content h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
  color: #343a40;
}

.card-content p {
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0;
}

/* Content Panel */
.content-panel {
  background: white;
  border-radius: 12px;
  margin-bottom: 2rem;
  border-top: 4px solid #6c1b1b;
}

/* Form Elements */
.form-control, .form-select {
  border-radius: 8px;
  padding: 0.6rem 1rem;
  border: 1px solid #dee2e6;
  transition: all 0.2s;
}

.form-control:focus, .form-select:focus {
  border-color: #6c1b1b;
  box-shadow: 0 0 0 0.25rem rgba(108, 27, 27, 0.25);
}

.btn {
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-dark {
  background-color: #6c1b1b;
  border-color: #6c1b1b;
}

.btn-dark:hover {
  background-color: #5a1717;
  border-color: #5a1717;
}

.btn-success {
  background-color: #28a745;
  border-color: #28a745;
}

/* Markdown Output */
.markdown-output {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: inset 0 1px 3px rgba(0,0,0,0.1);
  margin-top: 1.5rem;
  position: relative;
}

.markdown-output h1,
.markdown-output h2 {
  color: #6c1b1b;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

/* Animations */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Add these missing styles for the week selector */
.week-selector {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.weeks-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

/* Make week items more visible with these enhancements */
.week-item {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}


/* Responsive Adjustments */
@media (max-width: 768px) {
  .content-wrapper {
    padding: 1.5rem;
  }

  .cards-container {
    grid-template-columns: 1fr;
  }

  .welcome-heading {
    font-size: 1.8rem;
  }
}
</style>
