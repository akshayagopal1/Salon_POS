<template>
    <div class="md:w-1/2 w-full shadow-2xl pt-2 px-2 rounded ">
        <div class="h-[85%] w-full">
            <!-- Amount Paid / To Be Paid / Paid Change -->
            <div class="grid grid-cols-2 gap-4 p-2">
                <FormControl
                    :type="'number'"
                    :ref_for="true"
                    size="sm"
                    variant="subtle"
                    placeholder="Placeholder"
                    :disabled="true"
                    label="Amount Paid"
                    :value="Number(base.invoice.paid_amount).toFixed(2)"
                    v-model="base.invoice.paid_amount"
                />
                <FormControl
                    v-if="base.invoice.paid_amount > base.invoice.grand_total"
                    :type="'number'"
                    :ref_for="true"
                    size="sm"
                    variant="subtle"
                    placeholder="Placeholder"
                    :disabled="true"
                    label="Paid Change"
                    :value="Number(base.invoice.paid_amount - base.invoice.grand_total).toFixed(2)"
                />
            </div>

            <!-- Payments -->
            <div class="grid grid-cols-2 gap-4 p-2 items-center" v-for="(mode, index) in base?.pos_profile?.payments" :key="index">
                <FormControl
                    v-if="base.invoice?.payments?.[index] && base.invoice?.payments?.[index].amount !== undefined"
                    type="number"
                    size="sm"
                    variant="subtle"
                    placeholder="0.00"
                    :disabled="false"
                    :label="mode.mode_of_payment"
                    :value="Number(base.invoice.payments[index].amount).toFixed(2)"
                    v-model="base.invoice.payments[index].amount"
                    @change="changePaymentAmount($event)"
                />
                <Button
                    v-if="base.invoice?.payments?.[index] && base.invoice?.payments?.[index].amount !== undefined"
                    class="w-full h-full"
                    :variant="'solid'"
                    size="lg"
                    label="Button"
                    :loading="false"
                    :disabled="false"
                    @click="changemode(index)"
                    style="background-color: #4e60ac; color: #ffffff;"
                >
                    {{ mode.mode_of_payment }}
                </Button>
            </div>

            <!-- Exclusive VAT Toggle -->
            <div class="p-2 flex items-center gap-2">
                <label class="flex items-center gap-2">
                    <input
                        type="checkbox"
                        v-model="isExclusiveVat"
                        class="toggle-checkbox"
                    />
                    <span>Exclusive VAT (-5%)</span>
                </label>
            </div>

            <!-- Totals Section -->
            <div class="grid grid-cols-2 gap-4 p-2">
                <FormControl
                    :type="'number'"
                    :ref_for="true"
                    size="sm"
                    variant="subtle"
                    placeholder="0.00"
                    :disabled="true"
                    label="Net Total"
                    :value="Number(base.invoice.net_total).toFixed(2)"
                    v-model="base.invoice.net_total"
                />
                <FormControl
                    :type="'number'"
                    :ref_for="true"
                    size="sm"
                    variant="subtle"
                    placeholder="0.00"
                    :disabled="true"
                    label="Total Amount"
                    :value="Number(base.invoice.total).toFixed(2)"
                    v-model="base.invoice.total"
                />
                <FormControl
                    :type="'number'"
                    :ref_for="true"
                    size="sm"
                    variant="subtle"
                    placeholder="0.00"
                    :disabled="true"
                    label="Discount Amount"
                    :value="Number(base.invoice.discount_amount).toFixed(2)"
                    v-model="base.invoice.discount_amount"
                />
                <FormControl
                    type="number"
                    size="sm"
                    variant="subtle"
                    placeholder="0.00"
                    :disabled="false"
                    label="Tips (AED)"
                    v-model="tipsAmount"
                />
                <FormControl
                    :type="'number'"
                    :ref_for="true"
                    size="sm"
                    variant="subtle"
                    placeholder="0.00"
                    :disabled="true"
                    label="Grand Total"
                    :value="Number(base.invoice.grand_total).toFixed(2)"
                    v-model="base.invoice.grand_total"
                />
            </div>

            <!-- Advances Section -->
            <div v-for="(credit, index) in base.invoice.advances" :key="index">
                <div class="grid grid-cols-3 gap-4 p-2">
                    <FormControl
                        :type="'text'"
                        :ref_for="true"
                        size="sm"
                        variant="subtle"
                        placeholder="0.00"
                        :disabled="true"
                        label="Credit Origin"
                        v-model="credit.reference_name"
                    />
                    <FormControl
                        :type="'number'"
                        :ref_for="true"
                        size="sm"
                        variant="subtle"
                        placeholder="0.00"
                        :disabled="true"
                        label="Total Credit"
                        :value="Number(credit.advance_amount).toFixed(2)"
                        v-model="credit.advance_amount"
                    />
                    <FormControl
                        :type="'number'"
                        :ref_for="true"
                        size="sm"
                        variant="subtle"
                        placeholder="0.00"
                        :disabled="false"
                        label="Credit To Redeem"
                        :value="Number(credit.allocated_amount).toFixed(2)"
                        v-model="credit.allocated_amount"
                        @change="changePaymentAmount($event)"
                    />
                </div>
            </div>

            <div>
                <DatePicker
                    v-if="base.pos_profile.custom_set_sales_order"
                    size="md"
                    v-model="deliveryDate"
                    variant="subtle"
                    placeholder="Delivery Date"
                    :disabled="false"
                />
            </div>
        </div>

        <!-- Buttons -->
        <div class="h-[14%] w-full mt-2 flex flex-col gap-2 ">
            <div class="h-1/2 ">
                <div class="flex gap-8 h-full mb-3 justify-center items-center">
                    <Button
                        class="w-1/2 h-[90%]"
                        :variant="'solid'"
                        size="lg"
                        label="Submit"
                        :loading="submit_invoice.loading"
                        :disabled="submit_invoice.loading"
                        @click="submitInvoice()"
                        style="background-color: #4e60ac; color: #ffffff;"
                    >
                        Submit
                    </Button>
                    <Button
                        class="w-1/2  h-[90%]"
                        :variant="'solid'"
                        size="lg"
                        label="Submit & Print"
                        :loading="submit_invoice.loading"
                        :disabled="submit_invoice.loading"
                        @click="submitInvoice('print')"
                        style="background-color: #4e60ac; color: #ffffff;"
                    >
                        Submit & Print
                    </Button>
                </div>
            </div>
            <div class="h-1/2">
                <Button
                    class="w-full h-[90%]"
                    :variant="'ghost'"
                    size="lg"
                    label="Cancel"
                    :loading="false"
                    :disabled="false"
                    @click="remove_invoice"
                    theme="red"
                >
                    Cancel
                </Button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { Button, FormControl, createResource, DatePicker, dayjsLocal  } from 'frappe-ui'
