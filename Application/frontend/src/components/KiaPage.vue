<template>
  <div>
    <AppNavbar />
    <div class="dashboard-layout">
      <AppSidebar />

      <div class="main-content">
        <div class="content-wrapper">
          <div class="welcome-section text-center mb-4">
            <div class="avatar-container mb-3">
              <img :src="StudentIcon" class="avatar-img" alt="KIA Avatar" />
            </div>
            <h1 class="welcome-heading">Hello, Amit!</h1>
            <div class="subtitle-container">
              <p class="lead mb-1">I am KIA, your virtual companion at SEEK.</p>
              <p class="text-muted">Select an option below or chat with me anytime.</p>
            </div>
          </div>

          <div class="cards-container">
            <div class="feature-card" @click.stop="showContent('week-summary')" :class="{ active: activeContent === 'week-summary' }">
              <div class="card-icon-wrapper">
                <i class="bi bi-calendar-week"></i>
              </div>
              <div class="card-content">
                <h3>Weekly Summaries</h3>
                <p>Generate condensed notes for any course week</p>
              </div>
            </div>

            <div class="feature-card" @click.stop="showContent('generate-notes')" :class="{ active: activeContent === 'generate-notes' }">
              <div class="card-icon-wrapper">
                <i class="bi bi-journal-text"></i>
              </div>
              <div class="card-content">
                <h3>Topic Notes</h3>
                <p>Create focused notes on specific course topics</p>
              </div>
            </div>
          </div>
          <transition name="fade" mode="out-in">
          <div v-if="activeContent" class="dynamic-content-wrapper">
          <!-- Generate Notes Section -->
          <div v-if="activeContent === 'generate-notes'" class="dynamic-content">
            <div class="section-header mb-4">
              <h2>Generate Topic-Specific Notes</h2>
              <p class="text-muted">Search for any course topic to generate comprehensive notes</p>
            </div>

            <div class="search-container position-relative mb-4">
              <div class="input-group">
                <span class="input-group-text bg-white">
                  <i class="bi bi-search"></i>
                </span>
                <input
                  type="text"
                  v-model="searchQuery"
                  @input="fetchSuggestions"
                  placeholder="Search topics (e.g., Regression, Machine Learning)"
                  class="form-control"
                />
                <button class="btn btn-dark" @click="generateNotes" :disabled="!selectedTopic">
                  <i class="bi bi-magic me-1"></i> Generate
                </button>
              </div>

              <transition name="fade">
                <ul v-if="suggestions.length > 0" class="suggestions-list shadow-sm">
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

            <!-- Notes Generation Status -->
            <div v-if="isGenerating" class="generation-status text-center p-4">
              <div class="spinner-grow text-primary mb-3" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p>Generating comprehensive notes for <strong>{{ selectedTopic }}</strong>...</p>
            </div>
          </div>

          <!-- Week Summary Section with improved UI -->
          <div v-if="activeContent === 'week-summary'" class="dynamic-content">
            <div class="section-header mb-4">
              <h2>Weekly Learning Summaries</h2>
              <p class="text-muted">Generate comprehensive notes for any week of your course</p>
            </div>

            <div class="week-selector">
              <div class="weeks-grid">
                <div
                  v-for="week in weeks"
                  :key="'Week ' + week"
                  @click="selectWeek('Week ' + week)"
                  :class="['week-item', selectedWeek === 'Week ' + week ? 'active' : '']"
                >
                  {{ week }}
                </div>
              </div>

              <button @click="generateWeekSummary" class="btn btn-dark mt-3 w-100">
                <i class="bi bi-file-earmark-text me-1"></i>
                Generate {{ selectedWeek }} Summary
              </button>
            </div>
          </div>
          </div>
          </transition>

          <!-- Enhanced Markdown Output -->
          <div v-if="currentContent" class="markdown-output-container mt-4">
            <div class="markdown-header d-flex justify-content-between align-items-center">
              <h4>{{ activeContent === 'generate-notes' ? selectedTopic : selectedWeek }} Notes</h4>
              <div class="actions">
                <button @click="copyContent" class="btn btn-sm btn-light me-2">
                  <i class="bi bi-clipboard"></i> Copy
                </button>
                <button @click="downloadPDF" class="btn btn-sm btn-light">
                  <i class="bi bi-download"></i> Download PDF
                </button>
              </div>
            </div>
            <div class="markdown-content">
              <vue-markdown
                :source="currentContent"
                :options="{
                  highlight: function (code, lang) {
                  // This will handle the syntax highlighting based on language
                  return require('highlight.js').highlightAuto(code, [lang]).value;
                  }
                }"/>
            </div>
          </div>
        </div>
        <ChatWindow />
      </div>
    </div>
  </div>
