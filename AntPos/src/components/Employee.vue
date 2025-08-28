<template>
  <div class="w-full" style="background-color: #ffffff !important; color: #82868f !important; font-family: 'futura-pt', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; font-size: 17px !important;">
    <Autocomplete
      :options="computedOptions"
      v-model="selectedEmployee"
      placeholder="Select Employee"
    />
  </div>
</template>

<script setup>
import { computed, inject, onMounted, onUnmounted, watch } from 'vue';
import emitter from '../utils/emitter'; 
import Autocomplete from './custom_components/Autocomplete.vue';
import { createListResource } from 'frappe-ui';
import { createToast } from '../utils';

let base = inject('base');
let errorHandled = false;

const employeeResource = createListResource({
  doctype: 'Employee',
  fields: ['name', 'employee_name', 'department', 'designation', 'status'],
  filters: {
    status: 'Active',
  },
  pageLength: Number.MAX_VALUE * 2,
  auto: true,
  onSuccess(data) {
    errorHandled = false;
  },
  onError(error) {
    if (!errorHandled) {
        createToast({
            title: 'error',
            message: Array.isArray(error?.messages) ? error.messages[0] : error?.messages || error || 'An error occurred',
            icon: 'x-circle',
            iconClasses: 'bg-surface-red-5 text-ink-white rounded-md p-px',
            position: 'top-center',
            timeout: 5,
        });
        errorHandled = true;
    }
    },
  transform: (data) => {
    return data.map((item) => ({
      label: item.employee_name || item.name,
      value: item.name,
      name: item.name,
      employee_name: item.employee_name,
      department: item.department,
      designation: item.designation,
      status: item.status,
    }));
  },
});

const computedOptions = computed(() => {
  return employeeResource?.data
    ? employeeResource.data.map((option) => ({
        label: option.label || 'Unnamed',
        value: option.value,
        name: option.name,
        employee_name: option.employee_name,
        department: option.department,
        designation: option.designation,
        status: option.status,
      }))
    : [];
});

const refreshEmployeeList = async (params) => {
  await employeeResource.fetch();
  selectedEmployee.value = {
      label: params.employee_name || params.name || 'Unnamed',
      value: params.name,
      name: params.name,
      employee_name: params.employee_name,
      department: params.department,
      designation: params.designation,
      status: params.status,
  }
};

onMounted(() => {
  emitter.on("employeeCreated", refreshEmployeeList);
});

onUnmounted(() => {
  emitter.off("employeeCreated", refreshEmployeeList);
});

const selectedEmployee = computed({
  get: () => base.employee,
  set: (newVal) => {
    if(base.is_return) return
    base.employee = newVal;
  },
});

</script>
