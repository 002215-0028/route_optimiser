export const MAPS_LOADER_OPTIONS = {
    id: "route-optimiser-maps",
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_BROWSER_KEY ?? "",
    libraries: ["places"] as ("places")[],
  };