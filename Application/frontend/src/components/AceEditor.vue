<template>
  <v-ace-editor
    v-model:value="internalValue"
    lang="python"
    theme="monokai"
    placeholder="Write your Python code here..."
    style="height: 570px; width: 100%;"
    :options="editorOptions"
  />
</template>

<script>
import { VAceEditor } from "vue3-ace-editor";
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-monokai";

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
  computed: {
    internalValue: {
      get() {
        return this.modelValue;
      },
      set(value) {
        this.$emit("update:modelValue", value);
      }
    }
  },
  data() {
    return {
      editorOptions: {
        fontSize: "20px",
        useWorker: false,
        tabSize: 4,
        wrap: true,
      },
    };
  }
};
</script>
