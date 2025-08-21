import { ref } from 'vue';
import Settings from '../component/Dialog/Settings.vue';


export function useDynamicComponent() {
    const currentComponent = ref(null);

    const loadComponent = async (componentName) => {
        try {
            const components = {

                OpenShift: () => import('../component/Dialog/Open-Shift.vue'),
                CustomerForm: () => import('../component/Dialog/CustomerForm.vue'),
                Held: () => import('../component/Dialog/Held.vue'),
                Return: () => import('../component/Dialog/Return.vue'),
                CloseShift:() => import('../component/Dialog/CloseShift.vue'),
                Settings:() => import('../component/Dialog/Settings.vue')
            
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
