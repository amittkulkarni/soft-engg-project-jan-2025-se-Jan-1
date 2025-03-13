<template>
  <div>
    <AppNavbar/>

    <div class="container-fluid">
      <div class="row">
        <!-- Sidebar -->
        <AppSidebar/>

        <!-- Main Content -->
        <div class="col-lg-9 col-md-12 p-0 lecture-content">
          <!-- Breadcrumb Navigation -->
          <div class="breadcrumb-container px-4 py-2">
            <nav aria-label="breadcrumb">
              <ol class="breadcrumb mb-0">
                <li class="breadcrumb-item"><router-link to="/course">MLP</router-link></li>
                <li class="breadcrumb-item active" aria-current="page">{{ getWeekNumber() }}</li>
              </ol>
            </nav>
          </div>

          <!-- Lecture Header -->
          <div class="lecture-header px-4 py-3">
            <div class="d-flex justify-content-between align-items-center">
              <h3 class="mb-0">{{ lectureTitle }}</h3>
            </div>
          </div>

          <!-- Video Section with Enhanced UI -->
          <div class="video-wrapper px-4 mb-4">
            <div class="video-container">
              <iframe
                width="100%"
                height="550"
                :src="`https://www.youtube.com/embed/${videoId}`"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen
              ></iframe>
            </div>

            <!-- Video Info Bar -->
            <div class="video-info-bar d-flex justify-content-between align-items-center mt-2">
              <div/>
              <div>
                <button class="btn btn-sm btn-link text-decoration-none" @click="toggleFullScreen">
                  <i class="bi bi-fullscreen"></i> Fullscreen
                </button>
              </div>
            </div>
          </div>

          <!-- Content Tabs -->
          <div class="content-tabs px-4 mb-4">
            <ul class="nav nav-tabs" id="lectureTabs" role="tablist">
              <li class="nav-item" role="presentation">
                <button class="nav-link active" id="summary-tab" data-bs-toggle="tab" data-bs-target="#summary"
                  type="button" role="tab" aria-controls="summary" aria-selected="true">
                  Summary
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button class="nav-link" id="notes-tab" data-bs-toggle="tab" data-bs-target="#notes"
                  type="button" role="tab" aria-controls="notes" aria-selected="false">
                  Notes
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button class="nav-link" id="resources-tab" data-bs-toggle="tab" data-bs-target="#resources"
                  type="button" role="tab" aria-controls="resources" aria-selected="false">
                  Resources
                </button>
              </li>
            </ul>

            <div class="tab-content p-3 border border-top-0 rounded-bottom" id="lectureTabContent">
              <!-- Summary Tab -->
              <div class="tab-pane fade show active" id="summary" role="tabpanel" aria-labelledby="summary-tab">
                <div class="d-flex justify-content-between align-items-center mb-3">
                  <h5 class="mb-0">Video Summary</h5>
                  <button
                    @click="summarizeVideo"
                    class="ai-button summarize-btn"
                    :disabled="isLoading"
                  >
                    <div class="d-flex align-items-center">
                      <img :src="StudentIcon" class="ai-icon me-2" alt="AI Summarizer">
                      <span>{{ isLoading ? 'Generating...' : 'Generate Summary' }}</span>
                    </div>
                    <div v-if="isLoading" class="spinner-border spinner-border-sm ms-2" role="status">
                      <span class="visually-hidden">Loading...</span>
                    </div>
                  </button>
                </div>

                <div v-if="summary" class="summary-content">
                  <div class="summary-actions mb-2 text-end">
                    <button @click="copyToClipboard" class="btn btn-sm btn-outline-primary me-2">
                      <i class="bi bi-clipboard"></i> Copy
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" @click="downloadSummary">
                      <i class="bi bi-download"></i> Download
                    </button>
                  </div>
                  <div class="summary-text p-3 bg-light rounded">
                    <vue-markdown
                      :source="summary"
                      :options="{
                        highlight: function (code, lang) {
                        // This will handle the syntax highlighting based on language
                        return require('highlight.js').highlightAuto(code, [lang]).value;
                        }
                      }"/>
                  </div>
                </div>

                <div v-else-if="!isLoading" class="empty-summary text-center p-5">
                  <div class="mb-3">
                    <i class="bi bi-file-earmark-text empty-icon"></i>
                  </div>
                  <h6>No Summary Generated Yet</h6>
                  <p class="text-muted">Click the "Generate Summary" button to create an AI-powered summary of this lecture.</p>
                </div>

                <div v-else class="loading-summary text-center p-5">
                  <div class="spinner-border text-primary mb-3" role="status">
                    <span class="visually-hidden">Loading...</span>
                  </div>
                  <p>Generating your summary. This may take a moment...</p>
                </div>
              </div>

              <!-- Notes Tab -->
              <div class="tab-pane fade" id="notes" role="tabpanel" aria-labelledby="notes-tab">
                <div class="notes-container">
                  <textarea
                    class="form-control notes-area"
                    rows="10"
                    placeholder="Type your notes here..."
                    v-model="userNotes"
                  ></textarea>
                  <div class="d-flex justify-content-start mt-2">
                    <button class="btn btn-primary btn-sm" @click="saveNotes">
                      <i class="bi bi-save"></i> Save Notes
                    </button>
                  </div>
                </div>
              </div>

              <!-- Resources Tab -->
              <div class="tab-pane fade" id="resources" role="tabpanel" aria-labelledby="resources-tab">
                <div class="resources-list">
                  <div class="resource-item p-3 mb-2 border rounded d-flex align-items-center">
                    <i class="bi bi-file-pdf resource-icon me-3"></i>
                    <div>
                      <h6 class="mb-1">Lecture Slides</h6>
                      <small class="text-muted">PDF â€¢ 2.4 MB</small>
                    </div>
                    <button class="btn btn-sm btn-outline-primary ms-auto">Download</button>
                  </div>

                  <div class="resource-item p-3 mb-2 border rounded d-flex align-items-center">
                    <i class="bi bi-link-45deg resource-icon me-3"></i>
                    <div>
                      <h6 class="mb-1">Additional Reading</h6>
                      <small class="text-muted">External Link</small>
                    </div>
                    <a href="#" class="btn btn-sm btn-outline-primary ms-auto">Open</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <ChatWindow/>
  </div>