import { ref, inject, onMounted , watch, computed } from 'vue'
import { createToast } from '../utils';

let base = inject('base')
const emitter = inject('emitter') // Emitter for communication
let errorHandled = false;

const tipsAmount = ref(0)
const grandTotalWithoutTips = ref(0)

watch(tipsAmount, (newTipsValue) => {
    const tips = Number(newTipsValue) || 0;
    base.invoice.grand_total = grandTotalWithoutTips.value + tips;
    base.invoice.custom_tips_amount = tips; // Make sure this custom field exists on Sales Invoice Doctype
})

const isExclusiveVat = ref(false)
const originalTotals = ref({})

watch(isExclusiveVat, (newVal) => {
    if (newVal) {
        base.invoice.net_total = Number(originalTotals.value.net_total * 0.95).toFixed(2)
        base.invoice.total = Number(originalTotals.value.total * 0.95).toFixed(2)
        base.invoice.grand_total = Number(originalTotals.value.grand_total * 0.95).toFixed(2)
    } else {
        base.invoice.net_total = Number(originalTotals.value.net_total).toFixed(2)
        base.invoice.total = Number(originalTotals.value.total).toFixed(2)
        base.invoice.grand_total = Number(originalTotals.value.grand_total).toFixed(2)
    }
    grandTotalWithoutTips.value = Number(base.invoice.grand_total);
})

const addPayments = () => {
    const totalToPay = Number(base.invoice.grand_total) || 0;
    base.invoice.paid_amount = totalToPay;
    base.pos_profile.payments.forEach(element => {
        if (!base.invoice.payments.some(p => p.mode_of_payment === element.mode_of_payment) && (base.is_return && element.allow_in_returns || !base.is_return )) {
            base.invoice.payments.push({
                "mode_of_payment": element.mode_of_payment,
                "amount": Number(element.default) ? totalToPay : 0.00,
                "base_amount": Number(element.default) ? totalToPay : 0.00,
            });
        }
    });
}

const changemode = (index) => {
    const totalToPay = Number(base.invoice.grand_total);
    base.invoice.payments.forEach((element, i) => {
        element.amount = (i === index) ? totalToPay : 0;
    });
    base.invoice.paid_amount = totalToPay;
}

const deliveryDate = computed({
  get: () => base.invoice.delivery_date || dayjsLocal().format('YYYY-MM-DD'),
  set: (value) => { base.invoice.delivery_date = value; }
})

onMounted(() => {
    originalTotals.value = {
        net_total: base.invoice.net_total,
        total: base.invoice.total,
        grand_total: base.invoice.grand_total
    };
    grandTotalWithoutTips.value = Number(base.invoice.grand_total);
    addPayments();
});

const baseurl = createResource({ url: 'ant_pos.ant_pos.utils.get_domain_url' });

// Resource to submit the invoice
const submit_invoice = createResource({
    url: 'frappe.desk.form.save.savedocs',
    makeParams(params) {
        return {
            doc: JSON.stringify({ ...base.invoice, docstatus: 1 }),
            action: 'Submit'
        };
    },
    async onSuccess(data) {
        createToast({ title: 'Success', message: 'Invoice Submitted Successfully' });
        if (submit_invoice.params.print) {
            await baseurl.fetch();
            window.open(
                `${baseurl.data}/printview?doctype=Sales+Invoice&name=${data.docs[0].name}&format=${encodeURIComponent(base.pos_profile.print_format)}&trigger_print=1`,
                "_blank"
            );
        }
        remove_invoice(); // Clear form after success
    },
    onError(error) {
        createToast({ title: 'Error', message: error.messages?.[0] || 'An error occurred' });
    }
});

// Main function to trigger submission
const submitInvoice = (print = null) => {
    const params = print ? { print: true } : {};
    submit_invoice.fetch(params);
};

// Function to cancel and clear the invoice
const remove_invoice = () => {
    base.invoice = {};
    base.items = [];
    base.customer = {};
    tipsAmount.value = 0; // Reset tips
    emitter.emit('updatePage', 'Pos'); // Go back to main POS screen
};

// Function to recalculate total paid amount
const changePaymentAmount = () => {
    let totalPaid = 0;
    base.invoice.payments.forEach(p => {
        totalPaid += Number(p.amount) || 0;
    });
    base.invoice.paid_amount = totalPaid;
};
</script>