</template>

<script>
import AppNavbar from "@/components/AppNavbar.vue";
import AppSidebar from "@/components/AppSidebar.vue";
import ChatWindow from "@/components/ChatWindow.vue";
import StudentIcon from "@/assets/student.png";
import VueMarkdown from "vue-markdown-render";
import 'highlight.js/styles/github.css';
import { jsPDF } from "jspdf";

export default {
  name: "KiaPage",
  data() {
    return {
      StudentIcon,
      activeContent: null,
      searchQuery: "",
      suggestions: [],
      isGenerating: false,
      generatedNotes: "",
      weeks: Array.from({ length: 12 }, (_, i) => i + 1),
      selectedWeek: "Week 1",
      selectedTopic: "",
      generatedSummary: "",
    };
  },
  components: {
    AppSidebar,
    AppNavbar,
    ChatWindow,
    VueMarkdown
  },
  computed: {
    currentContent() {
      if (this.activeContent === 'generate-notes') return this.generatedNotes;
      if (this.activeContent === 'week-summary') return this.generatedSummary;
      return '';
    }
  },
  methods: {
    selectWeek(week) {
      this.selectedWeek = week;
    },
    showContent(content) {
      this.activeContent = content;
      this.generatedNotes = "";
      this.generatedSummary = "";
    },
    fetchSuggestions() {
      const topics = ["Regression", "Linear Regression", "Logistic Regression", "Auto-regressive model"];
      this.suggestions = topics.filter(topic =>
        topic.toLowerCase().includes(this.searchQuery.toLowerCase())
      );
    },
    selectSuggestion(suggestion) {
      this.selectedTopic = suggestion;
      this.searchQuery = suggestion;
      this.suggestions = [];
    },
    copyContent() {
      navigator.clipboard.writeText(this.currentContent)
        .then(() => {
          // You could add a toast notification here
          alert('Content copied to clipboard!');
        })
        .catch(err => {
          console.error('Failed to copy content: ', err);
        });
    },
    downloadPDF() {
      const doc = new jsPDF();
      const content = this.activeContent === "generate-notes" ? this.generatedNotes : this.generatedSummary;
      doc.text(content, 10, 10);
      const fileName = this.activeContent === "generate-notes"
        ? `Notes_${this.searchQuery || "Topic"}.pdf`
        : `Week_${this.selectedWeek.replace("Week ", "")}_Summary.pdf`;
      doc.save(fileName);
    },
    async generateNotes() {
      this.generatedNotes = "";
      this.isGenerating = true;
      setTimeout(() => {
        this.isGenerating = false;
      this.generatedNotes = `
# Linear Regression: Fundamentals and Implementation

## Introduction to Linear Regression

Linear Regression is a fundamental supervised machine learning algorithm used for predicting a continuous target variable based on one or more predictor variables. It works by finding the best-fitting straight line (or hyperplane in higher dimensions) through the data points.

## Simple Linear Regression Implementation

Let's start with implementing simple linear regression using Python's scikit-learn:

\`\`\`python
# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Generate sample data
np.random.seed(42)
X = 2 * np.random.rand(100, 1)
y = 4 + 3 * X + np.random.randn(100, 1)

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Print model parameters
print(f"Intercept: {model.intercept_[0]:.4f}")
print(f"Coefficient: {model.coef_[0][0]:.4f}")

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"Mean Squared Error: {mse:.4f}")
print(f"R² Score: {r2:.4f}")
\`\`\`

## Implementing Linear Regression from Scratch

To better understand the algorithm, let's implement linear regression using only NumPy:

\`\`\`python
class LinearRegressionFromScratch:
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.weights = None
        self.bias = None

    def fit(self, X, y):
        # Initialize parameters
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0

        # Gradient descent
        for _ in range(self.n_iterations):
            y_predicted = np.dot(X, self.weights) + self.bias

            # Compute gradients
            dw = (1/n_samples) * np.dot(X.T, (y_predicted - y))
            db = (1/n_samples) * np.sum(y_predicted - y)

            # Update parameters
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

        return self

    def predict(self, X):
        return np.dot(X, self.weights) + self.bias
\`\`\`

## Visualizing Linear Regression

Visualization helps understand how the model fits the data:

\`\`\`python
# Plot the data and regression line
plt.figure(figsize=(10, 6))
plt.scatter(X_test, y_test, color='blue', label='Test data')
plt.plot(X_test, y_pred, color='red', linewidth=2, label='Regression line')
plt.title('Linear Regression Model')
plt.xlabel('X')
plt.ylabel('y')
plt.legend()
plt.grid(True)
plt.show()
\`\`\`

## Multiple Linear Regression

When dealing with multiple features, the implementation is similar but works in higher dimensions:

\`\`\`python
# Generate multi-feature dataset
np.random.seed(42)
X_multi = np.random.rand(100, 3)  # 3 features
y_multi = 4 + np.dot(X_multi, np.array([2, 3, 4])) + np.random.randn(100)

# Split the data
X_train_multi, X_test_multi, y_train_multi, y_test_multi = train_test_split(
    X_multi, y_multi, test_size=0.2, random_state=42)

# Create and train the model
multi_model = LinearRegression()
multi_model.fit(X_train_multi, y_train_multi)

# Print model parameters
print(f"Intercept: {multi_model.intercept_:.4f}")
print(f"Coefficients: {multi_model.coef_}")

# Make predictions and evaluate
y_pred_multi = multi_model.predict(X_test_multi)
mse_multi = mean_squared_error(y_test_multi, y_pred_multi)
r2_multi = r2_score(y_test_multi, y_pred_multi)
print(f"MSE: {mse_multi:.4f}, R²: {r2_multi:.4f}")
\`\`\`

## Regularization Techniques

Regularization helps prevent overfitting by adding a penalty term to the loss function:

### Ridge Regression (L2 Regularization)

\`\`\`python
from sklearn.linear_model import Ridge

# Create and train Ridge model
ridge = Ridge(alpha=1.0)  # alpha controls regularization strength
ridge.fit(X_train_multi, y_train_multi)

# Evaluate
y_pred_ridge = ridge.predict(X_test_multi)
print(f"Ridge R²: {r2_score(y_test_multi, y_pred_ridge):.4f}")
\`\`\`

### Lasso Regression (L1 Regularization)

\`\`\`python
from sklearn.linear_model import Lasso

# Create and train Lasso model
lasso = Lasso(alpha=0.1)
lasso.fit(X_train_multi, y_train_multi)

# Evaluate
y_pred_lasso = lasso.predict(X_test_multi)
print(f"Lasso R²: {r2_score(y_test_multi, y_pred_lasso):.4f}")
print(f"Lasso Coefficients: {lasso.coef_}")  # Notice some might be exactly 0
\`\`\`

## Assumptions of Linear Regression

For linear regression to provide reliable results, several assumptions should be met:

1. **Linearity**: The relationship between features and target is linear
2. **Independence**: Observations are independent of each other
3. **Homoscedasticity**: Residuals have constant variance at every level
4. **Normality**: Residuals are normally distributed
5. **No multicollinearity**: Independent variables are not highly correlated

## Testing Assumptions with Code

\`\`\`python
# Checking residuals
residuals = y_test - y_pred

# Plot residuals
plt.figure(figsize=(10, 6))
plt.scatter(y_pred, residuals)
plt.axhline(y=0, color='r', linestyle='-')
plt.title('Residuals vs Predicted Values')
plt.xlabel('Predicted values')
plt.ylabel('Residuals')
plt.grid(True)
plt.show()

# Checking normality of residuals with Q-Q plot
import scipy.stats as stats
plt.figure(figsize=(10, 6))
stats.probplot(residuals.flatten(), dist="norm", plot=plt)
plt.title('Q-Q Plot of Residuals')
plt.grid(True)
plt.show()
\`\`\`

By understanding both the theory and implementation of linear regression, you'll have a solid foundation for more complex machine learning algorithms.
`;
      });
    },
    generateWeekSummary() {
      this.generatedSummary = "";
      this.isGenerating = true;
      setTimeout(() => {
            this.isGenerating = false;
            this.generatedSummary = `
# Summary of ${this.selectedWeek}


Lorem ipsum dolor sit amet consectetur adipiscing elit, non porttitor nec dictum sodales posuere, natoque orci class habitant ultricies semper. In condimentum vel blandit ante dis phasellus nunc vivamus aptent tempor metus, eget nibh congue morbi eu neque nascetur gravida aenean interdum. Risus convallis hac suscipit per ligula donec laoreet curabitur lectus aptent tellus proin vel dignissim gravida habitasse tincidunt maecenas odio rutrum, non torquent neque porta ullamcorper magna faucibus velit taciti est etiam sapien consequat interdum eros quam nullam fusce bibendum.

Sodales leo morbi auctor rhoncus purus arcu torquent dis, natoque quis cursus tortor lacinia eget tellus primis fusce, vivamus porttitor lacus senectus integer curabitur tempus. Netus platea consequat eu posuere velit porttitor suspendisse at proin, bibendum nisi dapibus pellentesque quam luctus semper mi, donec in hendrerit primis nisl sed porta pharetra.

## Posuere felis non scelerisque scelerisque

- Potenti nam id ridiculus, quam mollis, convallis accumsan.

- Magnis morbi aliquet nisl nullam, ante faucibus eget.

- Ad hendrerit praesent rutrum fames, laoreet hac purus.

- Nulla nisl massa eu iaculis, enim ac a.

Auctor nascetur condimentum sollicitudin laoreet proin faucibus nostra imperdiet, nunc metus aptent hac varius arcu cum ullamcorper, eget magna placerat ligula curabitur vulputate odio.

Netus dignissim placerat cum leo non class iaculis facilisi, habitasse sapien rutrum habitant tristique pellentesque curabitur cubilia, at nullam donec tempus metus nibh tempor. Pulvinar condimentum sociis vivamus egestas erat luctus sodales, convallis ad litora urna porttitor dignissim, netus cursus justo cubilia proin hendrerit. Tortor nam interdum montes ultrices parturient sapien sociis gravida, commodo conubia sem consequat tincidunt auctor taciti at, dignissim curabitur luctus congue aenean neque donec. `;
      }, 1500);
    },
  }
};
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  height: 100vh;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  padding: 2rem;
  overflow-y: auto;
}

