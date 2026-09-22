import { WaterBodyConfig } from "../types/analysis";

export const WATER_BODIES_REGISTRY: Record<string, WaterBodyConfig> = {
  "gosikhurd-reservoir": {
    id: "gosikhurd-reservoir",
    name: "Gosikhurd Reservoir",
    type: "reservoir",
    description: "Gosikhurd Dam on Wainganga River",
    aoi: {
      type: "Feature",
      properties: {
        waterBodyId: "gosikhurd-reservoir",
        name: "Gosikhurd Reservoir",
        type: "reservoir"
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [79.62, 20.87],
            [79.64, 20.87],
            [79.64, 20.85],
            [79.62, 20.85],
            [79.62, 20.87]
          ]
        ]
      }
    },
    defaultCenter: [20.86, 79.63],
    defaultZoom: 13,
    aoiStatus: "demo"
  },
  "godavari-selected-segment": {
    id: "godavari-selected-segment",
    name: "Godavari River \u2013 Selected Segment",
    type: "river_segment",
    description: "A specific selected segment of Godavari River",
    aoi: {
      type: "Feature",
      properties: {
        waterBodyId: "godavari-selected-segment",
        name: "Godavari River \u2013 Selected Segment",
        type: "river_segment"
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [77.30, 19.10],
            [77.32, 19.11],
            [77.32, 19.09],
            [77.30, 19.08],
            [77.30, 19.10]
          ]
        ]
      }
    },
    defaultCenter: [19.095, 77.31],
    defaultZoom: 13,
    aoiStatus: "demo"
  },
  "wainganga-selected-segment": {
    id: "wainganga-selected-segment",
    name: "Wainganga River \u2013 Selected Segment",
    type: "river_segment",
    description: "A specific selected segment of Wainganga River",
    aoi: {
      type: "Feature",
      properties: {
        waterBodyId: "wainganga-selected-segment",
        name: "Wainganga River \u2013 Selected Segment",
        type: "river_segment"
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [79.60, 20.80],
            [79.61, 20.81],
            [79.62, 20.79],
            [79.61, 20.78],
            [79.60, 20.80]
          ]
        ]
      }
    },
    defaultCenter: [20.795, 79.61],
    defaultZoom: 13,
    aoiStatus: "demo"
  },
  "jaikwadi-reservoir": {
    id: "jaikwadi-reservoir",
    name: "Jaikwadi Reservoir",
    type: "reservoir",
    description: "Jaikwadi Dam Reservoir",
    aoi: {
      type: "Feature",
      properties: {
        waterBodyId: "jaikwadi-reservoir",
        name: "Jaikwadi Reservoir",
        type: "reservoir"
      },
      geometry: {
        type: "Polygon",
        coordinates: [
          [
            [75.30, 19.45],
            [75.40, 19.45],
            [75.40, 19.40],
            [75.30, 19.40],
            [75.30, 19.45]
          ]
        ]
      }
    },
    defaultCenter: [19.425, 75.35],
    defaultZoom: 11,
    aoiStatus: "demo"
  },
  "custom-aoi": {
    id: "custom-aoi",
    name: "Custom AOI",
    type: "custom",
    description: "Custom user-defined Area of Interest",
    aoi: null,
    defaultCenter: [20.87, 79.62],
    defaultZoom: 11,
    aoiStatus: "drawing"
  }
};

export const WATER_BODIES_LIST = [
  "Gosikhurd Reservoir",
  "Godavari River \u2013 Selected Segment",
  "Wainganga River \u2013 Selected Segment",
  "Jaikwadi Reservoir",
  "Custom AOI"
];
