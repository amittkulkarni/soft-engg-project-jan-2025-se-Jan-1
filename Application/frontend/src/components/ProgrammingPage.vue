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
          <!-- Question Section -->
          <div class="problem-statement mb-5">
          <h4 class="mb-4">Predicting Office Space Price</h4>

            <div class="problem-content bg-light p-4 rounded">
              <h5 class="mb-3">The Problem</h5>
              <p class="mb-3">
                Charlie wants to buy office space and has conducted a survey of the area. He has quantified and normalized various office space features, and mapped them to values between 0 and 1. Each row in Charlie's data table contains these feature values followed by the price per square foot. However, some prices are missing. Charlie needs your help to predict the missing prices.
              </p>
              <p class="mb-3">
                The first line contains two space separated integers, F and N. Over here, F is the number of observed features. N is the number of rows for which features as well as price per square-foot have been noted.
                This is followed by a table with F+1 columns and N rows with each row in a new line and each column separated by a single space. The last column is the price per square foot.

                The table is immediately followed by integer T followed by T rows containing F space-separated columns
              </p>
              <p class="mb-3">
                The prices per square foot are approximately a polynomial function of the features, and you are tasked with using this relationship to predict the missing prices for some offices.

                The prices per square foot, are approximately a polynomial function of the features in the observation table. This polynomial always has an order less than 4

              </p>

              <div class="mb-4">
                <h6 class="font-weight-bold">Input Format</h6>
                <pre class="bg-white p-3 rounded">
First line: F N
Next N lines: F+1 space-separated values
Followed by: T
Next T lines: F space-separated values</pre>
              </div>

              <div class="mb-4">
                <h6 class="font-weight-bold">Constraints</h6>
                <ul class="list-unstyled">
                  <li>1 ≤ F ≤ 5</li>
                  <li>5 ≤ N ≤ 100</li>
                  <li>1 ≤ T ≤ 100</li>
                </ul>
              </div>

              <div class="mb-4">
                <h6 class="font-weight-bold">Output Format</h6>
                <pre class="bg-white p-3 rounded">T lines with predicted prices</pre>
              </div>
              <div class="row">
                <div class="col-md-6">
                  <h6 class="font-weight-bold">Sample Input</h6>
                  <pre class="bg-white p-3 rounded">2 7
0.44 0.68 511.14
0.99 0.23 717.1
...</pre>
                </div>
                <div class="col-md-6">
                  <h6 class="font-weight-bold">Sample Output</h6>
                  <pre class="bg-white p-3 rounded">180.38
907.07</pre>
                </div>
              </div>
            </div>
          </div>

          <!-- Ace Editor Component -->
          <div class="editor-container mb-4">
            <AceEditor
              :value="code"
            />
          </div>

          <!-- Buttons -->
          <div class="d-flex justify-content-end gap-2 mt-3">
            <button @click="submitCode" class="btn btn-success">Submit</button>
          </div>

          <!-- Test Case Results -->
          <div class="test-case-results mt-4" v-if="showResults">
            <h5 class="mb-3">Test Results <span class="badge badge-pill badge-light">{{ passedCount }}/{{ totalCases }}</span></h5>

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

          <!-- Console Output -->
          <div class="mt-4 d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Console</h5>
            <button
              v-if="consoleOutput.includes('Error')"
              @click="explainError"
              class="ai-button"
            >
              <img :src="StudentIcon" class="ai-icon me-2" alt="AI Assistant"/>
              Explain Error
            </button>
          </div>
          <div class="console-output p-3 bg-dark text-white rounded mt-2">
            {{ consoleOutput }}
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
      code: "# Write your Python code here...",
      consoleOutput: "",
      testCaseResults: [
        {
          status: 'passed',
          title: 'Basic Polynomial Fitting',
          description: 'Successfully predicted prices using degree 3 polynomial'
        },
        {
          status: 'failed',
          title: 'Edge Case Handling',
          description: 'Issue with features near boundary values (0 or 1)'
        },
        {
          status: 'passed',
          title: 'Input Parsing',
          description: 'Correctly parsed F features and N observations'
        },
        {
          status: 'failed',
          title: 'Prediction Accuracy',
          description: 'Predictions exceed 5% error margin on test cases'
        },
        {
          status: 'pending',
          title: 'Large Dataset Performance',
          description: 'Testing with maximum constraints (F=5, N=100, T=100)'
        }
      ]
        ,
      StudentIcon,
      showResults: false,
      showExplainButton: false,
      complexError: `Traceback (most recent call last):
  File "<string>", line 42, in <module>
  File "/usr/lib/python3.11/site-packages/sklearn/__init__.py", line 123, in <module>
    raise ImportError("dlopen(...) unable to load _arpack module: %s" % e)
ImportError: dlopen(/usr/lib/python3.11/site-packages/scipy/sparse/linalg/_eigen/arpack/_arpack.cpython-311-darwin.so, 0x0002): symbol not found in flat namespace (_gfortran_concat_string)
Fatal Python error: _Py_INCREF: can't increment refcount (value is 0x7f8b1d603d00)
Python runtime state: initialized
Current thread 0x0000000111d85e00 (most recent call first):
<no Python frame>
[1]    12345 abort      python main.py`
    };
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
    // When the user submits their code
async submitCode() {
  try {
    this.isLoading = true;
    this.results = null;

    const response = await api.post(
      `/programming_assignments/${this.assignmentId}/execute`,
      { code: this.code }
    );

    if (response.data.success) {
      this.results = response.data;
      this.testCaseResults = response.data.results.map(result => ({
        status: result.status,
        title: `Test Case ${result.test_case_id}`,
        description: result.status === 'passed'
          ? 'Output matched expected result'
          : 'Output did not match expected result'
      }));

      // Show success message
      this.showSuccessMessage = true;
    } else {
      // Handle error
      this.errorMessage = response.data.message || 'An error occurred';
    }
  } catch (error) {
    this.errorMessage = error.response?.data?.message || 'An error occurred';
  } finally {
    this.isLoading = false;
  }
},
    explainError() {
      // Simulate AI error explanation
      this.consoleOutput = `Simplified explanation:

      The code failed because of a missing dependency in the SciPy library.
      The specific error occurs when trying to import the ARPACK module, which is
      required for certain linear algebra operations. This typically happens when
      there's a mismatch between library versions or incomplete installation.

      Recommended fix:
      1. Update SciPy and NumPy packages
      2. Reinstall the scientific stack using:
         pip install --upgrade numpy scipy
      3. Verify installation with:
         python -c "import scipy.sparse.linalg"`;
    },
  }
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
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
  max-height: 300px;
  overflow-y: auto;
}

.sample-box {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
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
</style>