.cards-container {
  display: flex;
  gap: 2rem;
  justify-content: center;
}

.dynamic-content {
  max-width: 800px;
  margin: 0 auto;
}

/* Update your existing .markdown-output-container styles */
.markdown-output-container {
  width: 100%; /* Makes it full width of parent */
  max-width: 1200px; /* Match this to your other divs' max-width */
  margin: 2rem auto;
  border: 1px solid #e2e2e2;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  background-color: white;
  overflow: hidden;
}

/* Enhance code block styling */
.markdown-content pre {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
  margin: 1.2rem 0;
  width: 100%; /* Ensure code blocks take full width */
}

.markdown-header {
  background-color: #6c1b1b;
  color: white;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e2e2e2;
}

.markdown-content {
  padding: 1.5rem;
  font-size: 1.05rem;
  line-height: 1.7;
  color: #343a40;
  max-height: 600px;
  overflow-y: auto;
}

/* Typography enhancements */
.markdown-content h1 {
  font-size: 1.8rem;
  margin-top: 0;
  color: #6c1b1b;
  border-bottom: 2px solid #f0e5e5;
  padding-bottom: 0.5rem;
  margin-bottom: 1.2rem;
}

.markdown-content h2 {
  font-size: 1.5rem;
  color: #6c1b1b;
  margin-top: 1.5rem;
  border-bottom: 1px solid #f0e5e5;
  padding-bottom: 0.4rem;
  margin-bottom: 1rem;
}

