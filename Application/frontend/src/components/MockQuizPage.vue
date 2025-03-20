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
            <p class="mt-2">Initializing mock quiz generator...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="alert alert-danger">
            {{ error }}
          </div>

          <!-- Mock Quiz Generator (when no quiz is generated yet) -->
          <div v-else-if="!mockQuizGenerated" class="mock-quiz-container mb-4 p-4 rounded shadow-sm">
            <h2 class="mb-4 text-center">Generate Mock Quizzes</h2>
            <p class="text-center text-muted mb-4">Select one of the quiz types below to challenge yourself</p>

            <!-- Enhanced Quiz Buttons -->
            <div class="quiz-buttons-container">
              <button
                @click="generateMockQuiz('quiz1')"
                class="quiz-button quiz1-button">
                <div class="icon-container">
                  <i class="bi bi-lightning-charge"></i>
                </div>
                <div class="button-content">
                  <h4>Mock Quiz 1</h4>
                  <p>Covers weeks 1-4</p>
                </div>
              </button>

              <button
                @click="generateMockQuiz('quiz2')"
                class="quiz-button quiz2-button">
                <div class="icon-container">
                  <i class="bi bi-lightning-charge-fill"></i>
                </div>
                <div class="button-content">
                  <h4>Mock Quiz 2</h4>
                  <p>Covers weeks 1-8</p>
                </div>
              </button>

              <button
                @click="generateMockQuiz('endterm')"
                class="quiz-button endterm-button">
                <div class="icon-container">
                  <i class="bi bi-stars"></i>
                </div>
                <div class="button-content">
                  <h4>End Term</h4>
                  <p>Covers entire course</p>
                </div>
              </button>
            </div>

            <div v-if="generatingMock" class="text-center mt-4">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2">Generating {{ mockType }} questions...</p>
            </div>
          </div>

          <!-- Mock Quiz Content (after generation) -->
          <div v-else>
            <!-- Quiz Header -->
            <div class="assignment-header mb-4">
              <div class="d-flex justify-content-between align-items-center">
                <h3>{{ mockQuiz.title }}</h3>
                <span class="badge bg-info">Practice Material</span>
              </div>
              <div class="assignment-meta d-flex flex-wrap gap-3 mt-2">
                <span class="badge bg-success">Practice Quiz</span>
                <span class="text-muted">
                  <i class="bi bi-award me-1"></i> {{ mockQuiz.total_points }} Points
                </span>
              </div>
            </div>

            <!-- Progress Bar -->
            <div class="progress mb-4" style="height: 10px;">
              <div class="progress-bar" role="progressbar"
                   :style="{width: progressPercentage + '%'}"
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
                <div class="question-text mb-3">
                  <strong>{{ index + 1 }}. </strong>
                  <markdown-renderer :content="question.text"></markdown-renderer>
                </div>
                <span class="badge bg-secondary p-2" style="height: 25px">{{ question.points }} pts</span>
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
                Submit Quiz
              </button>

              <button
                v-if="showScore"
                @click="downloadPDF"
                class="btn btn-outline-secondary">
                <i class="bi bi-download me-1"></i> Download Report
              </button>

              <button
                @click="resetQuiz"
                class="btn btn-outline-danger">
                <i class="bi bi-arrow-counterclockwise me-1"></i> Generate New Quiz
              </button>
            </div>

            <!-- Score and Suggestions Section -->
            <div v-if="showScore" class="score-modal mt-4 p-4 rounded shadow-sm">
              <h4 class="mb-3">Your Score: {{ score }}/{{ totalPossiblePoints }}</h4>
              <div class="progress mb-3" style="height: 20px;">
                <div class="progress-bar" role="progressbar"
                     :style="{width: (score/totalPossiblePoints*100) + '%'}"
                     :class="getScoreClass(score/totalPossiblePoints)">
                  {{ Math.round(score/totalPossiblePoints*100) }}%
                </div>
              </div>

              <h5 class="mt-4 mb-2">Suggestions to Improve:</h5>
              <ul class="suggestions-list">
                <li v-for="(suggestion, index) in suggestions" :key="'suggestion-' + index">
                  {{ suggestion }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      <ChatWindow/>
    </div>
  </div>
</template>

<script>
import AppSidebar from "@/components/AppSidebar.vue";
import AppNavbar from "@/components/AppNavbar.vue";
import ChatWindow from "@/components/ChatWindow.vue";
import MarkdownRenderer from "@/components/MarkdownRenderer.vue";
import { jsPDF } from "jspdf";
import axios from 'axios';

export default {
  name: "MockQuizPage",
  components: {
    AppNavbar,
    AppSidebar,
    ChatWindow,
    MarkdownRenderer
  },
  data() {
    return {
      loading: false,
      error: null,
      mockQuizGenerated: false,
      generatingMock: false,
      mockType: null,
      mockQuiz: {
        id: null,
        title: '',
        total_points: 0,
      },
      questions: [],
      userAnswers: [],
      correctAnswers: [],
      pointsPerQuestion: [],
      score: 0,
      showScore: false,
      suggestions: [],
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
      return this.answeredCount === this.questions.length && this.questions.length > 0;
    },
    totalPossiblePoints() {
      return this.pointsPerQuestion.reduce((sum, points) => sum + points, 0);
    }
  },
  created() {
    // Nothing to load at initialization since we're using placeholders
    this.loading = false;
  },
  methods: {
    async generateMockQuiz(quizType) {
      try {
        this.generatingMock = true;
        this.mockType = this.formatMockType(quizType);
        this.error = null;

        // Call the API endpoint
        const response = await axios.post('http://127.0.0.1:5000/generate_mock', {
          quiz_type: quizType,
          num_questions: 10 // Fixed number of questions
        });

        // Process the response
        if (response.data.success) {
          // Set mock quiz data
          this.mockQuiz = {
            id: 'mock-' + Date.now(),
            title: this.formatMockType(quizType),
            total_points: response.data.questions.length * 5, // 5 points per question
          };

          // Transform questions data with A, B, C, D option format
          this.questions = response.data.questions.map((q, index) => ({
            id: index,
            text: q.question,
            type: 'multiple_choice',
            points: 5,
            options: Object.entries(q.options).map(([key, optText]) => ({
              id: `opt-${index}-${key}`,
              text: `${key}. ${optText}`, // Include the option letter (A, B, C, D) in the display text
              isCorrect: key === q.answer // Compare the key (A, B, C, D) with the answer
            }))
          }));

          // Initialize answers and extract correct answers
          this.userAnswers = Array(this.questions.length).fill(null);
          this.correctAnswers = this.questions.map(q =>
            q.options.find(opt => opt.isCorrect)?.id || null
          );
          this.pointsPerQuestion = this.questions.map(q => q.points);

          // Reset other state
          this.showScore = false;
          this.score = 0;
          this.mockQuizGenerated = true;
          this.generateDefaultSuggestions();
        } else {
          this.error = response.data.message || 'Failed to generate mock quiz';
        }
      } catch (error) {
        console.error('Error generating mock quiz:', error);
        if (error.response) {
          this.error = `Server error: ${error.response.status} - ${error.response.data.message || 'Unknown error'}`;
        } else if (error.request) {
          this.error = 'Could not connect to the server. Please check if the backend is running.';
        } else {
          this.error = `Error: ${error.message}`;
        }
      } finally {
        this.generatingMock = false;
      }
    },
    resetQuiz() {
      this.mockQuizGenerated = false;
      this.questions = [];
      this.userAnswers = [];
      this.correctAnswers = [];
      this.pointsPerQuestion = [];
      this.score = 0;
      this.showScore = false;
      this.error = null;
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

      // Generate personalized suggestions based on wrong answers
      this.generateSuggestions(wrongQuestions);
    },
    generateDefaultSuggestions() {
      // Default suggestions for mock quizzes
      this.suggestions = [
        "Take your time to understand each concept thoroughly.",
        "Review related lecture materials before attempting again.",
        "Try practicing similar problems for better understanding.",
        "Focus on understanding the reasoning behind each correct answer."
      ];
    },

    generateSuggestions(wrongQuestions) {
      // Generate more specific suggestions based on wrong answers
      const specificSuggestions = [];

      if (wrongQuestions.length > 0) {
        specificSuggestions.push(`Review concepts related to: ${wrongQuestions.slice(0, 2).join(', ')}${wrongQuestions.length > 2 ? ', and others.' : '.'}`);
      }

      if (this.score / this.totalPossiblePoints < 0.7) {
        specificSuggestions.push("Consider revisiting the course materials before proceeding to more advanced topics.");
      }

      if (specificSuggestions.length > 0) {
        this.suggestions = [...specificSuggestions, ...this.suggestions.slice(0, 2)];
      }
    },

    downloadPDF() {
      const doc = new jsPDF();

      // Add title and basic info
      doc.setFontSize(16);
      doc.text(this.mockQuiz.title, 20, 20);

      doc.setFontSize(12);
      doc.text(`Generated on: ${this.getCurrentDate()}`, 20, 38);

      // Add score
      doc.setFontSize(14);
      doc.text(`Your Score: ${this.score}/${this.totalPossiblePoints} (${Math.round(this.score/this.totalPossiblePoints*100)}%)`, 20, 50);

      // Add suggestions
      doc.setFontSize(14);
      doc.text("Suggestions to Improve:", 20, 65);

      let yPosition = 75;
      this.suggestions.forEach(suggestion => {
        doc.setFontSize(12);
        doc.text(`• ${suggestion}`, 25, yPosition);
        yPosition += 10;
      });

      // Add question details
      yPosition += 10;
      doc.setFontSize(14);
      doc.text("Question Details:", 20, yPosition);
      yPosition += 10;

      this.questions.forEach((question, index) => {
        // Check if we need a new page
        if (yPosition > 270) {
          doc.addPage();
          yPosition = 20;
        }

        doc.setFontSize(12);
        // Truncate long questions to fit on PDF
        const questionText = question.text.length > 65
          ? question.text.substring(0, 65) + '...'
          : question.text;
        doc.text(`${index + 1}. ${questionText}`, 25, yPosition);
        yPosition += 8;

        const correctOption = question.options.find(opt => opt.id === this.correctAnswers[index]);
        const userOption = question.options.find(opt => opt.id === this.userAnswers[index]);

        const isCorrect = this.userAnswers[index] === this.correctAnswers[index];
        doc.text(`Your answer: ${userOption ? userOption.text : 'None'} ${isCorrect ? '✓' : '✗'}`, 30, yPosition);
        yPosition += 8;

        if (!isCorrect) {
          doc.text(`Correct answer: ${correctOption ? correctOption.text : 'N/A'}`, 30, yPosition);
          yPosition += 8;
        }

        yPosition += 5;
      });

      doc.save(`${this.mockQuiz.title}_Report.pdf`);
    },

    getCurrentDate() {
      const now = new Date();
      return now.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },

    formatMockType(type) {
      switch(type) {
        case 'quiz1': return 'Mock Quiz 1';
        case 'quiz2': return 'Mock Quiz 2';
        case 'endterm': return 'End Term Practice';
        default: return 'Practice Quiz';
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

.mock-quiz-container {
  background-color: #f0f8ff;
  border-left: 4px solid #0d6efd;
}
.quiz-buttons-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.quiz-button {
  display: flex;
  align-items: center;
  padding: 20px;
  min-height: 120px;
  border: none;
  border-radius: 12px;
  transition: all 0.3s ease;
  text-align: left;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.quiz-button:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
}

.icon-container {
  font-size: 2.5rem;
  margin-right: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.2);
}

.button-content {
  flex: 1;
}

.button-content h4 {
  margin: 0;
  font-weight: 600;
}

.button-content p {
  margin: 5px 0 0;
  opacity: 0.8;
}

.quiz1-button {
  background: linear-gradient(135deg, #42b883, #347474);
  color: white;
}

.quiz2-button {
  background: linear-gradient(135deg, #4a69bd, #1e3799);
  color: white;
}

.endterm-button {
  background: linear-gradient(135deg, #eb4d4b, #b71540);
  color: white;
}

.mock-quiz-container {
  background-color: #f8f9fa;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  border-left: none;
  padding: 30px !important;
}

/* Enhanced question styling */
.question-container {
  background-color: white;
  border-left: 4px solid #42b883;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.2s ease;
  border-radius: 8px;
}

.question-container:hover {
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

/* Better score display */
.score-modal {
  background-color: white;
  border-left: 4px solid #28a745;
  border-radius: 8px;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.1);
}
.code-block {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  margin: 1rem 0;
  overflow-x: auto;
}

.python.hljs {
  color: #24292e;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
}

/* Python-specific syntax coloring */
.hljs-keyword {
  color: #d73a49; /* Red for keywords */
}

.hljs-built_in {
  color: #005cc5; /* Blue for built-ins */
}

.hljs-string {
  color: #032f62; /* Dark blue for strings */
}

.hljs-number {
  color: #005cc5; /* Blue for numbers */
}

.hljs-comment {
  color: #6a737d; /* Gray for comments */
  font-style: italic;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .assignment-meta {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
