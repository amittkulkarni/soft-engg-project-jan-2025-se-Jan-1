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
            <h1 class="welcome-heading">Hello, User!</h1>
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
                  placeholder="Search topics (e.g., Regression, Neural Networks)"
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

            <!-- Week Summary Generation Status -->
            <div v-if="isGenerating" class="generation-status text-center p-4 mt-4">
              <div class="spinner-grow text-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p>Generating comprehensive summary for <strong>{{ selectedWeek }}</strong>...</p>
            </div>
          </div>          
          </div>
          </transition>
          <!-- Error message (add this before the markdown-output-container) -->
          <div v-if="apiError" class="alert alert-danger mt-4">
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            {{ apiErrorMessage }}
          </div>
          <!-- Enhanced Markdown Output -->
          <div v-if="currentContent" class="markdown-output-container mt-4">
            <div class="markdown-header d-flex justify-content-between align-items-center">
              <h4>{{ activeContent === 'generate-notes' ? selectedTopic : selectedWeek }} Notes</h4>
              <div class="actions">
                <button @click="copyContent" class="btn btn-sm btn-light me-2">
                  <i class="bi bi-clipboard"></i> Copy
                </button>
                <button @click="downloadPDF" class="btn btn-sm btn-light">
                  <i class="bi bi-download"></i> Download PDF
                </button>
              </div>
            </div>
            <div class="markdown-content">
              <markdown-renderer :content="currentContent" />
            </div>
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
import MarkdownRenderer from "@/components/MarkdownRenderer.vue";
import api from "@/services/api.js"

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
      apiError: false,
      apiErrorMessage: ""
    };
  },
  components: {
    AppSidebar,
    AppNavbar,
    ChatWindow,
    MarkdownRenderer
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
    async fetchSuggestions() {
      // Clear suggestions if search query is empty
      if (!this.searchQuery || this.searchQuery.length < 2) {
        this.suggestions = [];
        return;
      }

      // You can replace this with a real API call to get topic suggestions
      // For now, we'll use a more comprehensive list of ML topics
      const topics = [
        "Regression", "Linear Regression", "Logistic Regression",
        "Decision Trees", "Random Forests", "Support Vector Machines",
        "Neural Networks", "Deep Learning", "Convolutional Neural Networks",
        "Recurrent Neural Networks", "Natural Language Processing",
        "K-Means Clustering", "Hierarchical Clustering", "DBSCAN",
        "Principal Component Analysis", "Feature Engineering",
        "Gradient Descent", "Backpropagation", "Overfitting", "Regularization",
        "Cross-Validation", "Precision and Recall", "ROC Curves", "AUC",
        "Naive Bayes", "Ensemble Methods", "Boosting", "Bagging",
        "Transfer Learning", "Reinforcement Learning"
      ];

      this.suggestions = topics.filter(topic =>
        topic.toLowerCase().includes(this.searchQuery.toLowerCase())
      ).slice(0, 5); // Limit to 5 suggestions
    },
    selectSuggestion(suggestion) {
      this.selectedTopic = suggestion;
      this.searchQuery = suggestion;
      this.suggestions = [];
    },
    copyContent() {
      navigator.clipboard.writeText(this.currentContent)
        .then(() => {
          // You could add a toast notification here
          alert('Content copied to clipboard!');
        })
        .catch(err => {
          console.error('Failed to copy content: ', err);
        });
    },
async downloadPDF() {
  try {
    this.isGenerating = true; // Show loading indicator

    // Prepare the request data
    const requestData = {
      content: this.currentContent, // Your markdown content
      title: this.activeContent === "generate-notes"
        ? this.selectedTopic
        : this.selectedWeek,
      filename: this.activeContent === "generate-notes"
        ? `Notes_${this.searchQuery || "Topic"}.pdf`
        : `Week_${this.selectedWeek.replace("Week ", "")}_Summary.pdf`
    };

    // Call the backend endpoint with responseType 'blob' to receive binary data
    const response = await api.post(
      '/download_markdown_pdf',
      requestData,
      { responseType: 'blob' }
    );

    // Create a blob URL from the PDF data
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);

    // Create a temporary link and trigger the download
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', requestData.filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up the blob URL
    window.URL.revokeObjectURL(url);

  } catch (error) {
    console.error('Error generating PDF:', error);
    this.apiError = true;
    this.apiErrorMessage = 'Failed to generate PDF. Please try again later.';
  } finally {
    this.isGenerating = false; // Hide loading indicator
  }
},
    async generateNotes() {
      // Only proceed if a topic is selected
      if (!this.selectedTopic) {
        return;
      }

      // Reset previous content and show loading state
      this.generatedNotes = "";
      this.isGenerating = true;

      try {
        // Call the backend API
        const response = await api.post('/generate_notes', {
          topic: this.selectedTopic
        });

        // Check if successful
        if (response.data.success) {
          // Store the notes content
          this.generatedNotes = response.data.notes;
        } else {
          // Handle API error
          this.generatedNotes = `## Error\n\nFailed to generate notes: ${response.data.message}`;
        }
      } catch (error) {
        console.error('Error generating notes:', error);
        this.apiError = true;
        this.apiErrorMessage = error.response?.data?.message || 'Failed to connect to the server';
        this.generatedNotes = "## Error\n\nUnable to generate notes at this time. Please try again later.";
      } finally {
        // Hide loading indicator when done (success or failure)
        this.isGenerating = false;
      }
    },
    async generateWeekSummary() {
      try {
        // Reset previous content and show loading state
        this.generatedSummary = "";
        this.isGenerating = true;
        this.apiError = false;

        // Extract week number from the selected week (e.g., "Week 1" -> 1)
        const weekNumber = parseInt(this.selectedWeek.replace("Week ", ""));

        // Call the backend API
        const response = await api.post('/generate_week_summary', {
          week_id: weekNumber
        });

        // Check if successful
        if (response.data.success) {
          // Store the summary content
          this.generatedSummary = response.data.summary;
        } else {
          // Handle API error
          this.apiError = true;
          this.apiErrorMessage = response.data.message || 'Failed to generate week summary';
          this.generatedSummary = `## Error\n\nFailed to generate summary: ${response.data.message}`;
        }
      } catch (error) {
        console.error('Error generating week summary:', error);
        this.apiError = true;
        this.apiErrorMessage = error.response?.data?.message || 'Failed to connect to the server';
        this.generatedSummary = "## Error\n\nUnable to generate week summary at this time. Please try again later.";
      } finally {
        // Hide loading indicator when done (success or failure)
        this.isGenerating = false;
      }
    }
  }
};
</script>

