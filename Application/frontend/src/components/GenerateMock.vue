<template>
  <div>
    <AppNavbar/>
    <div class="container-fluid dashboard-layout">
      <div class="row">
        <!-- Sidebar -->
        <AppSidebar/>

        <!-- Main Content -->
        <div class="col-9 p-0">
          <div class="content-wrapper">
            <!-- Page Header -->
            <div class="page-header mb-4">
              <h2 class="mb-3">Generate Practice Questions</h2>
              <p class="text-muted">Create practice questions on any topic to enhance your learning</p>
            </div>

            <!-- Search Section -->
            <div class="search-section mb-4">
              <div class="search-container position-relative">
                <div class="input-group">
                  <span class="input-group-text bg-white">
                    <i class="bi bi-search"></i>
                  </span>
                  <input
                    v-model="searchQuery"
                    @input="fetchSuggestions"
                    type="text"
                    placeholder="Search topics (e.g., Regression, Python Pandas)..."
                    class="form-control search-input"
                  />
                  <button
                    :disabled="!selectedTopic"
                    @click="generateQuestions"
                    class="btn btn-primary"
                  >
                    <i class="bi bi-magic me-2"></i> Generate Questions
                  </button>
                </div>

                <!-- Suggestions Dropdown -->
                <transition name="fade">
                  <ul v-if="suggestions.length" class="suggestions-list shadow-sm">
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
            </div>

            <!-- Loading State -->
            <div v-if="loading" class="text-center my-5">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-3">Generating questions on {{ selectedTopic }}...</p>
            </div>

            <!-- Questions Section -->
            <div v-if="questions.length && !loading" class="questions-section">
              <div class="section-header d-flex justify-content-between align-items-center mb-3">
                <div>
                <h4>Practice Questions: {{ selectedTopic }}</h4>
                <span class="badge bg-success">
                  Practice Quiz
                  </span>
                </div>
                <span class="badge bg-primary">{{ questions.length }} Questions</span>
              </div>

              <!-- Progress Bar -->
              <div class="progress mb-3" style="height: 10px;">
                <div
                  class="progress-bar"
                  role="progressbar"
                  :style="{width: progressPercentage + '%'}"
                  :aria-valuenow="answeredCount"
                  aria-valuemin="0"
                  :aria-valuemax="questions.length">
                </div>
              </div>
              <p class="text-muted small mb-4">
                {{ answeredCount }} of {{ questions.length }} questions answered
              </p>

              <!-- Questions List -->
              <div v-for="(question, index) in questions" :key="index" class="question-container mb-4 p-4 rounded">
                <div class="d-flex justify-content-between">
                  <div class="question-text mb-3">
                  <span><strong>{{ index + 1 }}. </strong><markdown-renderer :content="question.text"></markdown-renderer></span>
                  </div>
                  <span class="badge bg-secondary p-2" style="max-height: 25px">1 pt</span>
                </div>

                <div class="options-container">
                  <div
                    v-for="(option, optionIndex) in question.options"
                    :key="optionIndex"
                    class="form-check mb-2"
                  >
                    <input
                      type="radio"
                      :id="'question-' + index + '-option-' + optionIndex"
                      :name="'question-' + index"
                      class="form-check-input"
                      v-model="userAnswers[index]"
                      :value="option"
                      :disabled="showScore"
                    />
                    <label
                      :for="'question-' + index + '-option-' + optionIndex"
                      :class="[
                        'form-check-label',
                        showScore
                          ? option === question.correct_answer
                            ? 'text-success fw-bold'
                            : userAnswers[index] === option
                              ? 'text-danger'
                              : ''
                          : '',
                      ]"
                    >
                      {{ option }}
                    </label>
                  </div>
                </div>

                <!-- Correct Answer Display -->
                <p v-if="showScore && userAnswers[index] !== question.correct_answer" class="correct-answer-text mt-2">
                  <i class="bi bi-check-circle-fill text-success me-1"></i>
                  Correct Answer: <span class="text-success fw-bold">{{ question.correct_answer }}</span>
                </p>
              </div>

              <!-- Action Buttons -->
              <div class="d-flex gap-2 mb-4">
                <button
                  @click="checkScore"
                  class="btn btn-primary"
                  :disabled="!isAllAnswered || showScore">
                  Submit Answers
                </button>

                <button
                  v-if="showScore"
                  @click="downloadPDF"
                  class="btn btn-outline-secondary">
                  <i class="bi bi-download me-1"></i> Download Report
                </button>
              </div>

              <!-- Score Modal -->
              <div v-if="showScore" class="score-modal mt-4 p-4 rounded shadow-sm">
                <h4 class="mb-3">Your Score: {{ score }}/{{ questions.length }}</h4>
                <div class="progress mb-3" style="height: 20px;">
                  <div class="progress-bar" role="progressbar"
                       :style="{width: (score/questions.length*100) + '%'}"
                       :class="getScoreClass(score/questions.length)">
                    {{ Math.round(score/questions.length*100) }}%
                  </div>
                </div>

                <!-- AI Suggestions -->
                <div class="suggestions-container mt-4">
                  <h5 class="mb-3">Performance Assessment:</h5>
                  <p class="mb-3">Based on your answers, here are some personalized suggestions to improve your understanding:</p>

                  <!-- Topic-specific Suggestions -->
                  <div class="topic-card p-3 mb-3 rounded border">
                    <h6 class="mb-2">{{ selectedTopic }}</h6>
                    <ul class="mb-2">
                      <li v-for="(suggestion, index) in aiSuggestions" :key="'suggestion-' + index" class="mb-2">
                        {{ suggestion }}
                      </li>
                    </ul>
                    <div>
                      <p class="mb-1"><strong>Recommended Resources:</strong></p>
                      <ul>
                        <li>Interactive tutorial: Understanding {{ selectedTopic }} fundamentals</li>
                        <li>Practice exercises: Applied {{ selectedTopic }} problems</li>
                      </ul>
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
  </div>