.markdown-content h3 {
  font-size: 1.25rem;
  color: #333;
  margin-top: 1.2rem;
  margin-bottom: 0.8rem;
}

.markdown-content p {
  margin-bottom: 1rem;
}

.markdown-content ul,
.markdown-content ol {
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

.markdown-content li {
  margin-bottom: 0.5rem;
}

/* Code block formatting */
.markdown-content pre {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
  margin: 1.2rem 0;
  position: relative;
}

.markdown-content pre::before {
  content: 'Python';
  position: absolute;
  top: 0;
  right: 0;
  background: #e9ecef;
  padding: 2px 8px;
  font-size: 0.75rem;
  border-radius: 0 6px 0 6px;
  color: #495057;
}

.markdown-content code {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 0.9rem;
  color: #212529;
  background-color: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
}

.markdown-content pre code {
  padding: 0;
  background-color: transparent;
  color: #212529;
  display: block;
  line-height: 1.5;
}

/* Inline elements */
.markdown-content strong {
  color: #495057;
  font-weight: 600;
}

.markdown-content a {
  color: #6c1b1b;
  text-decoration: none;
  border-bottom: 1px solid #6c1b1b33;
}

.markdown-content a:hover {
  text-decoration: none;
  border-bottom: 1px solid #6c1b1b;
}

/* Tables */
.markdown-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
}

