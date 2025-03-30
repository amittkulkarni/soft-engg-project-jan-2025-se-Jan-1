<template>
  <div>
    <!-- Floating Chat Button with Notification Badge -->
    <button
      class="ai-button ask-me-btn"
      @click="toggleChat"
      :class=" { 'wiggle-animation': hasNewMessages }"
    >
      <img :src="StudentIcon" class="me-1" alt="AI Assistant"/>
      <span>Ask Kia</span>
      <span v-if="hasNewMessages" class="notification-badge">1</span>
    </button>

    <!-- Chat Window -->
    <transition name="slide-up">
      <div
        v-if="showChat"
        class="position-fixed border rounded shadow-lg chat-window"
      >
        <!-- Chat Header -->
        <div class="chat-header">
          <div class="d-flex align-items-center">
            <img :src="StudentIcon" alt="Kia Profile" class="profile-icon me-2"/>
            <div>
              <h6 class="mb-0 text-white">KIA - Your Virtual Assistant</h6>
              <small class="text-white-50" v-if="isTyping">typing...</small>
              <small class="text-white-50" v-else>Online</small>
            </div>
          </div>
          <div class="d-flex gap-2">
            <button
              type="button"
              class="btn btn-sm btn-teal"
              title="Download Chat"
              @click="downloadChat"
            >
              <i class="bi bi-download"></i>
            </button>
            <button
              type="button"
              class="btn btn-sm btn-outline-light"
              aria-label="Reset History"
              @click="resetHistory"
            >
              <i class="bi bi-arrow-counterclockwise"></i>
            </button>
            <button
              type="button"
              class="btn-close btn-close-white"
              aria-label="Close"
              @click="toggleChat"
            ></button>
          </div>
        </div>

        <!-- Chat Body -->
        <div
          v-if="!isMinimized"
          class="chat-body"
          ref="chatBody"
        >
          <!-- Welcome Message -->
          <div class="welcome-message" v-if="messages.length === 0">
            <h5>Welcome to KIA!</h5>
            <p>I can help you with course-related questions. Try asking about:</p>
            <div class="suggested-prompts">
              <button
                v-for="(prompt, i) in suggestedPrompts"
                :key="i"
                class="btn btn-sm btn-outline-secondary mb-2 me-2"
                @click="usePrompt(prompt)"
              >
                {{ prompt }}
              </button>
            </div>
          </div>

          <!-- Date Separator -->
          <div class="date-separator">
            <span>{{ today }}</span>
          </div>

          <!-- Messages -->
          <div
            v-for="(msg, index) in messages"
            :key="'msg-' + index"
            :class="[msg.sender === 'user' ? 'message-user' : 'message-kia']"
          >
            <!-- Kia's Messages with Icon-->
            <template v-if="msg.sender === 'kia'">
              <div class="message-container">
                <img
                  :src="StudentIcon"
                  alt="Kia Profile"
                  class="message-avatar"
                />
                <div class="message-content">
                  <div class="message-bubble kia-bubble">
                    <vue-markdown
                      :source="msg.text"
                      :options="markdownOptions"
                      class="markdown-content"
                    />
                  </div>
                  <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
                </div>
                <div class="message-actions">
                  <button class="action-btn" @click="copyMessage(msg.text)" title="Copy">
                    <i class="bi bi-clipboard"></i>
                  </button>
                </div>
              </div>
            </template>

            <!-- User's Messages -->
            <template v-else>
              <div class="message-container user-container">
                <div class="message-actions">
                  <button class="action-btn" @click="copyMessage(msg.text)" title="Copy">
                    <i class="bi bi-clipboard"></i>
                  </button>
                </div>
                <div class="message-content">
                  <div class="message-bubble user-bubble">
                    {{ msg.text }}
                  </div>
                  <div class="message-time">{{ formatTime(msg.timestamp) }}</div>
                </div>
              </div>
            </template>
          </div>

          <!-- Typing Indicator -->
          <div v-if="isTyping" class="message-container">
            <img
              :src="StudentIcon"
              alt="Kia Profile"
              class="message-avatar"
            />
            <div class="message-content">
              <div class="message-bubble kia-bubble typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Footer -->
        <div v-if="!isMinimized" class="chat-footer">
          <div class="input-group">
            <input
              type="text"
              v-model.trim="newMessage"
              placeholder="Ask Kia anything here..."
              @keyup.enter="sendMessage"
              class="form-control chat-input"
            />
            <button
              type="button"
              @click="sendMessage"
              class="btn send-btn"
              :disabled="!newMessage.trim()"
            >
              <i class="bi bi-send"></i>
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import StudentIcon from "@/assets/student.png";
import VueMarkdown from "vue-markdown-render";
import hljs from "highlight.js";
import "highlight.js/styles/atom-one-dark.css";
import api from "@/services/api.js"

