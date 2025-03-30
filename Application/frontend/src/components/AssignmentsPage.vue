<template>
  <div>
    <AppNavbar/>
    <div class="container-fluid">
      <div class="row">
        <!-- Sidebar -->
        <AppSidebar/>

        <!-- Main Content -->
        <div class="col-9 p-4">
          <!-- Loading State -->
          <div v-if="loading" class="text-center my-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p class="mt-2">Loading assignment...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="alert alert-danger">
            {{ error }}
          </div>

          <!-- Assignment Content -->
          <div v-else>
            <!-- Assignment Header -->
            <div class="assignment-header mb-4">
              <h3>{{ assignment.title }}</h3>
              <div class="assignment-meta d-flex flex-wrap gap-3 mt-2">
                <span class="badge" :class="getTypeClass(assignment.assignment_type)">
                  {{ formatType(assignment.assignment_type) }}
                </span>
                <span class="text-muted">
                  <i class="bi bi-calendar-event me-1"></i> Due: {{ formatDate(assignment.due_date) }}
                </span>
                <span class="text-muted">
                  <i class="bi bi-award me-1"></i> {{ assignment.total_points }} Points
                </span>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="progress mb-4" style=" height: 10px;">
              <div class="progress-bar" role="progressbar"
                   :style=" {width: progressPercentage + '%'}"
                   :aria-valuenow="answeredCount"
                   aria-valuemin="0"
                   :aria-valuemax="questions.length">
              </div>
            </div>
            <p class="text-muted small mb-4">
              {{ answeredCount }} of {{ questions.length }} questions answered
            </p>

            <!-- Questions Section -->
            <div v-for="(question, index) in questions" :key="question.id" class="question-container mb-4 p-4 rounded">
              <div class="d-flex justify-content-between">
                <p class="question-text mb-3"><strong>{{ index + 1 }}. {{ question.text }}</strong></p>
                <span class="badge bg-secondary" style=" height: 25px">{{ question.points }} pts</span>
              </div>

              <div class="options-container">
                <div
                  v-for="option in question.options"
                  :key="option.id"
                  class="form-check mb-2"
                >
                  <input
                    type="radio"
                    :id="'question-' + question.id + '-option-' + option.id"
                    :name="'question-' + question.id"
                    class="form-check-input"
                    v-model="userAnswers[index]"
                    :value="option.id"
                    :disabled="showScore"
                  />
                  <label
                    :for="'question-' + question.id + '-option-' + option.id"
                    :class="[
                      'form-check-label',
                      showScore
                      ? option.id === correctAnswers[index]
                      ? 'text-success fw-bold'
                      : userAnswers[index] === option.id
                      ? 'text-danger'
                      : ''
                      : '',
                    ]"
                  >
                    {{ option.text }}
                  </label>
                </div>
              </div>

              <!-- Correct Answer Display -->
              <p v-if="showScore && userAnswers[index] !== correctAnswers[index]" class="correct-answer-text mt-2">
                <i class="bi bi-check-circle-fill text-success me-1"></i>
                Correct Answer: <span class="text-success">{{ getCorrectAnswerText(index) }}</span>
              </p>
            </div>

            <!-- Action Buttons -->
            <div class="d-flex gap-2 mb-4">
              <button
                @click="checkScore"
                class="btn btn-primary"
                :disabled="!isAllAnswered || showScore">
                Submit Assignment
              </button>

              <button
                v-if="showScore"
                @click="downloadPDF"
                class="btn btn-primary"
                :disabled="downloadingReport">
                <span v-if="downloadingReport">
                  <i class="bi bi-hourglass-split me-1"></i> Generating...
                </span>
                <span v-else>
                  <i class="bi bi-download me-1"></i> Download Report
                </span>
              </button>
            </div>

            <!-- Score and Suggestions Section -->
            <div v-if="showScore" class="score-modal mt-4 p-4 rounded shadow-sm">
              <h4 class="mb-3">Your Score: {{ score }}/{{ totalPossiblePoints }}</h4>
              <div class="progress mb-3" style=" height: 20px;">
                <div class="progress-bar" role="progressbar"
                     :style=" {
                       width: (score / totalPossiblePoints * 100) + '%'
                     }"
                     :class="getScoreClass(score / totalPossiblePoints)">
                  {{ Math.round(score/totalPossiblePoints*100) }}%
                </div>
              </div>
              <!-- Suggestions Loading Indicator -->
              <div v-if="suggestionsLoading" class="text-center my-4">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Generating personalized suggestions...</span>
                </div>
                <p class="mt-2">Analyzing your performance and generating personalized suggestions...</p>
              </div>
              <!-- Enhanced Suggestions Section -->
              <div v-else class="suggestions-container mt-4">
                <h5 class="mb-3">Performance Assessment:</h5>
                <p class="mb-3">{{ overallAssessment }}</p>

                <!-- Topic-specific Suggestions -->
                <div v-if="topicSuggestions.length > 0" class="mb-4">
                  <h5 class="mb-3">Topics to Review:</h5>
                  <div v-for="(topic, index) in topicSuggestions" :key="'topic-' + index" class="topic-card p-3 mb-3 rounded border">
                    <h6 class="mb-2">{{ topic.topic }}</h6>
                    <ul class="mb-2">
                      <li v-for="(suggestion, i) in topic.suggestions" :key="'suggestion-' + i" class="mb-1">
                        {{ suggestion }}
                      </li>
                    </ul>
                    <div v-if="topic.resources && topic.resources.length > 0">
                      <p class="mb-1"><strong>Recommended Resources:</strong></p>
                      <ul>
                        <li v-for="(resource, r) in topic.resources" :key="'resource-' + r">
                          {{ resource }}
                        </li>
                      </ul>
                    </div>
                  </div>
                </div>

                <!-- General Tips -->
                <div v-if="generalTips.length > 0">
                  <h5 class="mb-2">General Learning Tips:</h5>
                  <ul class="general-tips-list">
                    <li v-for="(tip, index) in generalTips" :key="'tip-' + index" class="mb-2">
                      {{ tip }}
                    </li>
                  </ul>
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
import api from "@/services/api.js"
import AppSidebar from "@/components/AppSidebar.vue";
import AppNavbar from "@/components/AppNavbar.vue";
import ChatWindow from "@/components/ChatWindow.vue";

