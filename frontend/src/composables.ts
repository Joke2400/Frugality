import type { Ref } from "vue"
import { onMounted, onUnmounted } from 'vue'

export function useDetectClickElement(element: Ref<HTMLElement | null>, callback: (...args: any[]) => any): void {
    function detect(event: MouseEvent) {
        if (element.value && element.value.contains(event.target as Node)) {
            callback(true);
        } else {
            callback(false)
        }
    }
    onMounted(() => window.addEventListener('click', detect))
    onUnmounted(() => window.removeEventListener('click', detect))

}