export default {
  components: {
    VueMarkdown
  },
  data() {
    return {
      showChat: false,
      isTyping: false,
      newMessage: "",
      StudentIcon,
      hasNewMessages: false,
      userId: localStorage.getItem('user_id') || 1,
      messages: [],
      suggestedPrompts: [
        "What is Linear Regression?",
        "Explain decision trees",
        "How to handle missing data?",
        "Difference between classification and regression"
      ],
      markdownOptions: {
        breaks: true,
        html: true,
        highlight: function (code, lang) {
          if (lang && hljs.getLanguage(lang)) {
            return hljs.highlight(code, { language: lang }).value;
          }
          return hljs.highlightAuto(code).value;
        }
      }
    };
  },
  created() {
    this.loadChatHistory();
  },
  computed: {
    today() {
      return new Date().toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  },
  mounted() {
    this.highlightCode();
  },
  updated() {
    this.highlightCode();
  },
  methods: {
    toggleChat() {
      this.showChat = !this.showChat;
      if (this.showChat) {
        this.isMinimized = false;
        this.hasNewMessages = false;
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    resetHistory() {
      if (confirm("Are you sure you want to clear this conversation?")) {
        // Show loading indicator
        this.isTyping = true;

        // Call the reset chat history API
        api.post('/reset_chat_history', {
            user_id: this.userId
          })
          .then(response => {
            this.isTyping = false;

            if (response.data.success) {
              // Reset local messages with confirmation
              this.messages = [];
            } else {
              // Handle API error
              console.error('Failed to clear chat history:', response.data.message);
              this.messages.push({
                sender: "kia",
                text: "I couldn't clear our chat history. Please try again later.",
                timestamp: new Date()
              });
            }
          })
          .catch(error => {
            this.isTyping = false;
            console.error('API call failed:', error);

            // Add error message
            this.messages.push({
              sender: "kia",
              text: "I encountered an error while trying to clear our chat history. Please try again.",
              timestamp: new Date()
            });
          });
      }
    },
    sendMessage() {
      if (this.newMessage.trim() === "") return ;

      // Add user message to UI
      const userMessage = {
        sender: "user",
        text: this.newMessage,
        timestamp: new Date()
      };
      this.messages.push(userMessage);

      const userQuestion = this.newMessage;
      this.newMessage = "";

      // Update UI to show typing indicator
      this.isTyping = true;

      // Send message to backend
      api.post('/kia_chat', {
          user_id: this.userId,
          query: userQuestion
        })
        .then(response => {
          this.isTyping = false;

          if (response.data.success) {
            // Add AI response to UI
            const kiaMessage = {
              sender: "kia",
              text: response.data.response,
              timestamp: new Date()
            };
            this.messages.push(kiaMessage);

            if (!this.showChat) {
              this.hasNewMessages = true;
            }
          }
        })
        .catch(error => {
          this.isTyping = false;
          console.error('API call failed:', error);
        })
        .finally(() => {
          this.scrollToBottom();
        });
    },
    loadChatHistory() {
      api.get(`/chat_history/${this.userId}`)
        .then(response => {
          if (response.data.success) {
            this.messages = response.data.chat_history;
          } else {
            this.messages = [];
          }
        })
        .catch(error => {
          console.error('Failed to load chat history:', error);
          this.messages = [];
        });
    },
    scrollToBottom() {
      const chatBody = this.$refs.chatBody;
      if (chatBody) {
        chatBody.scrollTop = chatBody.scrollHeight;
      }
    },
    // Highlight code blocks dynamically after rendering
    highlightCode() {
      this.$nextTick(() => {
        document.querySelectorAll("pre code").forEach((block) => {
          hljs.highlightElement(block);
        });
      });
    },
    formatTime(timestamp) {
      if (!timestamp) return '';
      return new Date(timestamp).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    usePrompt(prompt) {
      this.newMessage = prompt;
      this.sendMessage();
    },
    copyMessage(text) {
      navigator.clipboard.writeText(text)
        .then(() => {
          alert('Message copied to clipboard!');
        })
        .catch(err => {
          console.error('Failed to copy message: ', err);
        });
    },
    downloadChat() {
      // Create chat transcript
      let transcript = "KIA Chat Transcript\n";
      transcript += "Date: " + new Date().toLocaleDateString() + "\n\n";

      this.messages.forEach(msg => {
        const time = this.formatTime(msg.timestamp);
        const sender = msg.sender === 'kia' ? 'KIA' : 'You';
        transcript += `[${time}] ${sender}: ${msg.text}\n\n`;
      });

      // Create download link
      const element = document.createElement('a');
      const file = new Blob([transcript], {type: 'text/plain'});
      element.href = URL.createObjectURL(file);
      element.download = 'kia-chat-transcript.txt';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }
  },
};
</script>

<style scoped>
/* Main Chat Container */
.chat-window {
  bottom: 20px;
  right: 20px;
  width: calc(100% - 40px);
  max-width: 600px;
  height: calc(100vh - 100px);
  max-height: 800px;
  min-height: 450px;
  overflow: hidden;
  z-index: 1050;
  display: flex;
  flex-direction: column;
  border-radius: 16px;
  border: none !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15) !important;
  background-color: #f8f9fa;
}
/* Code block styling */
.hljs {
  background-color: #282c34;
  color: #abb2bf;
}

.hljs-keyword {
  color: #c678dd;
}
.hljs-built_in {
  color: #e6c07b;
}
.hljs-string {
  color: #98c379;
}
.hljs-number {
  color: #d19a66;
}
.hljs-comment {
  color: #5c6370;
  font-style: italic;
}
.hljs-function {
  color: #61afef;
}
.hljs-variable {
  color: #e06c75;
}
.hljs-title {
  color: #61afef;
}
.hljs-params {
  color: #d19a66;
}
.hljs-operator {
  color: #56b6c2;
}

pre {
  background-color: #282c34;
  border-radius: 8px;
  padding: 16px;
}
.message-bubble .markdown-content {
  font-family: inherit !important;
}

.message-bubble .markdown-content * {
  font-family: inherit !important;
}

.message-bubble .markdown-content code,
.message-bubble .markdown-content pre code {
  font-family: 'Consolas', 'Monaco', monospace !important;
}

.markdown-content h1 {
  font-size: 1.8rem;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.markdown-content h2 {
  font-size: 1.5rem;
  margin-top: 0.8rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.markdown-content h3 {
  font-size: 1.2rem;
  margin-top: 0.6rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.markdown-content p {
  margin-bottom: 0.8rem;
}

/* Chat Header */
.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  background-color: #6c1b1b;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px 16px 0 0;
}

/* Chat Body */
.chat-body {
  flex-grow: 1;
  padding: 15px;
  overflow-y: auto;
  background-color: #f8f9fa;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%236c1b1b' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

/* Chat Footer */
.chat-footer {
  padding: 12px;
  background-color: #fff;
  border-top: 1px solid #e9ecef;
  border-radius: 0 0 16px 16px;
}

/* Message Containers */
.message-container {
  display: flex;
  margin-bottom: 16px;
  position: relative;
  align-items: flex-start;
}

.user-container {
  justify-content: flex-end;
}

/* Avatar */
.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 10px;
  border: 2px solid #6c1b1b;
  background-color: white;
}

/* Message Content */
.message-content {
  max-width: 85%;
}

.message-bubble {
  padding: 12px 16px;
  border-radius: 18px;
  position: relative;
  font-size: 0.95rem;
  line-height: 1.6;
  word-wrap: break-word;
  max-width: 100%;
}

.kia-bubble {
  background-color: white;
  color: #333;
  border-top-left-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.user-bubble {
  background-color: #6c1b1b;
  color: white;
  border-top-right-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* Message Time */
.message-time {
  font-size: 0.7rem;
  color: #6c757d;
  margin-top: 4px;
  opacity: 0.8;
}

/* Message Actions */
.message-actions {
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  flex-direction: column;
  margin: 0 8px;
}

.message-container:hover .message-actions {
  opacity: 1;
}

.action-btn {
  background: none;
  border: none;
  color: #6c757d;
  font-size: 0.8rem;
  cursor: pointer;
  padding: 4px;
}

.action-btn:hover {
  color: #495057;
}

/* Input Field */
.chat-input {
  border-radius: 20px;
  padding: 10px 16px;
  border: 1px solid #e9ecef;
  box-shadow: none;
  background-color: #f8f9fa;
  transition: all 0.2s;
}

.chat-input:focus {
  border-color: #6c1b1b;
  background-color: white;
  box-shadow: 0 0 0 0.2rem rgba(108, 27, 27, 0.15);
}

/* Send Button */
.send-btn {
  border-radius: 50%;
  width: 40px;
  height: 40px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 8px;
  background-color: #008080;
  border: none;
  color: white;
  transition: all 0.2s;
}

.send-btn:hover:not(:disabled) {
  background-color: #006666;
  transform: scale(1.05);
}

.send-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

/* Enhanced Floating Button */
.ask-me-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: linear-gradient(135deg, #6c1b1b 0%, #8a3030 100%);
  color: white;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(108, 27, 27, 0.3);
  border-radius: 50px;
  padding: 12px 22px;
  border: none;
  font-weight: 500;
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.ask-me-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(108, 27, 27, 0.4);
  background: linear-gradient(135deg, #7c2b2b 0%, #9a4040 100%);
}

.ask-me-btn img {
  width: 26px;
  height: 26px;
  margin-right: 8px;
}

/* Notification Badge */
.notification-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: #008080;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  font-size: 0.7rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Animations */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform .3s ease-in-out, opacity .3s ease-in-out;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(30px);
  opacity: 0;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  align-items: center;
  padding: 10px 20px;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  margin: 0 1px;
  background-color: #6c1b1b;
  display: block;
  border-radius: 50%;
  opacity: 0.4;
  animation: typing 1s infinite;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0% {
    transform: translateY(0px);
    opacity: 0.4;
  }
  50% {
    transform: translateY(-5px);
    opacity: 0.8;
  }
  100% {
    transform: translateY(0px);
    opacity: 0.4;
  }
}

/* Date Separator */
.date-separator {
  text-align: center;
  margin: 20px 0;
  position: relative;
}

.date-separator:before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  width: 100%;
  height: 1px;
  background: #e9ecef;
  z-index: 1;
}

.date-separator span {
  background: #f8f9fa;
  padding: 0 10px;
  font-size: 0.8rem;
  color: #6c757d;
  position: relative;
  z-index: 2;
}

/* Welcome Message */
.welcome-message {
  text-align: center;
  padding: 20px;
  margin-bottom: 20px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.welcome-message h5 {
  color: #6c1b1b;
  margin-bottom: 10px;
}

.suggested-prompts {
  margin-top: 15px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
}

/* Button for teal color */
.btn-teal {
  background-color: #008080;
  color: white;
  border: none;
}

.btn-teal:hover {
  background-color: #006666;
}

/* Wiggle animation for new messages */
@keyframes wiggle {
  0% {
    transform: rotate(0deg);
  }
  15% {
    transform: rotate(-5deg);
  }
  30% {
    transform: rotate(5deg);
  }
  45% {
    transform: rotate(-4deg);
  }
  60% {
    transform: rotate(4deg);
  }
  75% {
    transform: rotate(-2deg);
  }
  85% {
    transform: rotate(2deg);
  }
  92% {
    transform: rotate(-1deg);
  }
  100% {
    transform: rotate(0deg);
  }
}

.wiggle-animation {
  animation: wiggle 0.8s ease-in-out;
  animation-iteration-count: infinite;
}

@media (min-width: 768px) {
  .chat-window {
    max-width: 600px; /* Even larger on desktop */
    max-height: 750px;
  }
}

@media (min-width: 1200px) {
  .chat-window {
    max-width: 650px; /* Maximum size on large screens */
  }
}

/* Profile icon in header */
.profile-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid rgba(255, 255, 255, 0.6);
}
</style>