</template>

<script>
import AppNavbar from "@/components/AppNavbar.vue";
import AppSidebar from "@/components/AppSidebar.vue";
import ChatWindow from "@/components/ChatWindow.vue";
import MarkdownRenderer from "@/components/MarkdownRenderer.vue";
import { jsPDF } from "jspdf";
import axios from "axios";
export default {
  name: "GenerateMock",
  components: {
    AppNavbar,
    AppSidebar,
    ChatWindow,
    MarkdownRenderer
  },
  data() {
    return {
      searchQuery: "",
      suggestions: [],
      selectedTopic: "",
      questions: [],
      userAnswers: [],
      score: 0,
      showScore: false,
      loading: false,
      aiSuggestions: [
        "Review data manipulation techniques in Pandas library",
        "Practice more with DataFrame operations and methods",
        "Strengthen your understanding of CSV file handling in Python",
      ]
    };
  },
  computed: {
    answeredCount() {
      return this.userAnswers.filter(answer => answer !== null).length;
    },
    progressPercentage() {
      return (this.answeredCount / this.questions.length) * 100 || 0;
    },
    isAllAnswered() {
      return this.answeredCount === this.questions.length && this.questions.length > 0;
    }
  },
  methods: {
    fetchSuggestions() {
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
      this.suggestions = topics.filter((topic) =>
        topic.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    },
    selectSuggestion(suggestion) {
      this.selectedTopic = suggestion;
      this.searchQuery = suggestion;
      this.suggestions = [];
    },
    generateQuestions() {
      this.loading = true;
      this.questions = [];
      this.userAnswers = [];
      this.showScore = false;

      // API call configuration
      const requestData = {
        topic: this.selectedTopic,
        num_questions: 5
      };

      // Make the API call using Axios
      axios.post('http://127.0.0.1:5000/generate_topic_specific_questions', requestData)
        .then(response => {
          // Axios automatically parses JSON and puts data in response.data
          const data = response.data;

          if (data.success) {
            // Transform API response to match your component's question format
            this.questions = data.questions.map(item => ({
              text: item.question,
              options: item.options,
              correct_answer: item.correct_answer,
            }));

            // Initialize user answers array
            this.userAnswers = Array(this.questions.length).fill(null);
          } else {
            // Handle API success=false response
            console.error("API Error:", data.message);
          }
        })
        .catch(error => {
          // Enhanced error handling with Axios
          if (error.response) {
            // The server responded with a status code outside of 2xx range
            console.error("Server error:", error.response.status, error.response.data);
          } else if (error.request) {
            // The request was made but no response was received
            console.error("Network error - no response received:", error.request);
          } else {
            // Something happened in setting up the request
            console.error("Error:", error.message);
          }
        })
        .finally(() => {
          this.loading = false;
        });
    },
    checkScore() {
      this.score = this.questions.reduce((total, question, index) => {
        return total + (this.userAnswers[index] === question.correct_answer ? 1 : 0);
      }, 0);
      this.showScore = true;
    },
    downloadPDF() {
      const doc = new jsPDF();

      // Add title and header
      doc.setFontSize(20);
      doc.setTextColor(108, 27, 27);
      doc.text(`${this.selectedTopic} - Practice Questions`, 20, 20);

      doc.setFontSize(14);
      doc.setTextColor(0, 0, 0);
      doc.text(`Score: ${this.score}/${this.questions.length} (${Math.round(this.score/this.questions.length*100)}%)`, 20, 30);

      // Add date
      const today = new Date();
      doc.setFontSize(12);
      doc.text(`Generated on: ${today.toLocaleDateString()}`, 20, 40);

      // Add performance assessment
      doc.setFontSize(16);
      doc.text("Performance Assessment:", 20, 55);

      // Add suggestions
      let yPosition = 65;
      this.aiSuggestions.forEach((suggestion, index) => {
        doc.setFontSize(12);
        doc.text(`${index + 1}. ${suggestion}`, 25, yPosition);
        yPosition += 10;
      });

      // Add questions and answers
      yPosition += 10;
      doc.setFontSize(16);
      doc.text("Questions and Answers:", 20, yPosition);
      yPosition += 10;

      this.questions.forEach((question, index) => {
        // Check if we need a new page
        if (yPosition > 270) {
          doc.addPage();
          yPosition = 20;
        }

        doc.setFontSize(12);
        doc.text(`${index + 1}. ${question.text}`, 20, yPosition);
        yPosition += 10;

        doc.text(`Your answer: ${this.userAnswers[index] || 'Not answered'}`, 25, yPosition);
        yPosition += 8;

        if (this.userAnswers[index] !== question.correct_answer) {
          doc.setTextColor(0, 150, 0);
          doc.text(`Correct answer: ${question.correct_answer}`, 25, yPosition);
          doc.setTextColor(0, 0, 0);
        } else {
          doc.text("✓ Correct", 25, yPosition);
        }

        yPosition += 15;
      });

      doc.save(`${this.selectedTopic}_Practice_Questions.pdf`);
    },
    getScoreClass(scorePercentage) {
      if (scorePercentage >= 0.9) return 'bg-success';
      if (scorePercentage >= 0.7) return 'bg-info';
      if (scorePercentage >= 0.5) return 'bg-warning';
      return 'bg-danger';
    }
  }
};
</script>

<style scoped>
/* Dashboard Layout */
.dashboard-layout {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.content-wrapper {
  padding: 2.5rem;
  max-width: 1200px;
  margin: 0 auto;
}
/* Centered header styling */
.page-header {
  max-width: 500px; /* Match this to your search container width */
  margin: 0 auto 2rem auto;
}

.page-header h2 {
  color: #6c1b1b;
  font-weight: 600;
}

.page-header p {
  max-width: 600px;
  margin: 0 auto;
}

/* Search Section */
.search-container {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
}

.search-input {
  border-radius: 8px;
  padding: 0.8rem 1rem;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.suggestions-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  z-index: 1000;
  max-height: 250px;
  overflow-y: auto;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
}

.suggestion-item {
  padding: 12px 15px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  transition: background 0.2s;
  list-style: none;
}

.suggestion-item:hover {
  background-color: #f8f9fa;
}

/* Questions Section */
.questions-section {
  max-width: 1200px;
  margin: 0 auto;
}

.question-container {
  background-color: white;
  border-left: 4px solid #6c1b1b;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.question-container:hover {
  box-shadow: 0 5px 15px rgba(0,0,0,0.08);
}

.question-text {
  font-size: 1.1rem;
}

.form-check {
  padding-left: 2.2rem;
  margin-bottom: 0.8rem;
}

.form-check-input {
  margin-top: 0.4rem;
}

.form-check-input:checked {
  background-color: #6c1b1b;
  border-color: #6c1b1b;
}

.text-success {
  color: #28a745 !important;
}

.text-danger {
  color: #dc3545 !important;
}

/* Score Modal */
.score-modal {
  background-color: white;
  border-left: 4px solid #28a745;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.score-modal h4 {
  color: #343a40;
}

/* Progress Bar */
.progress {
  background-color: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar {
  background-color: #6c1b1b;
  transition: width 0.5s ease;
}

.topic-card {
  background-color: #f8f9fa;
  border-color: #dee2e6;
  transition: all 0.2s;
}

.topic-card:hover {
  background-color: #f0f0f0;
}

/* Custom button style */
.btn-primary {
  background-color: #6c1b1b;
  border-color: #6c1b1b;
}

.btn-primary:hover, .btn-primary:focus {
  background-color: #5a1616;
  border-color: #5a1616;
}

.btn-outline-secondary {
  color: #6c1b1b;
  border-color: #6c1b1b;
}

.btn-outline-secondary:hover {
  background-color: #6c1b1b;
  color: white;
}

/* Animation */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Badge styles */
.badge {
  padding: 0.5em 0.8em;
  font-weight: 500;
}

.badge.bg-primary {
  background-color: #6c1b1b !important;
}

/* Responsive adjustments */
@media (max-width: 992px) {
  .content-wrapper {
    padding: 1.5rem;
  }

  .question-text {
    font-size: 1rem;
  }
}

@media (max-width: 768px) {
  .page-header h2 {
    font-size: 1.5rem;
  }

  .btn {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
}
</style>
