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
          <div class="problem-statement mb-5">
            <!-- Assignment Header -->
            <div class="assignment-header mb-4">
              <h3>{{ 'Programming Assignment ' + assignment.id }}</h3>
              <div class="assignment-meta d-flex flex-wrap gap-3 mt-2">
                <span class="badge bg-info">Programming Assignment</span>
                <span v-if="assignment.due_date" class="text-muted">
                  <i class="bi bi-calendar-event me-1"></i> Due: {{ formatDate(assignment.due_date) }}
                </span>
                <span class="text-muted">
                  <i class="bi bi-code-slash me-1"></i> Week {{ assignment.week_number || '?' }}
                </span>
              </div>
            </div>
            <div class="problem-content bg-light p-4 rounded shadow-sm mb-4">
              <h5 class="mb-3 pb-2 border-bottom">Problem Description</h5>
              <p class="mb-3" v-html="assignment.problem_statement"></p>

              <div class="mb-4 problem-section">
                <h6 class="font-weight-bold text-dark">
                  <i class="bi bi-input-cursor me-1"></i> Input Format
                </h6>
                <pre class="bg-white p-3 rounded border">{{ assignment.input_format }}</pre>
              </div>

              <div class="mb-4 problem-section" v-if="assignment.constraints">
                <h6 class="font-weight-bold text-dark">
                  <i class="bi bi-exclamation-triangle me-1"></i> Constraints
                </h6>
                <pre class="bg-white p-3 rounded border">{{ assignment.constraints }}</pre>
              </div>

              <div class="mb-4 problem-section">
                <h6 class="font-weight-bold text-dark">
                  <i class="bi bi-output me-1"></i> Output Format
                </h6>
                <pre class="bg-white p-3 rounded border">{{ assignment.output_format }}</pre>
              </div>

              <div class="row g-4">
                <div class="col-md-6">
                  <h6 class="font-weight-bold text-dark">
                    <i class="bi bi-input-cursor-text me-1"></i> Sample Input
                  </h6>
                  <pre class="bg-white p-3 rounded border">{{ assignment.sample_input }}</pre>
                </div>
                <div class="col-md-6">
                  <h6 class="font-weight-bold text-dark">
                    <i class="bi bi-output me-1"></i> Sample Output
                  </h6>
                  <pre class="bg-white p-3 rounded border">{{ assignment.sample_output }}</pre>
                </div>
              </div>
            </div>
          </div>
          <!-- Code Editor Section -->
          <div class="editor-section mb-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h5 class="mb-0"><i class="bi bi-code-square me-2"></i>Your Solution</h5>
              <div>
                <button @click="code = '# Write your Python code here...'" class="btn btn-sm btn-outline-secondary me-2">
                  <i class="bi bi-arrow-counterclockwise me-1"></i> Reset
                </button>
              </div>
            </div>
            <div class="editor-container border rounded shadow-sm">
              <AceEditor v-model="code" />
            </div>

            <div class="d-flex justify-content-end gap-2 mt-3">
              <button @click="submitCode" class="btn btn-primary">
                <i class="bi bi-play-fill me-1"></i> Run & Submit
              </button>
            </div>
          </div>

          <!-- Test Case Results -->
          <!-- Loading Indicator -->
          <div v-if="isLoading" class="d-flex justify-content-center my-5">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="alert alert-danger" role="alert">
            {{ errorMessage }}
            <button class="btn btn-sm btn-outline-danger float-end" @click="errorMessage = null">Dismiss</button>
          </div>

          <!-- Success Message -->
          <div v-if="showSuccessMessage" class="alert alert-success alert-dismissible fade show" role="alert">
            Code submitted successfully!
            <button type="button" class="btn-close" @click="showSuccessMessage = false" aria-label="Close"></button>
          </div>

          <!-- Only show the content when not loading and no error -->
          <div v-if="!isLoading && !errorMessage">
            <!-- Your existing content -->
            <!-- Test Case Results -->
            <div v-if="showResults" class="test-results mt-4 mb-4">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="mb-0"><i class="bi bi-clipboard-check me-2"></i>Test Results</h5>
                <div class="d-flex align-items-center">
                  <div class="progress" style="width: 150px; height: 10px;">
                    <div class="progress-bar" role="progressbar"
                        :style="{width: (passedCount/totalCases*100) + '%'}"
                        :class="getScoreClass(passedCount/totalCases)">
                    </div>
                  </div>
                  <span class="ms-2">{{ passedCount }}/{{ totalCases }}</span>
                </div>
              </div>
            <div class="test-case-container">
              <div
                v-for="(result, index) in testCaseResults"
                :key="index"
                class="test-case-card"
                :class="result.status"
              >
                <div class="card-icon">
                  <transition name="scale">
                    <!-- Wrap icons in a container div -->
                    <div class="icon-container">
                      <svg v-if="result.status === 'passed'" class="icon-check">
                        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                      </svg>
                      <svg v-else-if="result.status === 'failed'" class="icon-cross">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                      </svg>
                      <svg v-else class="icon-pending">
                        <path d="M12 4V1L8 5l4 4V6c3.31 0 6 2.69 6 6 0 1.01-.25 1.97-.7 2.8l1.46 1.46A7.93 7.93 0 0020 12c0-4.42-3.58-8-8-8zm0 14c-3.31 0-6-2.69-6-6 0-1.01.25-1.97.7-2.8L5.24 7.74A7.93 7.93 0 004 12c0 4.42 3.58 8 8 8v3l4-4-4-4v3z"/>
                      </svg>
                    </div>
                  </transition>
                </div>

                <div class="card-content">
                  <div class="progress-ring">
                    <svg :class="result.status">
                      <circle cx="20" cy="20" r="18"/>
                    </svg>
                  </div>
                  <div class="case-info">
                    <h6>{{ result.title }}</h6>
                    <p class="description">{{ result.description }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          </div>

          <!-- Console Output -->
          <div class="console-section mt-4">
            <div class="d-flex justify-content-between align-items-center mb-2">
              <h5 class="mb-0"><i class="bi bi-terminal me-2"></i>Console</h5>
              <div>
                <button v-if="consoleOutput" @click="consoleOutput = ''" class="btn btn-sm btn-outline-secondary me-2">
                  <i class="bi bi-trash me-1"></i> Clear
                </button>
                <button
                  v-if="consoleOutput.includes('Error')"
                  @click="explainError"
                  class="btn btn-sm btn-outline-info"
                >
                  <img :src="StudentIcon" class="ai-icon me-2" alt="AI Assistant" width="16" height="16"/>
                  Explain Error
                </button>
              </div>
            </div>
            <div class="console-output p-3 bg-dark text-white rounded shadow-sm">
              <div v-if="!consoleOutput" class="text-muted font-italic">
                Run your code to see output here...
              </div>
              <pre v-else>{{ consoleOutput }}</pre>
            </div>
          </div>
        </div>
      </div>
      <ChatWindow/>
    </div>
  </div>
</template>

<script>
// Import assets and components
import AceEditor from "@/components/AceEditor.vue";
import AppNavbar from "@/components/AppNavbar.vue";
import AppSidebar from "@/components/AppSidebar.vue";
import StudentIcon from "@/assets/student.png"
import ChatWindow from "@/components/ChatWindow.vue";
import api from "@/services/api"
export default {
  name: "ProgrammingPage",
  components: {
    AceEditor,
    AppSidebar,
    AppNavbar,
    ChatWindow
  },
  data() {
    return {
      assignmentId: null, // Will be set from route or props
      code: "# Write your Python code here...",
      consoleOutput: "",
      assignment: {
        problem_statement: "",
        input_format: "",
        output_format: "",
        constraints: "",
        sample_input: "",
        sample_output: "",
        test_cases: []
      },
      testCaseResults: [],
      StudentIcon,
      showResults: false,
      isLoading: false,
      errorMessage: null,
      showSuccessMessage: false
    };
  },
  created() {
    // Get the assignment ID from the route params (this should be the Assignment table ID)
    this.assignmentId = this.$route.params.id || 1; // Default to 1 if not provided

    // Fetch the assignment data
    this.fetchAssignmentData();
  },
  watch: {
    // Watch for changes in the route parameter
    '$route.params.id': function(newId) {
      // Update the assignment ID
      this.assignmentId = newId || 1;
      // Reset component state
      this.code = "# Write your Python code here...";
      this.consoleOutput = "";
      this.showResults = false;
      this.errorMessage = null;
      this.showSuccessMessage = false;
      // Fetch the new assignment data
      this.fetchAssignmentData();
    }
  },
  computed: {
    passedCount() {
      return this.testCaseResults.filter(tc => tc.status === 'passed').length;
    },
    totalCases() {
      return this.testCaseResults.length;
    }
  },
  methods: {
    async fetchAssignmentData() {
      try {
        this.isLoading = true;
        const response = await api.get(`/programming_assignments/${this.assignmentId}`);

        if (response.data.success) {
          // Store the assignment data
          this.assignment = response.data.data;

          // Initialize test case results based on the fetched test cases
          this.testCaseResults = this.assignment.test_cases.map((testCase, index) => ({
            status: 'pending',
            title: `Test Case ${index + 1}`,
            description: testCase.description || 'Waiting to be executed'
          }));
        } else {
          this.errorMessage = response.data.message || 'Failed to load assignment data';
        }
      } catch (error) {
        this.errorMessage = error.response?.data?.message || 'An error occurred while fetching assignment';
        console.error('Error fetching assignment:', error);
      } finally {
        this.isLoading = false;
      }
    },
    codeChanged(newValue) {
      console.log("Code updated in parent:", newValue.slice(0, 50) + "..."); // Debug log
      this.code = newValue;
    },
    /* Add this method to your component */
    getScoreClass(scorePercentage) {
      if (scorePercentage >= 0.9) return 'bg-success';
      if (scorePercentage >= 0.7) return 'bg-info';
      if (scorePercentage >= 0.5) return 'bg-warning';
      return 'bg-danger';
    },
    // When the user submits their code
    async submitCode() {
       if (this.code.trim() === "# Write your Python code here..." || !this.code.trim()) {
         this.consoleOutput = "Error: You haven't written any code yet. Please write a solution before submitting.";
         this.errorMessage = "Please write your solution before submitting";
         return;
       }

      try {
        this.isLoading = true;
        this.showResults = false;
        this.errorMessage = null;
        this.showSuccessMessage = false;

        // Update console to show execution is in progress
        this.consoleOutput = "Executing your code...\n";

        const response = await api.post(
          `/programming_assignments/${this.assignment.id}/execute`,
          { code: this.code }
        );

        // Inside the submitCode method where you format the console output
        if (response.data.success) {
          // Process results
          const results = response.data;
          let output = "";

          // Check if there are any errors and extract them
          const errors = results.results
            .filter(result => result.status === 'error')
            .map(result => result.error_message);

          // Display unique errors at the top
          if (errors.length > 0) {
            output += `=== ERROR SUMMARY ===\n`;
            // Use Set to remove duplicate error messages
            const uniqueErrors = [...new Set(errors)];
            uniqueErrors.forEach(error => {
              output += `Error: ${error}\n`;
            });
            output += `\n`;
          }

          // Then show execution summary
          output += `=== EXECUTION SUMMARY ===\n`;
          output += `Score: ${results.score.toFixed(2)}%\n`;
          output += `Passed: ${results.passed_count}/${results.total_cases}\n\n`;

          // Add detailed test case results to console without repeating errors
          results.results.forEach(result => {
            output += `=== TEST CASE ${result.test_case_id} ===\n`;
            output += `Status: ${result.status.toUpperCase()}\n`;

            // Only show input and output details, not the error again
            output += `Input:\n${result.input}\n\n`;

            if (result.status !== 'error') {
              output += `Expected Output:\n${result.expected_output}\n\n`;
              output += `Your Output:\n${result.actual_output}\n\n`;
            } else {
              // Just reference that there was an error
              output += `See error details at the top of the console output\n\n`;
            }
          });

          // Update console
          this.consoleOutput = output;

          // Update the test case results for UI display
          this.testCaseResults = results.results.map(result => ({
            status: result.status,
            title: `Test Case ${result.test_case_id}`,
            description: result.status === 'passed'
              ? 'Output matched expected result'
              : result.status === 'error'
                ? `Error: ${result.error_message}`
                : 'Output did not match expected result'
          }));

          // Show both success message and results
          this.showSuccessMessage = true;
          this.showResults = true;
        } else {
          // Handle API error
          this.errorMessage = response.data.message || 'An error occurred';
          this.consoleOutput = `Execution Error: ${response.data.message || 'Unknown error'}\n`;
          if (response.data.error) {
            this.consoleOutput += `Details: ${response.data.error}\n`;
          }
        }
      } catch (error) {
        // Handle network or other errors
        const errorMsg = error.response?.data?.message || error.message || 'An unknown error occurred';
        this.errorMessage = errorMsg;
        this.consoleOutput = `Execution Error: ${errorMsg}\n`;
        if (error.response?.data?.error) {
          this.consoleOutput += `Details: ${error.response.data.error}\n`;
        }
        console.error('Error executing code:', error);
      } finally {
        this.isLoading = false;
      }
    },
    async explainError() {
      try {
        // Show loading state in console
        this.consoleOutput = "Analyzing your error...\n";

        // Make API request using axios
        const response = await api.post('/explain_error', {
          code_snippet: this.code
        });

        // Check if request was successful
        if (response.data.success) {
          // Format the explanation nicely
          this.consoleOutput = `=== AI ERROR ANALYSIS ===\n\n${response.data.explanation}`;
        } else {
          // Handle API success=false response
          this.consoleOutput = `Error Analysis Failed: ${response.data.message}`;
          console.error("API Error:", response.data.message);
        }
      } catch (error) {
        // Enhanced error handling
        if (error.response) {
          // The server responded with a status code outside of 2xx range
          this.consoleOutput = `Error Analysis Failed: ${error.response.data.message || 'Server error'}`;
          console.error("Server error:", error.response.status, error.response.data);
        } else if (error.request) {
          // The request was made but no response was received
          this.consoleOutput = "Error Analysis Failed: Network error - no response received";
          console.error("Network error:", error.request);
        } else {
          // Something happened in setting up the request
          this.consoleOutput = `Error Analysis Failed: ${error.message}`;
          console.error("Error:", error.message);
        }
      }
    }
  }
};
</script>

<style scoped>

/* Console output styling */
.console-output {
  min-height: 200px;
  font-family: monospace;
  white-space: pre-wrap;
  position: relative;
  overflow-x: auto;
}

/* Test case results styling */
.test-case-results ul {
  padding-left: 0;
}

.test-case-results .list-group-item {
  font-size: 14px;
}

.problem-statement {
  font-size: 0.95rem;
}

pre {
  font-family: monospace;
  white-space: pre-wrap;
  max-height: 300px;
  overflow-y: auto;
}

.problem-content h5 {
  color: #2c3e50;
  border-bottom: 2px solid #eee;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}
/* Highlight error messages */
[class*="bg-danger"] {
  border-left: 4px solid #dc3545;
}

[class*="bg-success"] {
  border-left: 4px solid #28a745;
}

.test-case-container {
  display: grid;
  gap: 12px;
}

.icon-container {
  position: relative;
  width: 24px;
  height: 24px;
}

.icon-container > svg {
  position: absolute;
  top: 0;
  left: 0;
  transition: opacity 0.2s ease;
}

.test-case-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
  overflow: hidden;
}

.test-case-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.card-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  flex-shrink: 0;
}

