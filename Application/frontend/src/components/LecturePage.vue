<template>
  <div>
    <AppNavbar/>

    <div class="container-fluid">
      <div class="row">
        <!-- Sidebar -->
        <AppSidebar/>

        <!-- Main Content -->
        <div class="col-9 p-4">
          <div class="content-header d-flex align-items-center mb-4">
            <h4 class="mb-0">{{ lectureTitle }}</h4>
            <div class="ms-3">
              <span v-for="i in 5" :key="i" class="me-1" :style=" {
                      color: i <= 3 ? '#f0c929' : '#6c757d'
                    }">★</span>
              <span>(0 reviews)</span>
              <a href="#" class="ms-2">Submit a review</a>
            </div>
          </div>

          <!-- Video Section -->
          <div class="row">
            <div class="col-12">
              <div class="video-container mb-4">
                <iframe
                  width="100%"
                  height="500"
                  :src="`https://www.youtube.com/embed/${videoId}`"
                  frameborder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowfullscreen
                ></iframe>
              </div>

              <!-- Summarize Button and Summary Box -->
              <div class="summary-section">
                <!-- Summarize Button with AI Assistant Icon -->
                <button
                  @click="summarizeVideo"
                  class="ai-button summarize-btn"
                  :disabled="isLoading"
                >
                  <img :src="StudentIcon" class="ai-icon" alt="AI Summarizer">
                  <span>{{ isLoading ? 'Summarizing...' : 'Summarize' }}</span>
                </button>

                <!-- Summary Box (shows only after clicking summarize) -->
                <div v-if="summary" class="summary-box">
                  <div class="summary-header">
                    <h5>Video Summary</h5>
                    <div class="d-flex gap-2">
                      <button @click="copyToClipboard" class="btn btn-sm btn-outline-secondary">
                        <i class="bi bi-clipboard"></i> Copy
                      </button>
                      <button @click="summary = ''" class="btn-close"></button>
                    </div>
                  </div>
                  <div class="summary-content">
                    {{ summary }}
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
import axios from 'axios'

export default {
  name: 'VideoLecturePage',
  components: {
    AppNavbar,
    AppSidebar,
    ChatWindow
  },
  data() {
    return {
      summary: '',
      isLoading: false,
      StudentIcon,
    }
  },
  computed: {
    lectureTitle() {
      return this.$route.query.title;
    },
    videoId() {
      return this.$route.query.videoId;
    }
  },
  watch: {
    // Watch for changes in videoId or lectureTitle
    videoId() {
      this.resetSummary();
    },
    lectureTitle() {
      this.resetSummary();
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
        this.summary = 'Failed to generate summary. Please try again.'
      } finally {
        this.isLoading = false
      }
    },
    resetSummary() {
      // Reset summary and close modal when switching lectures
      this.summary = '';
      this.isLoading = false;
    },
    redirectToChatbot() {
      this.$router.push('/chatbot')
    },
    async copyToClipboard() {
      try {
        await navigator.clipboard.writeText(this.summary);
        // Optional: Add a toast or notification to show success
        alert('Summary copied to clipboard!');
      } catch (err) {
        console.error('Failed to copy text: ', err);
      }
    }
  }
}
</script>

<style scoped>
.video-container {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.summary-section {
  margin-top: 20px;
}

.summary-box {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 0;
  margin-top: 15px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.summary-header {
  background-color: #f1f3f5;
  padding: 15px 20px;
  border-bottom: 1px solid #dee2e6;
  border-radius: 8px 8px 0 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-header h5 {
  margin: 0;
  color: #495057;
}

.summary-content {
  padding: 20px;
  line-height: 1.6;
  color: #495057;
}

/* AI Button Styles */
.ai-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.summarize-btn {
  background: linear-gradient(135deg, #f5f5f7 0%, #e8e8ea 100%);
  border: 1px solid #e0e0e0; /* Adding a thin border */
  color: #606060;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.summarize-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
.ai-icon {
  font-size: 20px;
  display: flex;
  align-items: center;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .ask-me-btn {
    bottom: 20px;
    right: 20px;
    padding: 10px 20px;
    font-size: 14px;
  }
}
</style>
