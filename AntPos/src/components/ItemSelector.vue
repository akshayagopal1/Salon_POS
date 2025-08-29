<template>
    <div class="md:w-1/2 w-full shadow-2xl pt-2 px-2 rounded">
      <!-- Search Input -->
      <FormControl
        type="text"
        v-model="debounceSearch"
        placeholder="Search Items"
        size="sm"
        variant="subtle"
        @input="fetchItems"
        :disabled="base.is_return"
      >
        <template #prefix>
          <FeatherIcon class="w-4" name="search" />
        </template>
      </FormControl>

      <!-- Items Grid -->
      <div class="mt-4 h-[calc(100%-40px)] overflow-y-auto scrollbar-hide">
        <div v-if="!items.length && itemListResource.loading" class="text-center text-gray-500">
            Loading items...
        </div>
        <div v-else-if="!items.length" class="text-center text-gray-500">
          No items found. Try searching again.
        </div>

        <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <!-- MODIFIED: Item card structure to include image -->
          <div
            v-for="item in items"
            :key="item.item_code"
            @click="handleItemClick(item)"
            class="border rounded-lg cursor-pointer hover:shadow-lg transition-shadow flex flex-col overflow-hidden bg-white"
          >
            <!-- Image Section -->
            <div class="h-28 w-full bg-gray-100 flex items-center justify-center">
                <img v-if="item.image" :src="item.image" :alt="item.item_name" class="h-full w-full object-cover">
                <!-- Fallback placeholder if no image -->
                <FeatherIcon v-else name="image" class="text-gray-400 w-10 h-10" />
            </div>

            <!-- Details Section -->
            <div class="p-2 flex-grow flex flex-col justify-between">
                <div class="font-semibold text-sm truncate" :title="item.item_name">{{ item.item_name }}</div>
                <div>
                    <div class="text-gray-600 text-xs">Price: {{ item.rate }} {{ base.pos_profile.currency }}</div>
                    <div class="text-gray-500 text-xs">In Stock: {{ item.stock_qty }}</div>
                </div>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
  import { ref, inject, watch, onMounted } from 'vue'
  import { FormControl, FeatherIcon, createResource } from 'frappe-ui'
  import { createToast } from '../utils' // Assuming this is your toast function path

  const items = ref([])
  const debounceSearch = ref('')
  const base = inject('base')

  const fetchItems = () => {
    if (!base.pos_profile?.name) {
      // Don't fetch if profile isn't loaded yet. Watcher will trigger it.
      return
    }
    itemListResource.fetch()
  }

  const itemListResource = createResource({
    url: 'ant_pos.ant_pos.api.item.items',
    method: 'GET',
    auto: false, // We will trigger it manually
    makeParams() {
      return {
        pos_profile: base.pos_profile.name,
        search_value: debounceSearch.value,
        customer: base.customer?.name || '',
      }
    },
    onSuccess(data) {
      items.value = data || []
    },
    onError(error) {
      console.error('Failed to fetch items:', error)
      createToast({ title: 'Error', message: 'Failed to load items' })
    }
  })

  // Initial load when the component is mounted
  onMounted(() => {
    if (base.pos_profile?.name) {
      fetchItems()
    }
  })

  // Watch for changes that should trigger a re-fetch of items
  watch(
    () => base.pos_profile?.name,
    (newName) => {
      if (newName) {
        fetchItems()
      }
    },
    { immediate: true }
  )


  const handleItemClick = (item) => {
    if (!base.customer?.name) {
      createToast({ title: 'Warning', message: 'Please select a customer first' })
      return
    }

    if (!base.employee?.name) {
        createToast({ title: 'Warning', message: 'Please select an employee' })
        return
    }

    const existing = base.items.find(i => i.item_code === item.item_code && !i.is_return)

    if (existing) {
      existing.qty += 1
      existing.amount = existing.rate * existing.qty
      createToast({ title: 'Info', message: `Increased quantity for ${item.item_name}` })
    } else {
      const cartItem = {
        item_code: item.item_code,
        item_name: item.item_name,
        rate: item.rate,
        image: item.image,
        stock_uom: item.stock_uom,
        uom: item.stock_uom,
        qty: 1,
        amount: item.rate * 1,

        // ================== LINE ADDED HERE ==================
        sales_person: base.employee.name, // Send the currently selected employee
        // =====================================================

        doctype: 'Sales Invoice Item',
        parenttype: 'Sales Invoice',
        custom_id: `cart-item-${Date.now()}`
      }
      base.items.push(cartItem)
      createToast({ title: 'Success', message: `${item.item_name} added to cart` })
    }
  }
</script>