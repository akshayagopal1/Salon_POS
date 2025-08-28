<template>
  <div class="w-screen h-screen flex select-none" style="background-color: #f8f8fc !important; color: #82868f !important; font-family: 'futura-pt', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; font-size: 17px !important;">
    <div v-if="currentComponent">
        <component :is="currentComponent"  @switchComponent="loadComponent"  />
    </div>
    <Sidebar :class="w-full" :collapse="collapse"/>
    <Platform :collapse="collapse"/>
  </div>
</template>

<script setup>
  import Sidebar from '../components/Sidebar.vue';
  import Platform from '../components/Platform.vue';
  // 1. IMPORT 'provide' AND 'reactive' FROM VUE
  import { provide, reactive, ref } from 'vue';
  import { useDynamicComponent } from '../utils/Dialog';
  import { usePageMeta } from 'frappe-ui';
  import emitter from '../utils/emitter';
  import  { getSettings } from '../stores/settings';

  const collapse=ref(true)
  const { currentComponent, loadComponent } = useDynamicComponent();
  const { brand } = getSettings()

  loadComponent('OpenShift');
  provide('dynamicComponent', { currentComponent, loadComponent });

  // 2. CREATE THE REACTIVE 'base' OBJECT HERE
  // This will be the single source of truth for your entire POS application.
  const base = reactive({
      items: [],
      customer: {},
      employee: {},
      invoice: {},
      pos_profile: {},
      page: 'Pos', // Default page
      // Add any other global state properties you need
  });

  // 3. PROVIDE THE REACTIVE 'base' OBJECT TO ALL CHILDREN
  // Now Platform.vue, ItemSelector.vue, ItemDetail.vue, etc. will all share the same reactive state.
  provide('base', base);


  usePageMeta(() => {
    return {
      icon: brand.favicon ? brand.favicon : '/assets/ant_pos/antPOS.png',
    }
  })
  emitter.on('trigger_collapse', () => {

    collapse.value =!collapse.value
  });
</script>