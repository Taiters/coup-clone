/** @type {import('tailwindcss').Config} */
module.exports = {
  safelist: [
    "bg-influence-unknown",
    "bg-influence-ambassador",
    "bg-influence-assassin",
    "bg-influence-captain",
    "bg-influence-duke",
    "bg-influence-contessa",
    "text-influence-unknown",
    "text-influence-ambassador",
    "text-influence-assassin",
    "text-influence-captain",
    "text-influence-duke",
    "text-influence-contessa",
  ],
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    colors: {
      white: "#ffffff",
      yellow: "#fffede",
      darkyellow: "#e8cfa9",
      darkeryellow: "#d9be94",
      brown: "#98754d",
      lightbrown: "#efc493",
      darkbrown: "#614627",
      purple: "#c78dba",
      gray: "#b1b59a",
      darkgray: "#8e8d7e",
      overlay: "#32220861",

      influence: {
        unknown: "#8E8D7E",
        ambassador: "#ADB55A",
        assassin: "#689393",
        captain: "#4494DE",
        duke: "#BF7BDF",
        contessa: "#DA7777",
      },
    },
  },
  plugins: [],
};