export default {
  name: "AssignmentsPage",
  components: {
    AppNavbar,
    AppSidebar,
    ChatWindow
  },
  data() {
    return {
      loading: true,
      error: null,
      assignment: {
        id: null,
        title: '',
        assignment_type: '',
        due_date: null,
        total_points: 0,
      },
      questions: [],
      userAnswers: [],
      correctAnswers: [],
      pointsPerQuestion: [],
      score: 0,
      showScore: false,
      suggestions: [],
      topicSuggestions: [],
      overallAssessment: '',
      generalTips: [],
      suggestionsLoading: false,
      downloadingReport: false
    };
  },
  computed: {
    answeredCount() {
      return this.userAnswers.filter(answer => answer !== null).length;
    },
    progressPercentage() {
      return (this.answeredCount / this.questions.length) * 100;
    },
    isAllAnswered() {
      return this.answeredCount === this.questions.length;
    },
    totalPossiblePoints() {
      return this.pointsPerQuestion.reduce((sum, points) => sum + points, 0);
    }
  },
  async created() {
    await this.fetchAssignmentData();
  },
  watch: {
    // Watch for changes in the route parameter
    '$route.params.id': function () {
      // Reset component state
      this.loading = true;
      this.error = null;
      this.assignment = {
        id: null,
        title: '',
        assignment_type: '',
        due_date: null,
        total_points: 0,
      };
      this.questions = [];
      this.userAnswers = [];
      this.correctAnswers = [];
      this.pointsPerQuestion = [];
      this.score = 0;
      this.showScore = false;

      // Fetch the new assignment data
      this.fetchAssignmentData();
    }
  },
  methods: {
    async fetchAssignmentData() {
      try {
        this.loading = true;
        // Get assignment ID from route params
        const assignmentId = this.$route.params.id;

        // Fetch assignment data from API
        const response = await api.get(`http://127.0.0.1:5000/assignments/${
assignmentId
}`);

        if (response.data.success) {
          const assignmentData = response.data.assignment;

          // Set basic assignment data
          this.assignment = {
            id: assignmentData.id,
            title: assignmentData.title,
            assignment_type: assignmentData.assignment_type,
            due_date: assignmentData.due_date,
            total_points: assignmentData.total_points,
          };

          // Transform questions data
          this.questions = assignmentData.questions.map(q => ({
            id: q.id,
            text: q.question_text,
            type: q.question_type,
            points: q.points,
            options: q.options.map(opt => ({
              id: opt.id,
              text: opt.option_text,
              isCorrect: opt.is_correct
            }))
          }));

          // Initialize answers array
          this.userAnswers = Array(this.questions.length).fill(null);

          // Extract correct answers and points
          this.correctAnswers = this.questions.map(q =>
            q.options.find(opt => opt.isCorrect)?.id || null
          );

          this.pointsPerQuestion = this.questions.map(q => q.points);

          // Generate default suggestions based on assignment type
          this.generateDefaultSuggestions();
        } else {
          this.error = response.data.message || 'Failed to load assignment';
        }
      } catch (error) {
        console.error('Error fetching assignment:', error);
        this.error = 'Error loading assignment. Please try again.';
      } finally {
        this.loading = false;
      }
    },

    checkScore() {
      let earnedScore = 0;
      let wrongQuestions = [];

      // Calculate score based on correct answers
      this.userAnswers.forEach((answer, index) => {
        if (answer === this.correctAnswers[index]) {
          earnedScore += this.pointsPerQuestion[index];
        } else {
          // Track topics of wrong answers for suggestions
          wrongQuestions.push(this.questions[index].text);
        }
      });

      this.score = earnedScore;
      this.showScore = true;

      // Generate personalized suggestions based on wrong questions
      this.generateSuggestions(wrongQuestions);
    },

    generateDefaultSuggestions() {
      // Default suggestions based on assignment type
      if (this.assignment.assignment_type === 'practice') {
        this.suggestions = [
          "Take your time to understand each concept thoroughly.",
          "Review related lecture materials before attempting again.",
          "Try practicing similar problems for better understanding."
        ];
      } else {
        this.suggestions = [
          "Focus on understanding core concepts rather than memorizing.",
          "Review lecture material for topics you struggled with.",
          "Practice with additional exercises in areas where you made mistakes."
        ];
      }
    },
    async generateSuggestions(wrongQuestions) {
      try {
        this.suggestionsLoading = true;

        // Call the topic recommendation API with the wrong_questions array
        const response = await api.post('/topic_recommendation', {
          wrong_questions: wrongQuestions
        });

        if (response.data.success) {
          // Store the detailed suggestion data
          const suggestionData = response.data.suggestions;
          this.overallAssessment = suggestionData.overall_assessment;
          this.topicSuggestions = suggestionData.topic_suggestions || [];
          this.generalTips = suggestionData.general_tips || [];

          // Also maintain the flat suggestions list for backward compatibility
          this.suggestions = [];

          // Add overall assessment as first suggestion
          if (this.overallAssessment) {
            this.suggestions.push(this.overallAssessment);
          }

          // Add specific topic suggestions
          if (this.topicSuggestions && this.topicSuggestions.length > 0) {
            this.topicSuggestions.forEach(topic => {
              if (topic.suggestions && topic.suggestions.length > 0) {
                this.suggestions.push(`Topic: ${
topic.topic
} - ${
topic.suggestions[0]
}`);
              }
            });
          }

          // Add general tips
          if (this.generalTips && this.generalTips.length > 0) {
            this.generalTips.forEach(tip => {
              this.suggestions.push(tip);
            });
          }
        } else {
          // Fallback to default suggestions if API fails
          this.generateDefaultSuggestions();
        }
      } catch (error) {
        console.error('Error fetching topic suggestions:', error);
        // Fallback to default suggestions
        this.generateDefaultSuggestions();
      } finally {
        this.suggestionsLoading = false;
      }
    },
    async downloadPDF() {
      this.downloadingReport = true;
      try {
        // Prepare data for API call
        const reportData = {
          score: this.score,
          total: this.totalPossiblePoints,
          suggestions: [
            // Format all suggestion types into a single array
            this.overallAssessment,
            ...this.topicSuggestions.flatMap(topic =>
              topic.suggestions.map(suggestion => `${topic.topic}: ${suggestion}`)
            ),
            ...this.generalTips
          ],
          questions: this.questions.map((question, index) => {
            const userAnswer = this.userAnswers[index];
            const correctAnswerId = this.correctAnswers[index];

            return {
              id: question.id,
              text: question.text,
              user_answer: question.options.find(opt => opt.id === userAnswer)?.text || 'Not answered',
              correct_answer: question.options.find(opt => opt.id === correctAnswerId)?.text || 'N/A',
              is_correct: userAnswer === correctAnswerId
            };
          })
        };

        // Call the API endpoint with proper response type for file download
        const response = await api.post('/download_report', reportData, {
          responseType: 'blob'
        });

        // Create a download link for the PDF
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `${this.assignment.title}_Report.pdf`);
        document.body.appendChild(link);
        link.click();

        // Clean up
        setTimeout(() => {
          window.URL.revokeObjectURL(url);
          document.body.removeChild(link);
        }, 100);
      } catch (error) {
        console.error('Error downloading report:', error);
        // Show error message to user
        alert('Failed to download report. Please try again later.');
      } finally {
        this.downloadingReport = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },

    formatType(type) {
      if (!type) return 'Assignment';
      return type.charAt(0).toUpperCase() + type.slice(1) + ' Assignment';
    },

    getTypeClass(type) {
      switch (type) {
        case 'graded': return 'bg-primary';
        case 'practice': return 'bg-success';
        case 'quiz': return 'bg-warning';
        default: return 'bg-secondary';
      }
    },

    getScoreClass(scorePercentage) {
      if (scorePercentage >= 0.9) return 'bg-success';
      if (scorePercentage >= 0.7) return 'bg-info';
      if (scorePercentage >= 0.5) return 'bg-warning';
      return 'bg-danger';
    },

    getCorrectAnswerText(index) {
      const correctId = this.correctAnswers[index];
      const question = this.questions[index];
      const correctOption = question.options.find(opt => opt.id === correctId);
      return correctOption ? correctOption.text : 'N/A';
    }
  },
};
</script>

<style scoped>
.assignment-header {
  border-bottom: 1px solid #eaeaea;
  padding-bottom: 15px;
}

.question-container {
  background-color: #f8f9fa;
  border-left: 4px solid #6c757d;
  transition: all 0.2s ease;
}

.question-container:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.question-text {
  font-size: 1.1rem;
}

.form-check {
  padding-left: 2rem;
}

.form-check-input:checked {
  background-color: #007bff;
  border-color: #007bff;
}

.score-modal {
  background-color: #f8f9fa;
  border-left: 4px solid #28a745;
}

.suggestions-list li {
  margin-bottom: 8px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .assignment-meta {
    flex-direction: column;
    gap: 10px;
  }
}

.topic-card {
  background-color: #f8f9fa;
  transition: all 0.2s;
}

.topic-card:hover {
  background-color: #f0f0f0;
}

.general-tips-list li {
  margin-bottom: 10px;
}
</style>
