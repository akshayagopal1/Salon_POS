import { ref } from 'vue';

export function useDynamicComponent() {
    const currentComponent = ref(null);

    const loadComponent = async (componentName) => {
        try {
            const components = {

                OpenShift: () => import('@/components/Dialog/Open-Shift.vue'),
                CustomerForm: () => import('@/components/Dialog/CustomerForm.vue'),
                Held: () => import('@/components/Dialog/Held.vue'),
                Return: () => import('@/components/Dialog/Return.vue'),
                CloseShift: () => import('@/components/Dialog/CloseShift.vue'),
                Settings: () => import('@/components/Dialog/Settings.vue'),
                Attendance: () => import('../components/Dialog/Attendance.vue'), // ✅ Added
            };

            if (components[componentName]) {
                // Reset the current component to null before loading
                currentComponent.value = null;

                // Small delay to ensure Vue notices the change
                await new Promise((resolve) => setTimeout(resolve, 0));

                const component = await components[componentName]();

                currentComponent.value = component.default;
            } else {
                console.error(`Component "${componentName}" not found.`);
                currentComponent.value = null;
            }
        } catch (error) {
            console.error('Error loading component:', error);
            currentComponent.value = null;
        }
    };

    return { currentComponent, loadComponent };
}
