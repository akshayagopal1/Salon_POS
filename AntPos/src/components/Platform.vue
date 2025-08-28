<template>
  <div
    class="w-full h-full bg-[#f8f8fc] text-[#82868f]"
    :class="props.collapse ? 'xl:w-[97%]' : 'xl:w-[90%]'"
    style="font-family: 'futura-pt', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 17px;"
  >
        <Navbar />
        <component :is="componentMap[currentComponent]" />
    </div>
</template>

<script setup>
  import Navbar from '../components/Navbar.vue';
  import PaymentSelect from '../components/PaymentSelect.vue';
  import Pos from '../components/Pos.vue';
  import SalesInvoice from './SalesInvoice.vue';
  import emitter from '../utils/emitter';
  import { computed, inject, defineProps } from 'vue';
  
  
  const props = defineProps({
        collapse: {
            type: Boolean,
            required: true,
        },
  });
  const base = inject('base');

  const componentMap = {
    PaymentSelect,
    Pos,
    SalesInvoice
  };

  const currentComponent = computed(() => {
    if (base.page === 'payments') return 'PaymentSelect';
    if (base.page === 'salesinvoice') return 'SalesInvoice';
    return 'Pos';
  });

  emitter.on('updatePage', (page) => {
    base.items = [];
    base.invoice = {};
    base.customer = {};
    base.page = page;
  });

</script>