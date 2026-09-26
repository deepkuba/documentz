import eslint from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";

export default tseslint.config(
  { ignores: ["apps/portal/dist", "apps/portal/coverage"] },
  eslint.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["apps/portal/**/*.{ts,tsx}"],
    languageOptions: {
      ecmaVersion: "latest",
      globals: { ...globals.browser, ...globals.node },
    },
  },
);
