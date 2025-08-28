<template>
  <div style="background-color: #f8f8fc !important; color: #82868f !important; font-family: 'futura-pt', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; font-size: 17px !important;">
    <FrappeUIProvider>
      <router-view />
    </FrappeUIProvider>
  </div>
</template>

<script setup>
  import { FrappeUIProvider } from 'frappe-ui'

</script>
