/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./flask_app/templates/**/*.{html,js,jsx,ts,tsx,vue,astro,svelte}"],
    theme: {
      extend: {},
    },
    plugins: [require("@tailwindcss/typography")],
  };
  