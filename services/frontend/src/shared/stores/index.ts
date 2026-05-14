import { atomWithStorage } from "jotai/utils";
import { getDefaultStore } from "jotai";

/**
 * Store Jotai global pour les opérations hors React
 */
const store = getDefaultStore();
/**
 * Langue par défaut
 */
export const langAtom = atomWithStorage<string>('lang', 'fr');

/**
 * Theme par défaut
 */
export const themeAtom = atomWithStorage<string>('theme', 'light');

/**
 * Récupère la langue actuelle
 */
export function getCurrentLang(): string {
    return store.get(langAtom);
} 