</template>

<script>
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import StudentIcon from '@/assets/student.png'
import ChatWindow from "@/components/ChatWindow.vue";
import VueMarkdown from "vue-markdown-render";
import 'highlight.js/styles/github.css';
import axios from 'axios'

const cleanMarkdown = (markdown) => {
  // Step 1: Remove consecutive blank lines (more than one)
  markdown = markdown.replace(/\n\s*\n+/g, '\n');

  // Step 2: Trim leading and trailing whitespace
  markdown = markdown.trim();

  // Step 3: Remove blank lines after headers (e.g., # Header)
  markdown = markdown.replace(/(\n#+.*)\n+/g, '$1\n');

  // Step 4: Remove blank lines after list items (e.g., - Item or * Item)
  markdown = markdown.replace(/(\n[-*]\s.*)\n+/g, '$1\n');

  // Step 6: Remove blank lines after paragraphs or text blocks
  markdown = markdown.replace(/([^\n]+\n)\n+/g, '$1');

  return markdown;
};


export default {
  name: 'LecturePage',
  components: {
    AppNavbar,
    AppSidebar,
    ChatWindow,
    VueMarkdown
  },
  data() {
    return {
      summary: '',
      isLoading: false,
      StudentIcon,
      userNotes: ''
    }
  },
  computed: {
    lectureTitle() {
      return this.$route.query.title || 'Untitled Lecture';
    },
    videoId() {
      return this.$route.query.videoId || '';
    }
  },
  mounted() {
    // Load saved notes for this lecture if available
    this.loadNotes();
  },
  watch: {
    // Watch for changes in videoId or lectureTitle
    videoId() {
      this.resetSummary();
      this.loadNotes();
    },
    lectureTitle() {
      this.resetSummary();
      this.loadNotes();
    }
  },
  methods: {
    async summarizeVideo() {
      this.isLoading = true
      try {
        const response = await axios.post('/api/get-video-summary', {
          videoId: 'your-video-id'
        })
        this.summary = response.data.summary
      } catch (error) {
        console.error('Error fetching summary:', error)
        const unclean_summary = `# Scikit-learn Dataset Loading and Generation

This document summarizes the methods for loading and generating datasets within the scikit-learn (sklearn) library. Sklearn offers several ways to access data, catering to different data formats and needs.

## Dataset Loaders

Sklearn provides built-in loaders for several small, commonly used datasets. These are readily available and don't require external downloads. Key examples include:

* **Classification Datasets:**
    * \`load_iris\`: 150 samples, 3 features, 1 label (classification).
    * \`load_digits\`: 1797 samples, 64 features, 1 label (classification).
    * \`load_wine\`: 178 samples, 13 features, 1 label (classification).
    * \`load_breast_cancer\`: 569 samples, 30 features, 1 label (classification).

* **Regression Datasets:**
    * \`load_diabetes\`: 442 samples, 10 features, 1 label (regression).
    * \`load_linnerud\`: 20 samples, 3 features, 3 labels (multi-output regression).

* **Larger Datasets (Fetchers):** Sklearn also offers fetchers for larger datasets, often requiring downloads. These include:
    * \`fetch_olivetti_faces\`: 400 samples, 4096 features, 40 labels (multi-class image classification).
    * \`fetch_20newsgroups\`: 18846 samples, 1 feature, 20 labels (multi-class text classification).
    * \`fetch_lfw_people\`: ~13233 samples, 5828 features, ~5749 labels (multi-class image classification).
    * \`fetch_covtype\`: 581012 samples, 54 features, 7 labels (multi-class classification).
    * \`fetch_rcv1\`: 804414 samples, 47236 features, 103 labels (multi-class classification).
    * \`fetch_kddcup99\`: ~4800000 samples, 41 features, 1 label (multi-class classification).
    * \`fetch_california_housing\`: 20640 samples, 8 features, 1 label (regression).

## Dataset Generators

For situations where existing datasets are insufficient, sklearn provides generators to create synthetic datasets with specific properties. This is useful for controlled experiments or when needing datasets with particular statistical characteristics.

* **Regression:** \`make_regression()\` generates regression datasets. It creates targets as a sparse linear combination of features, adding noise. Users can control the number of informative features and their correlation.

* **Classification:**
    * \`make_blobs()\`: Generates clusters of normally distributed data points, suitable for single-label classification. Each cluster is then assigned to a class.
    * \`make_classification()\`: Creates multi-class datasets by generating normally distributed clusters and assigning them to classes.
    * \`make_multilabel_classification()\`: Generates multi-label datasets where each sample can have multiple labels. It employs a specific generative process with rejection sampling to avoid samples with zero labels.

* **Clustering:** \`make_blobs()\` is also used for generating datasets for clustering tasks, creating normally distributed clusters with specified means and standard deviations.

## Loading External Datasets

Sklearn supports loading data from various external sources:

1. **\`fetch_openml()\`:** Retrieves datasets from the openml.org repository.

2. **\`pandas.io\`:** Reads data from common formats like CSV, Excel, JSON, and SQL databases.

3. **\`scipy.io\`:** Handles binary formats frequently used in scientific computing (e.g., \`.mat\`, \`.arff\`).

4. **\`numpy.routines.io\`:** Loads columnar data directly into NumPy arrays.

5. **\`dataset.load_files()\`:** Loads text data from directories where the directory name represents the label, and each file is a sample (useful for text classification).

6. **HDF5:** For managing large numerical datasets, sklearn recommends using the HDF5 format (Hierarchical Data Format version 5) due to its efficiency. Libraries like \`pandas\`, \`PyTables\`, and \`h5py\` provide interfaces for working with HDF5 files. These formatted datasets load much faster than other formats.

The choice of method depends on the data's format, size, and the specific machine learning task. The functions generally follow a naming convention: loaders start with \`load_\`, fetchers with \`fetch_\`, and generators with \`make_\`.`
        this.summary = cleanMarkdown(unclean_summary)
      } finally {
        this.isLoading = false
      }
    },
    resetSummary() {
      // Reset summary and close modal when switching lectures
      this.summary = '';
      this.isLoading = false;
    },
    async copyToClipboard() {
      try {
        await navigator.clipboard.writeText(this.summary);
        // You can add a toast notification here
        alert('Summary copied to clipboard!');
      } catch (err) {
        console.error('Failed to copy text: ', err);
      }
    },
    downloadSummary() {
      // Create a blob from the summary text
      const blob = new Blob([this.summary], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);

      // Create a temporary link and trigger download
      const a = document.createElement('a');
      a.href = url;
      a.download = `${this.lectureTitle.replace(/\s+/g, '_')}_Summary.txt`;
      document.body.appendChild(a);
      a.click();

      // Clean up
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    },
    saveNotes() {
      // Save notes to localStorage
      localStorage.setItem(`lecture_notes_${this.videoId}`, this.userNotes);
      alert('Notes saved successfully!');
    },
    loadNotes() {
      // Load notes from localStorage
      const savedNotes = localStorage.getItem(`lecture_notes_${this.videoId}`);
      this.userNotes = savedNotes || '';
    },
    getWeekNumber() {
      // Extract week number from lecture title if available
      const match = this.lectureTitle.match(/^(\d+)(?=\.)/);
      return match ? `Week ${match[1]}` : 'Current Week';
    },
    toggleFullScreen() {
      const iframe = document.querySelector('iframe');
      if (iframe) {
        // This is a simplified approach - might not work in all browsers
        if (iframe.requestFullscreen) {
          iframe.requestFullscreen();
        } else if (iframe.webkitRequestFullscreen) {
          iframe.webkitRequestFullscreen();
        } else if (iframe.msRequestFullscreen) {
          iframe.msRequestFullscreen();
        }
      }
    }
  }
}
</script>

<style scoped>
/* Base Styles */
.lecture-content {
  background-color: white;
  min-height: calc(100vh - 56px);
  display: flex;
  flex-direction: column;
}

.breadcrumb-container {
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.lecture-header {
  border-bottom: 1px solid #e9ecef;
}

/* Video Styles */
.video-wrapper {
  position: relative;
}

.video-container {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background-color: #000;
}

.video-container:hover{
  opacity: 1;
}


.video-info-bar {
  color: #6c757d;
}

/* Summary Button & Content */
.ai-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 50px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.summarize-btn {
  background: linear-gradient(135deg, #6c1b1b 0%, #8a3030 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(108, 27, 27, 0.2);
}

.summarize-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(108, 27, 27, 0.3);
}

.summarize-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.ai-icon {
  width: 24px;
  height: 24px;
}

.summary-content {
  animation: fadeIn 0.5s ease;
}

.summary-text {
  line-height: 1.2;
  white-space: pre-line;
}

.empty-icon {
  font-size: 48px;
  color: #ced4da;
}

/* Notes Tab */
.notes-area {
  resize: vertical;
  min-height: 200px;
  border: 1px solid #ced4da;
  padding: 15px;
  font-family: inherit;
  transition: border-color 0.2s ease;
}

.notes-area:focus {
  border-color: #6c1b1b;
  box-shadow: 0 0 0 0.25rem rgba(108, 27, 27, 0.25);
}

/* Resources Styles */
.resource-icon {
  font-size: 24px;
  color: #6c1b1b;
}

.resource-item {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.resource-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Responsive adjustments */
@media (max-width: 992px) {
  .lecture-content {
    padding: 0 15px;
  }

  .video-container iframe {
    height: 400px;
  }
}

@media (max-width: 768px) {
  .lecture-actions {
    display: none;
  }

  .video-container iframe {
    height: 300px;
  }

}

@media (max-width: 576px) {
  .video-container iframe {
    height: 240px;
  }
}
</style>
