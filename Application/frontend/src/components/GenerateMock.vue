<template>
  <div>
    <AppNavbar/>
    <div class="container-fluid">
      <div class="row">
        <!-- Sidebar -->
        <AppSidebar/>

        <!-- Main Content -->
        <div class="col-9 p-4">
          <!-- Search Bar -->
          <div class="search-section">
            <h2 class="text-center mb-4">Generate Topic-Specific Questions</h2>
            <div class="search-bar-container">
              <input
                v-model="searchQuery"
                @input="fetchSuggestions"
                type="text"
                placeholder="Search topics..."
                class="form-control search-input"
              />
              <ul v-if="suggestions.length" class="suggestions-list">
                <li
                  v-for="(suggestion, index) in suggestions"
                  :key="index"
                  @click="selectSuggestion(suggestion)"
                  class="suggestion-item"
                >
                  {{ suggestion }}
                </li>
              </ul>
              <button
                :disabled="!selectedTopic"
                @click="generateQuestions"
                class="btn btn-dark mt-3"
              >
                Generate Questions
              </button>
            </div>
          </div>
          <!-- Questions Section -->
          <div v-if="questions.length" class="questions-section mt-5">
            <h4>Practice Questions on {{ selectedTopic }}</h4>
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
                      ? option === question.correct
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
              <p v-if="showScore && userAnswers[index] !== question.correct" class="correct-answer-text mt-2">
                Correct Answer: <span class="text-success">{{ question.correct }}</span>
              </p>
            </div>
            <!-- Check Score Button -->
            <button @click="checkScore" class="btn btn-dark check-score-btn mt-4">Check Score</button>

            <!-- Score Modal -->
            <div v-if="showScore" class="score-modal mt-4 p-3 rounded shadow-sm bg-light">
              <h5>Your Score: {{ score }}/{{ questions.length }}</h5>

              <!--&lt;!&ndash; Correct and Incorrect Answers &ndash;&gt;-->
              <!--<div v-for="(question, index) in questions" :key="'score-' + index" class="mb-3">-->
              <!--  <p><strong>{{ index + 1 }}. {{ question.text }}</strong></p>-->

              <!--  <ul>-->
              <!--    <li-->
              <!--      v-for="(option, optionIndex) in question.options"-->
              <!--      :key="'option-' + optionIndex"-->
              <!--      :class=" {-->
              <!--        'text-success': option === question.correct,-->
              <!--        'text-danger': userAnswers[index] === option && option !== question.correct,-->
              <!--      }"-->
              <!--    >-->
              <!--      {{ option }}-->
              <!--    </li>-->
              <!--  </ul>-->

              <!--  &lt;!&ndash; Show Correct Answer if Answered Incorrectly &ndash;&gt;-->
              <!--  <p v-if="userAnswers[index] !== question.correct" class="mt-2">-->
              <!--    Correct Answer:-->
              <!--    <span class="text-success">-->
              <!--      {{ Array.isArray(question.correct) ? question.correct.join(", ") : question.correct }}-->
              <!--    </span>-->
              <!--  </p>-->
              <!--</div>-->

              <!-- AI Suggestions -->
              <div>
                <h6>Suggestions to Improve:</h6>
                <ul>
                  <li v-for="(suggestion, index) in aiSuggestions" :key="'suggestion-' + index">
                    {{ suggestion }}
                  </li>
                </ul>
              </div>

              <!-- Download Report Button -->
              <button @click="downloadReport" class="btn btn-secondary mt-3">Download Report</button>
            </div>

            <!-- Ask Me Button -->
            <button @click="redirectToChatbot" class="ai-button ask-me-btn">
              <img :src="StudentIcon" class="me-1" alt="AI Assistant"/>
              Ask Kia
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import AppNavbar from "@/components/AppNavbar.vue";
import AppSidebar from "@/components/AppSidebar.vue";
import StudentIcon from "@/assets/student.png";

export default {
  name: "GenerateMock",
  components: {
    AppNavbar,
    AppSidebar,
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
      aiSuggestions: [
        "Review Pandas library concepts",
        "Practice more with DataFrame operations",
        "Learn about CSV file handling in Python",
      ],
      StudentIcon
    };
  },
  methods: {
    fetchSuggestions() {
      const topics = [
        "Regression",
        "Auto-regressive model",
        "Linear Regression",
        "Probabilistic Regression Model",
        "Logistic Regression",
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
      this.questions = [
        {
          text: "What is Pandas?",
          options: [
            "A data visualization library",
            "A web development framework",
            "A data manipulation library",
            "A machine learning framework",
          ],
          correct: "A data manipulation library"
        },
        {
          text: "What is the primary data structure in Pandas for one-dimensional labeled data?",
          options: ["Series", "DataFrame", "Array", "List"],
          correct: "Series"
        },
        {
          text: "How do you read a CSV file into a Pandas DataFrame?",
          options: ["pd.read_csv()", "pd.load_csv()", "pd.read_data", "pd.import_csv()"],
          correct: "pd.read_csv()"
        },
      ];
      this.userAnswers = Array(this.questions.length).fill(null);
      this.showScore = false;
      this.score = 0;
    },
    checkScore() {
      this.score = this.questions.reduce((total, question, index) => {
        return total + (this.userAnswers[index] === question.correct ? 1 : 0);
      }, 0);
      this.showScore = true;
    },
    downloadReport() {
      const reportContent = `Your Score: ${this.score}/${this.questions.length}

Suggestions to Improve:  ${this.aiSuggestions.map(s => `- ${s}`).join('\n')}

Correct Answers:
${this.questions.map((q, i) => `${i+1}. ${q.text}\n   Correct: ${q.correct}`).join('\n\n')}`;

      const blob = new Blob([reportContent], { type: "text/plain" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `${this.selectedTopic}-report.txt`;
      link.click();
    },
    redirectToChatbot() {
      alert("Redirecting to chatbot...");
    }
  }
};
</script>

<style scoped>
.search-section {
  max-width: 600px;
  margin: auto;
}
.search-bar-container {
  position: relative;
}
.search-input {
  width: 100%;
  padding: 10px;
}
.suggestions-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: white;
  border: 1px solid #ccc;
}
.suggestion-item {
  padding: 10px;
  cursor: pointer;
}
.suggestion-item:hover {
  background-color: #f0f0f0;
}
.questions-section h4 {
  margin-bottom: 20px;
}
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
.text-success {
  color: #28a745 !important; /* Green for correct answers */
}

.text-danger {
  color: #dc3545 !important; /* Red for incorrect answers */
}

</style>
