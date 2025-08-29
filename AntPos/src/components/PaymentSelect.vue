<template>
    <div class="w-full h-[94%] flex p-2 gap-4" style="background-color: #f8f8fc !important; color: #82868f !important; font-family: 'futura-pt', sans-serif !important; font-size: 17px !important;">
        <div class="w-full h-full ">
            <div class="w-full h-full flex gap-6 ">
                <div class="w-[65%] h-full">
                    <div class="w-full h-full shadow-2xl p-4 rounded" style="background-color: #ffffff !important;">
                        <div class="h-[6%]">
                            <Customer/>
                        </div>
                        <div class="w-full h-[94%] flex flex-col gap-4">
                            <TextInput type="text" v-model="searchQuery" placeholder="Search">
                                <template #prefix>
                                    <FeatherIcon class="w-4" name="search" />
                                </template>
                            </TextInput>
                            <div class="flex justify-evenly text-center rounded-md p-3 h-[6%] items-center" style="background-color: #4e60ac !important; color: white !important; font-size: 17px !important;">
                                <div class="w-[4%]">
                                    <input type="checkbox" :checked="selectAll" class="text-black rounded-sm focus:outline-none focus:ring-0 focus:border-transparent" @change="toggleAllSelection" />
                                </div>
                                <p class="w-[19%]">Name</p>
                                <p class="w-[19%]">Customer</p>
                                <p class="w-[19%]">Amount</p>
                                <p class="w-[19%]">Outstanding</p>
                            </div>
                            <div class="h-[92%] overflow-y-scroll rounded scrollbar-hide flex flex-col gap-3 text-center">
                                <div v-if="filteredInvoices.length === 0" class="flex justify-center items-center h-full">
                                    <p class="text-gray-500">No invoices found</p>
                                </div>
                                <div v-for="invoice in filteredInvoices" :key="invoice.name" class="w-full">
                                    <div class="flex justify-evenly items-center rounded text-center p-2.5" style="background-color: #f8f8fc !important;">
                                        <div class="w-[4%]">
                                            <input type="checkbox" :checked="invoice.selected" class="text-black rounded-sm focus:outline-none focus:ring-0 focus:border-transparent" @change="toggleSelection(invoice)" />
                                        </div>
                                        <p class="w-[19%]">{{ invoice.name }}</p>
                                        <p class="w-[19%]">{{ invoice.customer }}</p>
                                        <p class="w-[19%]">{{ invoice.grand_total }}</p>
                                        <p class="w-[19%]">{{ invoice.outstanding_amount }}</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="w-[35%] h-full">
                    <div class="w-full h-full shadow-2xl p-4 rounded flex flex-col justify-between" style="background-color: #ffffff !important;">
                        <div class="flex flex-col gap-4">
                            <div class="flex flex-col gap-6 h-fit">
                                <div class="flex justify-evenly rounded-md p-3" style="background-color: #4e60ac !important; color: white !important;">
                                    <p>Payment Total</p>
                                </div>
                                <FormControl
                                    type="number"
                                    size="sm"
                                    variant="subtle"
                                    placeholder="0"
                                    :disabled="true"
                                    label="Total Selected Outstanding"
                                    v-model="totalSelectedAmount"
                                />
                            </div>
                            <div>
                                <p class="text-2xl font-bold">Payment Method</p>
                                <div class="grid grid-cols-2 gap-4 p-2 items-center" v-for="(mode, index) in modes" :key="index">
                                    <FormControl
                                        type="number"
                                        size="sm"
                                        variant="subtle"
                                        placeholder="0"
                                        :disabled="false"
                                        :label="`${mode.mode_of_payment}:`"
                                        v-model="mode.amount"
                                    />
                                    <Button
                                        class="w-full h-full"
                                        :variant="'solid'"
                                        size="lg"
                                        @click="setFullAmount(index)"
                                        style="background-color: #4e60ac !important; color: white !important;"
                                    >
                                        {{ mode.mode_of_payment }}
                                    </Button>
                                </div>
                                <FormControl
                                    type="number"
                                    size="sm"
                                    variant="subtle"
                                    placeholder="0"
                                    :disabled="true"
                                    v-model="differenceAmount"
                                    label="Difference:"
                                />
                            </div>
                        </div>
                        <div class="text-right">
                            <Button
                                class="w-full p-2 h-full"
                                :variant="'solid'"
                                size="lg"
                                :loading="paymentResource.loading"
                                @click="createPayment"
                                :disabled="!canSubmit"
                                style="background-color: #4e60ac !important; color: white !important;"
                            >
                                Submit
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { createListResource, TextInput, FormControl, FeatherIcon, createResource } from 'frappe-ui';
import { ref, inject, computed, watch, onMounted } from 'vue';
import Customer from './Customer.vue';
import { createToast } from '../utils';

