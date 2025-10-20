<template>
  <div class="info-page" v-html="infoHtml"></div>
</template>

<script>
import readme from '../../README.md';
import { marked } from 'marked';

export default {
  name: 'InfoPage',
  data: () => ({ infoHtml: '' }),
  created() {
    const match = readme.match(/<!-- INFO_START -->([\s\S]*?)<!-- INFO_END -->/);
    const markdown = match ? match[1] : 'Keine Anwenderhilfe gefunden.';
    // Markdown → HTML umwandeln
    this.infoHtml = marked.parse(markdown);
  }
};
</script>

<style scoped>
.info-page {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  font-size: 16px;
  color: #333;
}

/* Überschriften */
.info-page h1 {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-align: center;
}

.info-page h2 {
  font-size: 1.5rem;
  margin-top: 2rem;
  margin-bottom: 1rem;
  font-weight: 600;
  border-bottom: 2px solid #eee;
  padding-bottom: 0.3rem;
}

.info-page h3 {
  font-size: 1.2rem;
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #444;
}

/* Absätze und Listen */
.info-page p {
  margin-bottom: 1rem;
}

.info-page ul, 
.info-page ol {
  margin-bottom: 1rem;
  padding-left: 1.5rem;
}

.info-page li {
  margin-bottom: 0.5rem;
}

/* Code Inline */
.info-page code {
  background: #f8f9fa;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-size: 0.9rem;
  color: #c7254e;
}

/* Tipps / Hinweise */
.info-page blockquote {
  background: #f1f3f5;
  border-left: 4px solid #0d6efd;
  margin: 1rem 0;
  padding: 0.5rem 1rem;
  font-style: italic;
  color: #555;
}
</style>



