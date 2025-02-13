<template>
  <div>
    <!-- Navigation Bar -->
    <AppNavbar/>

    <!-- Main Layout -->
    <div class="container-fluid">
      <div class="row">
        <!-- Sidebar -->
        <AppSidebar/>

        <!-- Main Content -->
        <div class="col-9 p-4">
          <!-- Programming Assignment Interface -->
          <h4>Programming Assignment: Train an SVM Classifier</h4>
          <p>Write Python code to train an SVM classifier with specific parameters and data points.</p>

          <!-- Ace Editor Component -->
          <div class="editor-container mb-4">
            <AceEditor
              :value="code"
            />
          </div>

          <!-- Buttons -->
          <div class="d-flex justify-content-end mt-3">
            <button @click="testCode" class="btn btn-primary me-2">Test</button>
            <button @click="submitCode" class="btn btn-success">Submit</button>
          </div>

          <!-- Test Case Results -->
          <div class="test-case-results mt-4">
            <h5>Test Case Results</h5>
            <ul class="list-group">
              <li
                v-for="(result, index) in testCaseResults"
                :key="'test-case-' + index"
                :class="['list-group-item', result.passed ? 'bg-success text-white' : 'bg-danger text-white']"
              >
                {{ result.message }}
              </li>
            </ul>
          </div>

          <!-- Console Output -->
          <h5 class="mt-4">Console</h5>
          <div class="console-output p-3 bg-dark text-white rounded">
            {{ consoleOutput }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// Import assets and components
import AceEditor from "@/components/AceEditor.vue";
import AppNavbar from "@/components/AppNavbar.vue";
import AppSidebar from "@/components/AppSidebar.vue";
import axios from "axios";

export default {
  name: "ProgrammingPage",
  components: {
    AceEditor,
    AppSidebar,
    AppNavbar,
  },
  data() {
    return {
      code: "# Write your Python code here...",
      consoleOutput: "",
      testCaseResults: [],
      // Array to store test case results
    };
  },
  methods: {
    async testCode() {
      try {
        const response = await axios.post("http://127.0.0.1:5000/test", { code: this.code });
        this.consoleOutput = response.data.output;
        this.testCaseResults = response.data.testCases || [];
      } catch (error) {
        this.consoleOutput = `Error: $ {
error.response ? error.response.data.error : error.message
}`;
      }
    },
    async submitCode() {
      try {
        const response = await axios.post("http://127.0.0.1:5000/submit", { code: this.code });
        this.consoleOutput = response.data.message;
      } catch (error) {
        this.consoleOutput = `Error: $ {
error.response ? error.response.data.error : error.message
}`;
      }
    },
  },
};
</script>

<style scoped>
/* Styling for the editor container */
.editor-container {
  border: 1px solid #ddd;
  border-radius: 5px;
}

/* Console output styling */
.console-output {
  min-height: 150px;
  font-family: monospace;
  white-space: pre-wrap;
}

/* Test case results styling */
.test-case-results ul {
  padding-left: 0;
}

.test-case-results .list-group-item {
  font-size: 14px;
}
</style>
