export const API_URL =
  import.meta.env.MODE === "test"
    ? import.meta.env.VITE_API_URL_PLAYWRIGHT
    : import.meta.env.VITE_API_URL;