.markdown-content th {
  background-color: #f8f9fa;
  font-weight: 600;
  text-align: left;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
}

.markdown-content td {
  padding: 0.75rem;
  border: 1px solid #dee2e6;
}

.markdown-content tr:nth-child(even) {
  background-color: #f8f9fa;
}
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f8f9fa;
}

.dynamic-content-wrapper {
  width: 100%;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  margin-bottom: 30px;
}

.btn-light {
  background-color: #f8f9fa;
  color: #333;
  border: 1px solid #dee2e6;
}

.btn-light:hover {
  background-color: #e2e6ea;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  padding: 2.5rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

/* Welcome Section */
.welcome-section {
  padding: 2rem;
  margin-bottom: 3rem;
  background: linear-gradient(to right, #6c1b1b11, #6c1b1b22);
  border-radius: 12px;
}

.avatar-container {
  display: inline-block;
  background-color: #6c1b1b;
  padding: 1.2rem;
  border-radius: 50%;
  box-shadow: 0 8px 20px rgba(108, 27, 27, 0.2);
}

.avatar-img {
  height: 50px;
  width: 50px;
}

.welcome-heading {
  font-size: 2.2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #6c1b1b;
}

.subtitle-container {
  max-width: 500px;
  margin: 0 auto;
}

/* Feature Cards */
.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.feature-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 8px rgba(0,0,0,0.05);
  border-left: 5px solid transparent;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.feature-card.active {
  border-left: 5px solid #6c1b1b;
  background-color: #fcf8f8;
}

.card-icon-wrapper {
  background-color: #f0e5e5;
  color: #6c1b1b;
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
}

.card-icon-wrapper i {
  font-size: 1.8rem;
}

.card-content h3 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
  color: #343a40;
}

.card-content p {
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0;
}

/* Content Panel */
.content-panel {
  background: white;
  border-radius: 12px;
  margin-bottom: 2rem;
  border-top: 4px solid #6c1b1b;
}

/* Form Elements */
.form-control, .form-select {
  border-radius: 8px;
  padding: 0.6rem 1rem;
  border: 1px solid #dee2e6;
  transition: all 0.2s;
}

.form-control:focus, .form-select:focus {
  border-color: #6c1b1b;
  box-shadow: 0 0 0 0.25rem rgba(108, 27, 27, 0.25);
}

.btn {
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-dark {
  background-color: #6c1b1b;
  border-color: #6c1b1b;
}

.btn-dark:hover {
  background-color: #5a1717;
  border-color: #5a1717;
}

.btn-success {
  background-color: #28a745;
  border-color: #28a745;
}

.markdown-output h1,
.markdown-output h2 {
  color: #6c1b1b;
  border-bottom: 1px solid #dee2e6;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

/* Animations */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* Add these missing styles for the week selector */
.week-selector {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.weeks-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 15px;
}

/* Make week items more visible with these enhancements */
.week-item {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-weight: 500;
}


/* Responsive Adjustments */
@media (max-width: 768px) {
  .content-wrapper {
    padding: 1.5rem;
  }

  .cards-container {
    grid-template-columns: 1fr;
  }

  .welcome-heading {
    font-size: 1.8rem;
  }
}
</style>
