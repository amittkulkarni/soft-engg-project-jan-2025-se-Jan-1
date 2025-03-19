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
            <h3 class="mb-3 text-center">Generate Mock Quizzes</h3>

            <!-- Configuration Options (removed question count) -->
            <div class="row mb-4 justify-content-center">
              <div class="col-md-6">
                <div class="form-group mb-3">
                  <label for="difficultySelect">Difficulty:</label>
                  <select id="difficultySelect" v-model="mockDifficulty" class="form-select">
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Centralized Buttons -->
            <div class="d-flex flex-wrap gap-3 mb-4 justify-content-center">
              <button
                @click="generateMockQuiz('mock_quiz_1')"
                class="btn btn-outline-primary btn-lg">
                <i class="bi bi-lightning me-1"></i> Mock Quiz 1
              </button>
              <button
                @click="generateMockQuiz('mock_quiz_2')"
                class="btn btn-outline-primary btn-lg">
                <i class="bi bi-lightning-fill me-1"></i> Mock Quiz 2
              </button>
              <button
                @click="generateMockQuiz('end_term')"
                class="btn btn-outline-danger btn-lg">
                <i class="bi bi-file-earmark-text me-1"></i> End Term Practice
              </button>
            </div>

            <div v-if="generatingMock" class="d-flex align-items-center justify-content-center mt-3">
              <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <span>Generating {{ mockType }} questions...</span>
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
                <span class="text-muted">
                  <i class="bi bi-gear me-1"></i> Difficulty: {{ mockDifficulty }}
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
                <p class="question-text mb-3"><strong>{{ index + 1 }}. {{ question.text }}</strong></p>
                <span class="badge bg-secondary">{{ question.points }} pts</span>
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
import { jsPDF } from "jspdf";

export default {
  name: "MockQuizPage",
  components: {
    AppNavbar,
    AppSidebar,
    ChatWindow
  },
  data() {
    return {
      loading: false,
      error: null,
      mockQuizGenerated: false,
      generatingMock: false,
      mockType: null,
      mockDifficulty: 'medium',
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
      suggestions: []
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

        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));

        // Generate placeholder questions instead of API call
        const response = this.generatePlaceholderQuestions(
          quizType,
          this.mockDifficulty,
          5
        );

        // Process the response
        if (response.success) {
          // Set mock quiz data
          this.mockQuiz = {
            id: 'mock-' + Date.now(),
            title: this.formatMockType(quizType),
            total_points: response.total_points,
          };

          // Transform questions data
          this.questions = response.questions.map(q => ({
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

          // Generate default suggestions
          this.generateDefaultSuggestions();
        } else {
          this.error = 'Failed to generate mock quiz';
        }
      } catch (error) {
        console.error('Error generating mock quiz:', error);
        this.error = 'Error generating mock quiz. Please try again.';
      } finally {
        this.generatingMock = false;
      }
    },

    // Generate placeholder questions for testing
    generatePlaceholderQuestions(quizType, difficulty, count) {
      const questions = [];

      // Question templates based on difficulty
      const questionTemplates = {
        easy: [
          "What is the primary purpose of a constructor in object-oriented programming?",
          "Which data structure follows the First-In-First-Out principle?",
          "What does HTML stand for?",
          "Which of these is NOT a JavaScript data type?",
          "What is the purpose of CSS in web development?"
        ],
        medium: [
          "What is the time complexity of binary search?",
          "Which design pattern is used to create a single instance of a class?",
          "What is the difference between == and === in JavaScript?",
          "Explain the concept of function hoisting in JavaScript",
          "What is the box model in CSS?"
        ],
        hard: [
          "Explain the differences between a process and a thread in operating systems",
          "What are the ACID properties in database transactions?",
          "Describe the principles of RESTful API design",
          "Compare and contrast virtual memory and physical memory",
          "Explain how the event loop works in Node.js"
        ]
      };

      // Options templates based on difficulty
      const optionsTemplates = {
        easy: [
          ["To initialize object properties", "To destroy objects", "To define class methods", "To export the class"],
          ["Queue", "Stack", "Tree", "Hash Table"],
          ["Hypertext Markup Language", "High-level Technical Machine Language", "Hyper Transfer Markup Language", "Home Tool Markup Language"],
          ["Object", "String", "Array", "Character"],
          ["To add functionality", "To structure content", "To style web pages", "To handle server requests"]
        ],
        medium: [
          ["O(1)", "O(n)", "O(log n)", "O(n²)"],
          ["Factory Pattern", "Observer Pattern", "Singleton Pattern", "Decorator Pattern"],
          ["They are identical", "== compares values, === compares values and types", "=== is deprecated", "== is faster"],
          ["Functions are always available regardless of where they're defined", "Functions are moved to the top of their scope", "Functions are hidden until called", "Functions are copied to every scope"],
          ["A layout paradigm for arranging elements", "A CSS framework", "A JavaScript library", "A HTML structure"]
        ],
        hard: [
          ["Processes are lightweight, threads are heavyweight", "Processes share memory space, threads don't", "Threads have separate memory spaces, processes share memory", "Processes can contain multiple threads, threads are single-execution units"],
          ["Atomicity, Consistency, Isolation, Durability", "Authentication, Caching, Integration, Deployment", "Authority, Control, Independence, Distribution", "Accuracy, Completeness, Integrity, Delivery"],
          ["Using only GET and POST methods", "Resource-based URLs, proper HTTP methods, statelessness", "Always returning JSON responses", "Requiring authentication for all endpoints"],
          ["Virtual memory is faster but more expensive", "Physical memory is larger than virtual memory", "Virtual memory uses disk space to extend RAM", "There's no difference in modern systems"],
          ["It processes events in parallel using multiple threads", "It runs a single thread that processes an event queue", "It delegates events to the operating system", "It creates a new process for each event"]
        ]
      };

      // Correct answers based on difficulty (index of correct option)
      const correctAnswersIndex = {
        easy: [0, 0, 0, 3, 2],
        medium: [2, 2, 1, 1, 0],
        hard: [3, 0, 1, 2, 1]
      };

      // Point values for each difficulty
      const pointValues = {
        easy: 5,
        medium: 10,
        hard: 15
      };

      // Use number of questions requested (capped at available templates)
      const numQuestions = Math.min(count, questionTemplates[difficulty].length);

      for (let i = 0; i < numQuestions; i++) {
        const questionText = questionTemplates[difficulty][i];
        const options = optionsTemplates[difficulty][i];
        const correctIndex = correctAnswersIndex[difficulty][i];

        // Create question object
        const question = {
          id: `q-${i + 1}`,
          question_text: questionText,
          question_type: 'multiple_choice',
          points: pointValues[difficulty],
          options: options.map((text, idx) => ({
            id: `opt-${i + 1}-${idx + 1}`,
            option_text: text,
            is_correct: idx === correctIndex
          }))
        };

        questions.push(question);
      }

      return {
        success: true,
        questions: questions,
        total_points: numQuestions * pointValues[difficulty]
      };
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

      if (this.mockDifficulty === 'hard' && this.score / this.totalPossiblePoints < 0.5) {
        specificSuggestions.push("Try generating a medium difficulty quiz first to build confidence.");
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
      doc.text(`Practice Material (${this.mockDifficulty} difficulty)`, 20, 30);
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
        case 'mock_quiz_1': return 'Mock Quiz 1';
        case 'mock_quiz_2': return 'Mock Quiz 2';
        case 'end_term': return 'End Term Practice';
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

/* Responsive adjustments */
@media (max-width: 768px) {
  .assignment-meta {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
