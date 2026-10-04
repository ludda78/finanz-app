<template>
  <div class="info-page" v-html="infoHtml"></div>
</template>

<script>
import { marked } from 'marked'

export default {
  name: 'InfoPage',
  data() {
    return {
      infoHtml: ''
    }
  },
  async created() {
    const res = await fetch('/info.md')
    const markdown = await res.text()
    this.infoHtml = marked.parse(markdown)
  }
}
</script>

<style scoped>
.info-page {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
}
.info-page :deep(table) {
  border-collapse: collapse;
  margin-bottom: 1rem;
}
.info-page :deep(th),
.info-page :deep(td) {
  border: 1px solid #dee2e6;
  padding: 6px 10px;
  vertical-align: top;
}
</style>
