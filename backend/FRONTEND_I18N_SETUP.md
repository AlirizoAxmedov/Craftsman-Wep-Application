# Frontend Internationalization (i18n) Setup Guide

Complete setup for multi-language support (English, Russian, Uzbek) with Vue 3 and vue-i18n.

## Installation

### 1. Install Required Packages
```bash
npm install vue-i18n@next axios
npm install --save-dev @types/node
```

### 2. Create i18n Configuration

**File: `src/i18n/index.js`**
```javascript
import { createI18n } from 'vue-i18n'

// Import locale messages (will be populated from API)
import enMessages from './locales/en.json'
import ruMessages from './locales/ru.json'
import uzMessages from './locales/uz.json'

const i18n = createI18n({
  legacy: false, // Use composition API
  locale: localStorage.getItem('language') || 'en',
  fallbackLocale: 'en',
  messages: {
    en: enMessages,
    ru: ruMessages,
    uz: uzMessages
  },
  globalInjection: true,
  missingWarn: false, // Suppress warnings for missing keys
  fallbackWarn: false
})

export default i18n
```

### 3. Create Translation Loader Service

**File: `src/api/translationService.js`**
```javascript
import axios from 'axios'

const API_BASE_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000'

const translationService = {
  /**
   * Fetch all translations for a language from backend
   */
  async getLocale(language = 'en') {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/translations/locale/${language}`
      )
      return response.data.translations || {}
    } catch (error) {
      console.error(`Failed to load locale ${language}:`, error)
      return {}
    }
  },

  /**
   * Auto-translate content to multiple languages
   */
  async autoTranslate(key, englishText, languages = ['ru', 'uz']) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/translations/${key}/auto-translate`,
        null,
        {
          params: {
            english_text: englishText,
            languages: languages
          }
        }
      )
      return response.data.translations
    } catch (error) {
      console.error(`Auto-translation failed for key ${key}:`, error)
      return { en: englishText }
    }
  },

  /**
   * Save translations to backend
   */
  async saveTranslations(key, translations) {
    try {
      const response = await axios.put(
        `${API_BASE_URL}/api/translations/${key}`,
        {
          english: translations.en,
          russian: translations.ru,
          uzbek: translations.uz
        }
      )
      return response.data
    } catch (error) {
      console.error(`Failed to save translations for key ${key}:`, error)
      throw error
    }
  },

  /**
   * Batch import translations from JSON data
   */
  async batchImport(translationsArray) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/translations/batch/import`,
        translationsArray
      )
      return response.data
    } catch (error) {
      console.error('Batch import failed:', error)
      throw error
    }
  }
}

export default translationService
```

### 4. Create Language Switcher Component

**File: `src/components/LanguageSwitcher.vue`**
```vue
<template>
  <div class="language-switcher">
    <button
      v-for="lang in languages"
      :key="lang.code"
      :class="['lang-button', { active: currentLanguage === lang.code }]"
      @click="switchLanguage(lang.code)"
      :title="lang.name"
    >
      {{ lang.flag }} {{ lang.code.toUpperCase() }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import translationService from '@/api/translationService'

const { locale } = useI18n()

const languages = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'ru', name: 'Русский', flag: '🇷🇺' },
  { code: 'uz', name: 'Ўзбек', flag: '🇺🇿' }
]

const currentLanguage = computed(() => locale.value)

const switchLanguage = async (lang) => {
  try {
    // Load locale from backend
    const messages = await translationService.getLocale(lang)
    
    // Update i18n
    locale.value = lang
    
    // Save preference to localStorage
    localStorage.setItem('language', lang)
    
    // Update i18n messages
    if (Object.keys(messages).length > 0) {
      const i18nInstance = useI18n()
      i18nInstance.setLocaleMessage(lang, messages)
    }
  } catch (error) {
    console.error('Language switch failed:', error)
  }
}
</script>

<style scoped>
.language-switcher {
  display: flex;
  gap: 0.5rem;
}