.card-icon svg {
  width: 24px;
  height: 24px;
  fill: currentColor;
}

.icon-check { color: #38a169; }
.icon-cross { color: #e53e3e; }
.icon-pending { color: #718096; }

.progress-ring {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
}

.progress-ring svg {
  width: 40px;
  height: 40px;
  transform: rotate(-90deg);
}

.progress-ring circle {
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
}

.passed .progress-ring circle {
  stroke: #c6f6d5;
  stroke-dasharray: 113;
  stroke-dashoffset: 0;
}

.failed .progress-ring circle {
  stroke: #fed7d7;
  stroke-dasharray: 113;
  stroke-dashoffset: 56.5;
}

.pending .progress-ring circle {
  stroke: #edf2f7;
  stroke-dasharray: 113;
  stroke-dashoffset: 113;
  animation: ring-spin 1.5s linear infinite;
}

.case-info h6 {
  font-size: 0.9rem;
  margin: 0 0 4px 0;
  color: #2d3748;
}

.description {
  font-size: 0.85rem;
  margin: 0;
  color: #718096;
}

@keyframes ring-spin {
  0% { stroke-dashoffset: 113; }
  50% { stroke-dashoffset: 0; }
  100% { stroke-dashoffset: -113; }
}
.assignment-header {
  border-bottom: 1px solid #eaeaea;
  padding-bottom: 15px;
}

.problem-section {
  transition: all 0.2s ease;
}

.problem-section:hover {
  transform: translateY(-2px);
}

.editor-container {
  border: 1px solid #ddd;
  border-radius: 5px;
  overflow: hidden;
}

.test-case-card {
  display: flex;
  align-items: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  margin-bottom: 10px;
  border-left: 4px solid #6c757d;
}

.test-case-card.passed {
  border-left-color: #28a745;
}

.test-case-card.failed {
  border-left-color: #dc3545;
}

.test-case-card.error {
  border-left-color: #ffc107;
}

.test-case-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.console-output {
  min-height: 200px;
  font-family: monospace;
  white-space: pre-wrap;
  position: relative;
  overflow-x: auto;
}
</style>

