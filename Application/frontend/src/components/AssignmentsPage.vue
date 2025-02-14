<template>
  <div>
    <AppNavbar/>
    <div class="container-fluid">
      <div class="row">
        <!-- Sidebar -->
        <AppSidebar/>

        <!-- Main Content -->
        <div class="col-9 p-4">
          <!-- Dynamic Title -->
          <h4>{{ title }}</h4>

          <!-- Questions Section -->
          <div v-for="(question, index) in questions" :key="index" class="question-container mb-4 p-3">
            <p><strong>{{ index + 1 }}. {{ question.text }}</strong></p>
            <div class="options-container">
              <div
                v-for="(option, optionIndex) in question.options"
                :key="optionIndex"
                class="form-check"
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
                    showScore
                    ? option === correctAnswers[index]
                    ? 'text-success'
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
            <p v-if="showScore && userAnswers[index] !== correctAnswers[index]" class="correct-answer-text mt-2">
              Correct Answer: <span class="text-success">{{ correctAnswers[index] }}</span>
            </p>
          </div>

          <!-- Check Score Button -->
          <button @click="checkScore" class="btn btn-dark">
            Check Score
          </button>

          <!-- Score and Suggestions Section -->
          <div v-if="showScore" class="score-modal mt-4 p-3 rounded shadow-sm bg-light">
            <h5>Your Score: {{ score }}/{{ questions.length }}</h5>
            <p><strong>Suggestions to Improve:</strong></p>
            <ul>
              <li v-for="(suggestion, index) in suggestions" :key="'suggestion-' + index">
                {{ suggestion }}
              </li>
            </ul>
            <button @click="downloadReport" class="btn btn-secondary mt-3">Download Report</button>
          </div>
        </div>
      </div>

      <!-- Ask Me Button -->
      <button @click="redirectToChatbot" class="ai-button ask-me-btn">
        <img :src="StudentIcon" class="ai-icon me-2" alt="AI Assistant"/>
        Ask Kia
      </button>
    </div>
  </div>
</template>

<script>
import AppSidebar from "@/components/AppSidebar.vue";
import AppNavbar from "@/components/AppNavbar.vue";
import StudentIcon from "@/assets/student.png";

export default {
  name: "AssignmentsPage",
  components: {
    AppNavbar,
    AppSidebar,
  },
  props: {
    title: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      questions: [
        {
          text: "What is Pandas?",
          options: [
            "A data visualization library",
            "A web development framework",
            "A data manipulation library",
            "A machine learning framework",
          ],
        },
        {
          text: "What is the primary data structure in Pandas for one-dimensional labeled data?",
          options: ["Series", "DataFrame", "Array", "List"],
        },
        {
          text: "How do you read a CSV file into a Pandas DataFrame?",
          options: ["pd.read_csv()", "pd.load_csv()", "pd.read_data", "pd.import_csv()"],
        },
      ],
      userAnswers: Array(3).fill(null),
      // Placeholder for user answers
      correctAnswers: [
        "A data manipulation library",
        "Series",
        "pd.read_csv()",
      ],
      score: 0,
      showScore: false,
      suggestions: ["Review concepts of Pandas library", "Practice more on data preprocessing problems"],
      StudentIcon,
    };
  },
  methods: {
    checkScore() {
      this.score = this.userAnswers.reduce((total, answer, index) => {
        return total + (answer === this.correctAnswers[index] ? 1 : 0);
      }, 0);
      this.showScore = true;
    },
    downloadReport() {
      const reportContent = `Your Score: ${this.score}/${this.questions.length}

Suggestions to Improve:- ${this.suggestions.join("\n- ")}`;
      const blob = new Blob([reportContent], { type: "text/plain" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = "assignment-report.txt";
      link.click();
    },
    redirectToChatbot() {
      alert("Redirecting to chatbot..."); // Replace with actual routing logic if needed
    },
  },
};
</script>

<style scoped>
.question-container {
  background-color: #f8f9fa;
  padding: 15px;
  border-bottom: 1px solid #ddd;
}

.score-modal {
  margin-top: 20px;
  padding: 20px;
  border-radius: 8px;
  background-color: #f8f9fa;
  box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);
}

/* Correct and Wrong Answer Styles */
.text-success {
  color: #28a745 !important; /* Green for correct answers */
}

.text-danger {
  color: #dc3545 !important; /* Red for incorrect answers */
}

.correct-answer-text .text-success {
  font-weight: bold;
}

.ask-me-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: linear-gradient(135deg, #f5f5f7 0%, #e8e8ea 100%);
  border: 1px solid #e0e0e0; /* Adding a thin border */
  color: #606060;
  z-index: 1000;
}

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
.ai-icon {
  width: 24px;
}
</style>
