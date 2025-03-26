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
                    <markdown-renderer :content="summary"/>
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
                      <small class="text-muted">PDF 2.4 MB</small>
                    </div>
                    <a href='https://drive.google.com/drive/folders/1KHTCerz-AiCm6criGXI8_hfU4tmgPwf5' class="btn btn-sm btn-outline-primary ms-auto">Download</a>
                  </div>

                  <div class="resource-item p-3 mb-2 border rounded d-flex align-items-center">
                    <i class="bi bi-link-45deg resource-icon me-3"></i>
                    <div>
                      <h6 class="mb-1">Additional Reading</h6>
                      <p class="text-muted">External Link</p>
                    </div>
                    <a href="https://drive.google.com/drive/folders/1wjY0KFuMDG2XwLUySf0R5uvxMaDzaa0v?usp=sharing" class="btn btn-sm btn-outline-primary ms-auto">Open</a>
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
import MarkdownRenderer from "@/components/MarkdownRenderer.vue";
import api from "@/services/api.js"


export default {
  name: 'LecturePage',
  components: {
    AppNavbar,
    AppSidebar,
    ChatWindow,
    MarkdownRenderer
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
    summarizeVideo() {
      this.isLoading = true;
      const weekId = this.getWeekId();

      if (weekId) {
        this.summarizeLecture(weekId);
      } else {
        this.isLoading = false;
        console.error('Could not extract lecture ID from title');
        this.error = 'Could not determine lecture ID from title format';
      }
    },
    async summarizeLecture(weekId) {
      // Set loading state
      this.summary = '';
      this.error = '';

      try {
        // Make API request
        const response = await api.post('/video_summarizer', {
          week_id: weekId
        });

        // Process successful response
        if (response.data.success) {
          // Store the summary in component data
          this.summary = response.data.summary;

          // Optional: Store metadata if needed
          this.currentWeek = response.data.week;
          this.currentLecture = response.data.lecture;

          // Optional: Show success message
          this.statusMessage = 'Summary generated successfully!';
        } else {
          // Handle API success=false case
          this.error = response.data.message || 'Failed to generate summary';
          console.error('Summary generation failed:', response.data.message);
        }
      } catch (error) {
        // Detailed error handling
        if (error.response) {
          // Server returned error status
          this.error = `Server error: ${error.response.data.message || error.response.status}`;
          console.error('Server error:', error.response.data);
        } else if (error.request) {
          // No response received
          this.error = 'Network error: Could not connect to the server';
          console.error('Network error:', error.request);
        } else {
          // Request setup error
          this.error = `Error: ${error.message}`;
          console.error('Error:', error.message);
        }
      } finally {
        // Clear loading state
        this.isLoading = false;
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
    getWeekId() {
      // Extract week number from lecture title if available
      const match = this.lectureTitle.match(/^(\d+)(?=\.)/);
      return match[1];
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
