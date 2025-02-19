<template>
  <div>
    <!-- Floating Chat Button -->
    <button
      class="ai-button ask-me-btn"
      @click="toggleChat"
    >
      <img :src="StudentIcon" class="me-1" alt="AI Assistant" /> Ask Kia
    </button>

    <!-- Chat Window -->
    <transition name="slide-up">
      <div
        v-if="showChat"
        class="position-fixed border rounded shadow-lg chat-window"
        style="
          bottom: 20px;
          right: 20px;
          width: calc(100% - 40px);
          max-width: 600px;
          height: 900px;
          overflow: hidden;
          z-index: 1050;
        "
      >
        <!-- Chat Header -->
        <div
          class="d-flex align-items-center justify-content-between p-3 border-bottom"
          style="background-color: #707070;"
        >
          <h6 class="mb-0 text-white">KIA - Your Virtual Assistant</h6>
          <div class="d-flex gap-3">
          <button
            type="button"
            class="btn btn-outline-light"
            aria-label="Reset History"
            @click="resetHistory"
          >Reset Chat</button>
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
          class="p-3 overflow-auto"
          style="
            max-height: calc(100% - 80px);
          "
          ref="chatBody"
        >
          <!-- Messages -->
          <div
            v-for="(msg, index) in messages"
            :key="'msg-' + index"
            :class="[msg.sender === 'user' ? 'text-end' : 'text-start']"
            class="mb-3"
          >
            <!-- Kia's Messages with Icon-->
           <template v-if="msg.sender === 'kia'">
             <div class="d-flex align-items-start">
               <img
                 :src="StudentIcon"
                 alt="Kia Profile"
                 class="profile-icon me-2"
               />
               <span
                 class="bg-white text-dark d-inline-block rounded px-3 py-2 shadow-sm"
                 style="
                   max-width: 80%;
                   word-wrap: break-word;
                   font-size: 0.9rem;
                 "
               >
                 {{ msg.text }}
               </span>
             </div>
           </template>
           <!-- User's Messages -->
           <template v-else>
             <div class="text-end">
               <span
                 class="text-white d-inline-block rounded px-3 py-2 shadow-sm"
                 style="
                   background-color: #707070;
                   max-width: 80%;
                   word-wrap: break-word;
                   font-size: 0.9rem;
                 "
               >
                 {{ msg.text }}
               </span>
             </div>
           </template>
          </div>
        </div>

        <!-- Chat Footer (Fixed at the Bottom) -->
        <div
          class="input-group p-2 border-top position-absolute w-100"
          style="
            background-color: #f2f3f5;
            bottom: 0;
            left: 0;
            right: 0;
          "
        >
          <input
            type="text"
            v-model.trim="newMessage"
            placeholder="Ask Kia anything here..."
            @keyup.enter="sendMessage"
            class="form-control bg-light border-0 text-dark rounded-pill px-3 shadow-sm"
          />
          <button
            type="button"
            @click="sendMessage"
            class="btn btn-secondary rounded-circle ms-2 px-3 py-2 d-flex align-items-center justify-content-center"
          >
            <i class="bi bi-send text-white"></i>
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import StudentIcon from "@/assets/student.png";
export default {
  data() {
    return {
      showChat: false,
      newMessage: "",
      StudentIcon,
      messages: [
        { sender: "kia", text: "Hi! How can I assist you today?" },
        { sender: "user", text: "Just talk some placeholder conversation. Suggest me models for regression." },
        { sender: "kia", text: "Try models like Lasso Regression or Logistic Regression." },
        { sender: "user", text: "I think Logistic Regression is a classification model." },
        { sender: "kia", text: "Oopsies! I got confused. Yes you are right, it is a classification model." },
        { sender: "user", text: "Hah." },
      ],
    };
  },
  methods: {
    toggleChat() {
      this.showChat = !this.showChat;
    },
    resetHistory() {
      this.messages = [];
    },
    sendMessage() {
      if (this.newMessage.trim() !== "") {
        this.messages.push({ sender: "user", text: this.newMessage });
        this.newMessage = "";

        // Simulate Kia's response
        setTimeout(() => {
          this.messages.push({
            sender: "kia",
            text: "Let me think about that... Here's what I found!",
          });

          // Scroll to bottom of chat body
          this.$nextTick(() => {
            const chatBody = this.$refs.chatBody;
            chatBody.scrollTop = chatBody.scrollHeight;
          });
        }, 1000);
      }
    },
  },
};
</script>

<style scoped>
/* Floating Button */

.ask-me-btn {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: linear-gradient(135deg, #e0e0e0 0%, #e8e8ea 100%);
  border: 1px solid #e0e0e0; /* Adding a thin border */
  color: #606060;
  z-index: 1000;
}

.ask-me-btn:hover {
  background-color: #333333; /* Slightly lighter black on hover */
}

.bg-light {
  background-color: #f5f5f5;
}

/* StudentIcon styling for circular profile image */
.profile-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
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

.chat-window::-webkit-scrollbar {
  width: 6px;
}
/* Chat Window Background using off-white (gray white) theme */
.chat-window {
  background-color: #F2F3F5;
}

.chat-window::-webkit-scrollbar-thumb {
  background-color:#dcdcdc;
}

.chat-window::-webkit-scrollbar-track {
  background-color: #f5f5f5;
}

/* Smooth Slide-Up Animation */
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform .3s ease-in-out, opacity .3s ease-in-out;
}

.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(100%);
}
</style>