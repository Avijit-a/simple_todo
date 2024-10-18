import { createTheme } from "@mui/material/styles";

// Creating the custom theme based on your preferences
const theme = createTheme({
  palette: {
    primary: {
      main: "#000048", // Primary color
    },
    secondary: {
      main: "#7dc7ff", // Secondary color
    },
    // Defining additional colors
    accent: {
      main: "#26eeeb", // Accent/Highlight color
    },
    dark: {
      main: "#00224D", // Dark color
    },
    light: {
      main: "#f7f8fa", // Light color
    },
    background: {
      default: "#bdbcc8", // Background/Canvas color
    },
  },
  typography: {
    fontFamily: 'Gelixfont, "Roboto", sans-serif', // Update the font-family
  },
});
export default theme;
