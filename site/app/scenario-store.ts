export type MortgageGoal = "purchase" | "va" | "fha" | "refinance" | "equity";

export type SavedMortgageScenario = {
  goal: MortgageGoal;
  homePrice: number;
  downPayment: number;
  rate: number;
  payment: number;
  savedAt: number;
};

export const scenarioStorageKey = "drmortgage-active-scenario";
export const scenarioEventName = "drmortgage-scenario-updated";

export function readMortgageScenario(): SavedMortgageScenario | null {
  if (typeof window === "undefined") return null;
  try {
    const value = window.localStorage.getItem(scenarioStorageKey);
    return value ? JSON.parse(value) as SavedMortgageScenario : null;
  } catch {
    return null;
  }
}

export function saveMortgageScenario(scenario: SavedMortgageScenario) {
  window.localStorage.setItem(scenarioStorageKey, JSON.stringify(scenario));
  window.dispatchEvent(new CustomEvent(scenarioEventName, { detail: scenario }));
}

export function clearMortgageScenario() {
  window.localStorage.removeItem(scenarioStorageKey);
  window.dispatchEvent(new CustomEvent(scenarioEventName));
}