.lang-button {
  padding: 0.5rem 1rem;
  border: 2px solid var(--divider);
  background: var(--surface);
  color: var(--text);
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.lang-button:hover {
  border-color: var(--accent);
  color: var(--accent);
}

.lang-button.active {
  background: var(--accent);
  color: white;
  border-color: var(--accent);
}
</style>
```

### 5. Update Main App File

**File: `src/main.js`**
```javascript
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import i18n from './i18n'

const app = createApp(App)

app.use(router)
app.use(i18n)

app.mount('#app')
```

### 6. Create Locale JSON Files

**File: `src/i18n/locales/en.json`**
```json
{
  "header": {
    "title": "Uzbek Kandakorlik",
    "subtitle": "Copper Engraving Mastery"
  },
  "schools": {
    "bukhara": {
      "title": "Bukhara School",
      "description": "Known for elegant and simple designs with distinctive dotted background technique."
    },
    "samarkand": {
      "title": "Samarkand School",
      "description": "Famous for complex geometric patterns and sophisticated artistic techniques."
    }
  },
  "quiz": {
    "instructions": "Read each question carefully and select the correct answer.",
    "timeRemaining": "Time remaining: {time}",
    "submit": "Submit Quiz",
    "passed": "Congratulations! You passed the quiz.",
    "failed": "You need {score}% to pass. Try again!"
  },
  "validation": {
    "emailRequired": "Email is required",
    "passwordTooShort": "Password must be at least 8 characters"
  }
}
```

**File: `src/i18n/locales/ru.json`**
```json
{
  "header": {
    "title": "Узбекское кандакорство",
    "subtitle": "Мастерство медной гравировки"
  },
  "schools": {
    "bukhara": {
      "title": "Школа Бухары",
      "description": "Известна элегантными и простыми дизайнами с характерной техникой пунктирного фона."
    }
  },
  "quiz": {
    "instructions": "Внимательно прочитайте каждый вопрос и выберите правильный ответ.",
    "timeRemaining": "Осталось времени: {time}",
    "submit": "Отправить квиз",
    "passed": "Поздравляем! Вы прошли квиз.",
    "failed": "Вам нужно набрать {score}% чтобы пройти. Попробуйте снова!"
  }
}
```

**File: `src/i18n/locales/uz.json`**
```json
{
  "header": {
    "title": "Ўзбек Кандакорлиги",
    "subtitle": "Мисали ворис авада ҳунари"
  },
  "schools": {
    "bukhara": {
      "title": "Бухоро Мактаби",
      "description": "Элегант ва содда дизайнлар ва диагностиквасит фон техникаси учун машҳур."
    }
  },
  "quiz": {
    "instructions": "Ҳар бир саволни диққат билан ўқиб, тўғри жавобни танлаңиз.",
    "timeRemaining": "Қолган вақт: {time}",
    "submit": "Викторинани жўнатиш",
    "passed": "Табриклаймиз! Сиз викторинани ўтдингиз.",
    "failed": "Ўтиш учун {score}% га эҳтиёж. Қайта уринб кўринг!"
  }
}
```

## Usage in Vue Components

### Basic Template Usage
```vue
<template>
  <div>
    <h1>{{ $t('header.title') }}</h1>
    <p>{{ $t('quiz.instructions') }}</p>
  </div>
</template>
```

### With Interpolation
```vue
<template>
  <div>
    <p>{{ $t('quiz.timeRemaining', { time: '5:00' }) }}</p>
  </div>
</template>
```

### Script Setup Usage
```vue
<script setup>
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()

console.log(t('header.title'))
console.log(locale.value) // 'en'
</script>
```

## Auto-Translation Workflow

### 1. Admin Creates Content
```javascript
// When admin adds school description
const newSchool = {
  name: 'Samarkand',
  description: 'The Samarkand school flourished under Timur...'
}

// Auto-translate
const translations = await translationService.autoTranslate(
  'school.samarkand.description',
  newSchool.description,
  ['ru', 'uz']
)

// Returns:
// {
//   'en': 'The Samarkand school...',
//   'ru': 'Школа Самарканда...',
//   'uz': 'Samarqand maktabi...'
// }
```

### 2. Load Translations on App Start
```javascript
// In App.vue setup()
import { useI18n } from 'vue-i18n'
import translationService from '@/api/translationService'

const { locale, setLocaleMessage } = useI18n()

onMounted(async () => {
  const languages = ['en', 'ru', 'uz']
  
  for (const lang of languages) {
    const messages = await translationService.getLocale(lang)
    setLocaleMessage(lang, messages)
  }
})
```

### 3. Update Translations in Real-Time
```javascript
// When quiz results are added, auto-translate feedback
const feedback = 'Great job! You scored 95% on this quiz.'

const translations = await translationService.autoTranslate(
  'feedback.high_score',
  feedback,
  ['ru', 'uz']
)

// Save to backend
await translationService.saveTranslations(
  'feedback.high_score',
  translations
)
```

## Environment Configuration

**File: `.env.local`**
```
VUE_APP_API_URL=http://localhost:8000
VUE_APP_DEFAULT_LANGUAGE=en
```

## Translation Key Naming Convention

```
{feature}.{object}.{property}

Examples:
- school.bukhara.title
- school.bukhara.description
- quiz.instructions
- quiz.timeRemaining
- validation.emailRequired
- feedback.passed
- feedback.failed
```

## Best Practices

1. **Lazy Load Translations**: Load only necessary locales to reduce bundle size
2. **Fallback Language**: Always have English as fallback
3. **Cache Translations**: Store in localStorage to minimize API calls
4. **Validate Keys**: Check for missing translation keys in development
5. **Use Namespacing**: Organize keys hierarchically (school.*, quiz.*, etc.)
6. **Pluralization**: Use special i18n format for plural forms
7. **Date/Time Formatting**: Use i18n built-in formatters for dates

## Production Deployment

1. **Pre-generate Locales**: Export all locale files from backend during build
2. **Static Hosting**: Serve locale files from CDN for faster access
3. **Compression**: Gzip JSON files for smaller payloads
4. **Version Locking**: Pin translation API version to prevent breaking changes

## Troubleshooting

### Missing Translations
```javascript
// Check if translation exists
const { t, te } = useI18n()
if (te('key.path')) {
  console.log(t('key.path'))
} else {
  console.warn('Translation key not found')
}
```

### Language Not Switching
```javascript
// Ensure locale is updated first
locale.value = 'ru'

// Then update messages
setLocaleMessage('ru', newMessages)
```

### API Translations Not Loading
```javascript
// Add error handling
try {
  const messages = await translationService.getLocale('ru')
  if (Object.keys(messages).length === 0) {
    console.warn('Empty translations from API')
  }
} catch (error) {
  console.error('API error:', error)
  // Fall back to cached translations
}
```

## References

- [Vue-i18n Documentation](https://vue-i18n.intlify.dev/)
- [DeepL API](https://www.deepl.com/docs-api)
- [Google Translate API](https://cloud.google.com/translate/docs)
