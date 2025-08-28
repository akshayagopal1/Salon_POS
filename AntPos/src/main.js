import './index.css'

import { createApp, reactive } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'
import mitt from 'mitt';

import {
  Button,
  Card,
  Input,
  setConfig,
  frappeRequest,
  resourcesPlugin,
} from 'frappe-ui'


const app = createApp(App)

const emitter = mitt();

const pinia = createPinia()

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)

app.component('Button', Button)
app.component('Card', Card)
app.component('Input', Input)

app.use(pinia)

const base = reactive({
  customer: {},
  employee: {},
  Ant_Opening_Shift:{},
  pos_profile:{},
  items:[],
  invoice:{
    
  },
  page:'Pos',
  discount_amount: 0.00,
  additional_discount_percentage: 0.00,
  total: 0.00,
  is_return: false
})
app.provide('base', base)

// Provide emitter it globally
app.provide('emitter', emitter);

app.mount('#app')