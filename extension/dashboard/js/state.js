export const state = {
  helperOnline: false,
  helperError: "",
  registry: [],
  installed: [],
  auth: {
    github_accounts: [],
    github: null,
    microsoft: null,
    google: null
  },
  cloud: { primary: "" },
  paths: null,
  repos: []
};
