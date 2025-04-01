<template>
  <div class="markdown-content" v-html="renderedContent"></div>
</template>

<script>
import { marked } from 'marked';
import hljs from 'highlight.js';
import python from 'highlight.js/lib/languages/python';
import 'highlight.js/styles/github.css';
import katex from 'katex';
import 'katex/dist/katex.min.css';

hljs.registerLanguage('python', python);

export default {
  props: {
    content: {
      type: String,
      required: true
    }
  },
  mounted() {
    this.$nextTick(() => {
      this.highlightCodeBlocks();
    });
  },
  updated() {
    this.$nextTick(() => {
      this.highlightCodeBlocks();
    });
  },
  methods: {
    highlightCodeBlocks() {
      const codeBlocks = this.$el.querySelectorAll('pre code');
      codeBlocks.forEach(block => {
        hljs.highlightElement(block);
      });
    }
  },
  computed: {
    renderedContent() {
      // Ensure content is a string
      const contentStr = typeof this.content === 'object'
        ? JSON.stringify(this.content)
        : String(this.content);

      // Configure marked with Python syntax highlighting
      marked.setOptions({
        gfm: true,
        breaks: true
      });

      // First process LaTeX expressions
      let processedContent = contentStr;

      // Process display math - fixed regex pattern
      processedContent = processedContent.replace(/\$\$([\s\S]*?)\$\$/g,
        (match, formula) => {
          try {
            return katex.renderToString(formula, {
              displayMode: true,
              throwOnError: false,
              output: 'html'
            });
          } catch (error) {
            console.error('LaTeX display math error:', error);
            return `<span class="latex-error">${match}</span>`;
          }
        });

      // Also handle \[ \] syntax for display math
      processedContent = processedContent.replace(/\\\[([\s\S]*?)\\\]/g,
        (match, formula) => {
          try {
            return katex.renderToString(formula, {
              displayMode: true,
              throwOnError: false,
              output: 'html'
            });
          } catch (error) {
            console.error('LaTeX display math error:', error);
            return `<span class="latex-error">${match}</span>`;
          }
        });

      // Handle inline math with proper regex - careful with $ delimiters
      processedContent = processedContent.replace(/\$([^$\n]+?)\$/g,
        (match, formula) => {
          try {
            return katex.renderToString(formula, {
              displayMode: false,
              throwOnError: false,
              output: 'html'
            });
          } catch (error) {
            console.error('LaTeX inline math error:', error);
            return `<span class="latex-error">${match}</span>`;
          }
        });

      // Handle \( \) syntax for inline math
      processedContent = processedContent.replace(/\\\(([\s\S]*?)\\\)/g,
        (match, formula) => {
          try {
            return katex.renderToString(formula, {
              displayMode: false,
              throwOnError: false,
              output: 'html'
            });
          } catch (error) {
            console.error('LaTeX inline math error:', error);
            return `<span class="latex-error">${match}</span>`;
          }
        });

      // Parse markdown AFTER LaTeX processing
      return marked(processedContent);
    }
  },
}
</script>

<style>
/* Add proper spacing for elements */
.markdown-content h1, .markdown-content h2, .markdown-content h3 {
  margin-top: 1.8rem;
  margin-bottom: 1.2rem;
}

/* Add error styling */
.latex-error {
  color: #cc0000;
  background-color: #ffeeee;
  border: 1px solid #cc0000;
  padding: 2px 4px;
  border-radius: 3px;
}

/* Fix LaTeX display */
.markdown-content {
  overflow-x: visible;
  width: 100%;
}

.katex-display {
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0.5em 0;
  max-width: 100%;
}

.katex {
  display: inline-block;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0 0.2em;
  vertical-align: middle;
}

/* For deeper nested elements that might still be misaligned */
.katex .katex-mathml {
  vertical-align: middle;
}

/* Adjust specific KaTeX inner elements if needed */
.katex .mord {
  vertical-align: baseline;
}

/* Code block formatting */
.markdown-content pre {
  background-color: #f8f9fa; /* Light background */
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto;
  margin: 1.2rem 0;
}

.markdown-content pre code {
  color: #24292e; /* Dark text color for light background */
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace;
}

.markdown-content table {
  margin: 1.5rem 0;
  border-collapse: separate;
  border-spacing: 0;
  width: 100%;
}

.markdown-content th, .markdown-content td {
  padding: 0.8rem 1rem;
  border: 1px solid #dee2e6;
}
</style>
