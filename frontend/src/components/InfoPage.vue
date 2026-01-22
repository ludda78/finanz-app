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
</style>
