import { NATIVE_HOST } from "./constants.js";

export function nativeMessage(op, data = {}) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendNativeMessage(NATIVE_HOST, { op, ...data }, response => {
      const err = chrome.runtime.lastError;
      if (err) reject(new Error(err.message));
      else resolve(response);
    });
  });
}

export async function nativeOk(op, data = {}) {
  const response = await nativeMessage(op, data);
  if (!response?.ok) {
    const message = response?.error || `Falha em ${op}`;
    if (/opera.*desconhecida|unknown operation/i.test(message)) {
      throw new Error(
        "Native Host desatualizado. Atualize ou reinstale o ExtNest Native Host e tente novamente."
      );
    }
    throw new Error(message);
  }
  return response;
}