const base = inject('base');
const searchQuery = ref("");
const selectAll = ref(false);
const modes = ref([]);
const totalSelectedAmount = ref(0);

const invoices = createListResource({
    doctype: 'Sales Invoice',
    fields: ['name', 'customer', 'grand_total', 'outstanding_amount'],
    filters: computed(() => ({ 
        outstanding_amount: [">", 0],
        docstatus: 1, 
        is_return: 0, 
        customer: base.customer?.name || ""
    })),
    transform: (data) => data.map(d => ({ ...d, selected: false })),
    auto: true
});

const filteredInvoices = computed(() => {
    if (!invoices.data) return [];
    if (!searchQuery.value) return invoices.data;
    return invoices.data.filter(invoice => 
        invoice.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
});

const calculateTotalSelected = () => {
    totalSelectedAmount.value = invoices.data
        .filter(inv => inv.selected)
        .reduce((sum, inv) => sum + inv.outstanding_amount, 0);
};

const toggleAllSelection = () => {
    selectAll.value = !selectAll.value;
    invoices.data.forEach(invoice => invoice.selected = selectAll.value);
    calculateTotalSelected();
};

const toggleSelection = (invoice) => {
    invoice.selected = !invoice.selected;
    selectAll.value = invoices.data.every(inv => inv.selected);
    calculateTotalSelected();
};

const totalPaidAmount = computed(() => {
    return modes.value.reduce((sum, mode) => sum + Number(mode.amount || 0), 0);
});

const differenceAmount = computed(() => {
    return totalSelectedAmount.value - totalPaidAmount.value;
});

const canSubmit = computed(() => {
    const hasSelection = invoices.data?.some(inv => inv.selected);
    const hasPayment = totalPaidAmount.value > 0;
    return hasSelection && hasPayment && differenceAmount.value >= 0;
});

const setFullAmount = (index) => {
    modes.value.forEach((mode, i) => {
        mode.amount = (i === index) ? totalSelectedAmount.value : 0;
    });
};

const paymentResource = createResource({
    url: 'ant_pos.ant_pos.api.payment_entry.settle_invoices_with_payment',
    method: 'POST',
    auto: false,
});

const createPayment = async () => {
    const selectedReferences = invoices.data
        .filter(inv => inv.selected)
        .map(inv => inv.name);

    const paymentDetails = modes.value
        .filter(mode => Number(mode.amount || 0) > 0);
    
    await paymentResource.submit({
        customer: base.customer.name,
        references: selectedReferences,
        payments: paymentDetails,
        pos_profile: base.pos_profile.name
    });

    if (!paymentResource.error) {
        createToast({ title: 'Success', message: 'Payment submitted successfully!' });
        clearForm();
    } else {
        createToast({ title: 'Error', message: paymentResource.error.messages?.[0] || 'An error occurred' });
    }
};

const clearForm = () => {
    invoices.reload();
    modes.value.forEach(mode => mode.amount = 0);
    totalSelectedAmount.value = 0;
    selectAll.value = false;
};

onMounted(() => {
    if (base.pos_profile?.payments) {
        modes.value = base.pos_profile.payments.map(p => ({
            mode_of_payment: p.mode_of_payment,
            amount: 0
        }));
    }
});

watch(() => base.customer, (newCustomer) => {
    if (newCustomer?.name) {
        invoices.reload();
    } else {
        invoices.data = [];
    }
    clearForm();
}, { deep: true });
</script>