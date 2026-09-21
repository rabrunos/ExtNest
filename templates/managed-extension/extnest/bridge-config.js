// ExtNest Bridge configuration.
globalThis.EXTNEST_BRIDGE_CONFIG = {
  protocol: 1,
  vaultExtensionIds: [
    "econfanmnmmcggpgdflcipmdlmkcbiag",
    // "EDGE_STORE_EXTENSION_ID",
    // "CHROME_WEB_STORE_EXTENSION_ID"
  ],
  backupKeys: ["theme", "preferences"],
  schema: 1,
  async exportTransform(data) { return data; },
  async importTransform(data, fromSchema) { return data; }
};
