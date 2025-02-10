<template>
  <v-ace-editor
    :value="content"
    lang="python"
    theme="monokai"
    placeholder="Write your Python code here..."
    style="height: 570px; width: 100%;"
    :options="editorOptions"
  />
</template>

<script>
import { VAceEditor } from "vue3-ace-editor";
import "ace-builds/src-noconflict/mode-python"; // Import Python mode
import "ace-builds/src-noconflict/theme-monokai"; // Import Monokai theme

export default {
  name: "AceEditor",
  components: {
    VAceEditor,
  },
  props: {
    modelValue: {
      type: String,
      required: true,
    },
  },
  emits: ["update:modelValue"],
  data() {
    return {
      content: this.modelValue,
      editorOptions: {
        fontSize: "20px",
        useWorker: false, // Disable syntax checking worker (optional)
        tabSize: 4,
        wrap: true,
      },
    };
  },
  watch: {
    modelValue(newValue) {
      if (newValue !== this.content) {
        this.content = newValue;
      }
    },
    content(newValue) {
      this.$emit("update:modelValue", newValue);
    },
  },
};
</script>

<style scoped>
/* Optional styling */
</style>
