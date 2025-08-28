<template>
  <Dialog :options="{ size: 'lg' }" v-model="dialogVisible">
    <template #body-title>
      <h3 class="text-[#4e60ac]" style="font-family: 'futura-pt', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 17px;">Mark Attendance</h3>
    </template>

    <template #body-content>
      <div class="bg-[#ffffff] text-[#82868f]" style="font-family: 'futura-pt', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 17px;">
      <div class="space-y-3">
        <!-- Employee Dropdown -->
        <FormControl
          type="autocomplete"
          :options="options.employees"
          size="sm"
          variant="subtle"
          placeholder="Select Employee"
          label="Employee"
          v-model="formData.employee"
        />

        <!-- Status -->
        <FormControl
          type="autocomplete"
          :options="statusOptions"
          size="sm"
          variant="subtle"
          placeholder="Select Status"
          label="Status"
          v-model="formData.status"
        />

        <!-- Date -->
        <FormControl
          type="date"
          size="sm"
          variant="subtle"
          label="Date"
          v-model="formData.date"
        />

        <!-- Company -->
        <FormControl
          type="autocomplete"
          :options="options.companies"
          size="sm"
          variant="subtle"
          placeholder="Select Company"
          label="Company"
          v-model="formData.company"
        />

        <!-- Shift -->
        <FormControl
          type="autocomplete"
          :options="options.shifts"
          size="sm"
          variant="subtle"
          placeholder="Select Shift (Optional)"
          label="Shift"
          v-model="formData.shift"
        />

        <!-- Late Entry -->
        <FormControl label="Late Entry (minutes)">
          <Input
            type="number"
            min="0"
            v-model.number="formData.late_entry"
          />
        </FormControl>

        <!-- Early Exit -->
        <FormControl label="Early Exit (minutes)">
          <Input
            type="number"
            min="0"
            v-model.number="formData.early_exit"
          />
        </FormControl>
      </div>
      
      <div class="flex justify-end gap-2 mt-4">
        <Button variant="ghost" @click="closeDialog">Cancel</Button>
        <Button variant="solid" @click="handleSubmit" style="background-color: #4e60ac !important; border-color: #4e60ac !important; color: white !important; font-family: 'futura-pt', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; font-size: 17px !important;">Submit</Button>
      </div>
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import { createResource, Button, Dialog, FormControl } from 'frappe-ui';
import { inject, ref, reactive, onMounted } from 'vue';

const dialogVisible = ref(true);
const options = reactive({
  employees: [],
  companies: [],
  shifts: []
});

const formData = ref({
  employee: {},
  status: { label: 'Present', value: 'Present' },
  date: new Date().toISOString().slice(0, 10),
  company: {},
  shift: {},
  late_entry: 0,
  early_exit: 0
});

const statusOptions = [
  { label: 'Present', value: 'Present' },
  { label: 'Absent', value: 'Absent' },
  { label: 'Half Day', value: 'Half Day' },
  { label: 'On Leave', value: 'On Leave' },
  { label: 'Work From Home', value: 'Work From Home' }
];

function closeDialog() {
  dialogVisible.value = false;
}

// Fetch dropdown data using POS profile pattern
const fetchDropdownData = createResource({
  url: 'ant_pos.ant_pos.api.attendance.get_dropdown_data',
  method: 'GET',
  onSuccess(data) {
    console.log('Dropdown data loaded:', data);
    if (data) {
      options.employees = data.employees?.map(emp => ({ 
        label: emp.employee_name, 
        value: emp.name 
      })) || [];
      options.companies = data.companies?.map(comp => ({ 
        label: comp.name, 
        value: comp.name 
      })) || [];
      options.shifts = data.shifts?.map(shift => ({ 
        label: shift.name, 
        value: shift.name 
      })) || [];
    }
  },
  onError(error) {
    console.error('Failed to load dropdown data:', error);
  }
});

// Create attendance submission resource
const createAttendance = createResource({
  url: 'ant_pos.ant_pos.api.attendance.create_attendance',
  onSuccess(data) {
    alert(`Attendance marked successfully! Document: ${data}`);
    closeDialog();
  },
  onError(err) {
    console.error('Attendance submission failed:', err);
    alert(`Failed to mark attendance: ${err.message}`);
  },
});

// Submit Attendance
function handleSubmit() {
  console.log('Form data before submission:', formData.value);
  
  if (!formData.value.employee?.value || !formData.value.status?.value || !formData.value.date) {
    alert('Please fill all required fields.');
    return;
  }

  const submissionData = {
    employee: formData.value.employee.value,
    status: formData.value.status.value,
    attendance_date: formData.value.date,
    shift: formData.value.shift?.value || null,
    late_entry: formData.value.late_entry || 0,
    early_exit: formData.value.early_exit || 0
  };

  console.log('Submission data:', submissionData);
  createAttendance.submit({ values: submissionData });
}

// Load data on mount
onMounted(() => {
  fetchDropdownData.fetch();
});
</script>