<style scoped>
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  padding: 2.5rem;
  max-width: 1200px;
  margin: 0 auto;
  overflow-y: auto;
  width: 100%;
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

.markdown-output-container {
  width: 100%; /* Makes it full width of parent */
  max-width: 1200px; /* Match this to your other divs' max-width */
  margin: 2rem auto;
  border: 1px solid #e2e2e2;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background-color: white;
  overflow: hidden;
}

/* Enhance code block styling */
.markdown-content pre {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
  margin: 1.2rem 0;
  width: 100%; /* Ensure code blocks take full width */
}

.markdown-header {
  background-color: #6c1b1b;
  color: white;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e2e2e2;
}

.markdown-content {
  padding: 1.5rem;
  font-size: 1.05rem;
  line-height: 1.7;
  color: #343a40;
  max-height: 600px;
  overflow-y: auto;
}

/* Typography enhancements */
.markdown-content h1 {
  font-size: 1.8rem;
  margin-top: 0;
  color: #6c1b1b;
  border-bottom: 2px solid #f0e5e5;
  padding-bottom: 0.5rem;
  margin-bottom: 1.2rem;
}

.markdown-content h2 {
  font-size: 1.5rem;
  color: #6c1b1b;
  margin-top: 1.5rem;
  border-bottom: 1px solid #f0e5e5;
  padding-bottom: 0.4rem;
  margin-bottom: 1rem;
}

.markdown-content h3 {
  font-size: 1.25rem;
  color: #333;
  margin-top: 1.2rem;
  margin-bottom: 0.8rem;
}

.markdown-content p {
  margin-bottom: 1rem;
}

.markdown-content ul,
.markdown-content ol {
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

.markdown-content li {
  margin-bottom: 0.5rem;
}

/* Code block formatting */
.markdown-content pre {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
  margin: 1.2rem 0;
  position: relative;
}

.markdown-content pre::before {
  content: 'Python';
  position: absolute;
  top: 0;
  right: 0;
  background: #e9ecef;
  padding: 2px 8px;
  font-size: 0.75rem;
  border-radius: 0 6px 0 6px;
  color: #495057;
}

.markdown-content code {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9rem;
  color: #212529;
  background-color: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
}

.markdown-content pre code {
  padding: 0;
  background-color: transparent;
  color: #212529;
  display: block;
  line-height: 1.5;
}

/* Inline elements */
.markdown-content strong {
  color: #495057;
  font-weight: 600;
}

.markdown-content a {
  color: #6c1b1b;
  text-decoration: none;
  border-bottom: 1px solid #6c1b1b33;
}

.markdown-content a:hover {
  text-decoration: none;
  border-bottom: 1px solid #6c1b1b;
}

/* Tables */
.markdown-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.markdown-content th {
  background-color: #f8f9fa;
  font-weight: 600;
  text-align: left;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
}

.markdown-content td {
  padding: 0.75rem;
  border: 1px solid #dee2e6;
}

.markdown-content tr:nth-child(even) {
  background-color: #f8f9fa;
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

.btn-light {
  background-color: #f8f9fa;
  color: #333;
  border: 1px solid #dee2e6;
}

.btn-light:hover {
  background-color: #e2e6ea;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
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

/* Add more spacing to headings */
.markdown-content h1, .markdown-content h2, .markdown-content h3 {
  margin-top: 1.8rem;
  margin-bottom: 1.2rem;
}

/* Fix table spacing */
.markdown-content table {
  margin: 1.5rem 0;
  border-collapse: separate;
  border-spacing: 0;
}

.markdown-content th, .markdown-content td {
  padding: 0.8rem 1rem;
  border: 1px solid #dee2e6;
}

/* Add space after lists */
.markdown-content ul, .markdown-content ol {
  margin-bottom: 1.2rem;
}

/* Add space between list items */
.markdown-content li {
  margin-bottom: 0.5rem;
}

.generation-status {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.week-item.active {
  background-color: #6c1b1b;
  color: white;
  border-color: #6c1b1b;
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
