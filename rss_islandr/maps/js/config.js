// Map Configuration
const MAP_CONFIG = {
    center: [53.3439, 23.0622],
    zoom: 4,
    baseLayer: {
      url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
      //attribution: 'Map data © OpenStreetMap contributors'
    },
  };
  

  // WMS Layers Configuration
  const WMS_LAYERS = {
    geology: {
      name: "Geology",
      url: "https://geoserver.geo-zs.si/egdi-surface-geology/gsmlp/wms",
      params: {
        layers: "gsmlp:GeologicUnitView_Lithology",
        format: "image/png",
        transparent: true,
        version: "1.3.0",
      },
      attribution: "Geological Survey of Slovenia (GeoZS)",
      legendId: "GeologyLegend",
      defaultOn: false,
    },
    geologyBGR: {
      name: "GeologyBGR",
      url: "https://services.bgr.de/wms/geologie/igk1500/",
      params: {
        layers: "0,1,2",
        format: "image/png",
        transparent: true,
        version: "1.3.0",
      },
      attribution:
        "BGR: International Geological Map of Europe and the Mediterranean Regions 1:1,500,000",
      legendId: "GeologyBGRLegend",
      defaultOn: false,
    },
  
    geologyIGME5000BGR: {
      name: "GeologyIGME5000BGR",
      url: "https://services.bgr.de/wms/geologie/igme5000/",
      params: {
        layers:
          "3,5,6,8,10,11,13,14,15,16,17,18,19,20,22,23,24,27,29,31,33,37,39,41,43,44,46,47,48,51,53,55,57",
        format: "image/png",
        transparent: true,
        version: "1.3.0",
      },
      attribution:
        "BGR: 1:5 Million International Geological Map of Europe and Adjacent Areas (IGME5000)",
      legendId: "GeologyIGME5000BGRLegend",
      defaultOn: false,
    },
  
    geologyIGE2500BGR: {
      name: "GeologyIGE2500BGR",
      url: "https://services.bgr.de/wms/geologie/iqe2500/",
      params: {
        layers: "0,1",
        format: "image/png",
        transparent: true,
        version: "1.3.0",
      },
      attribution: "BGR: International Quaternary Map of Europe 1:2,500,000",
      legendId: "GeologyIGE2500BGRLegend",
      defaultOn: false,
    },
    mines: {
      name: "Mines",
      url: "https://data.geus.dk/egdi/wms/",
      params: {
        layers: "egdi_mines",
        format: "image/png",
        transparent: true,
        version: "1.3.0",
      },
      attribution:
        '<a href="https://maps.europe-geology.eu/?mapname=egdi_geoera_mintell4eu#baslay=baseMapGEUS&extent=302590,950050,8202390,5515330&layers=egdi_mines&filter_0=commodity.part%3D%26status.multi%3D%26miningactivity.multi%3D" target="_blank">Mintell4EU Project</a>',
      legendId: "MinesLegend",
      defaultOn: false,
    },
    // gemas: {
    //   name: 'Gemas',
    //   url: 'https://services.bgr.de/wms/geochemie/gemas_supporting_information/',
    //   params: {
    //     layers: '2,3,5,6,8,9,11,13,15',
    //     format: 'image/png',
    //     transparent: true,
    //     version: '1.3.0'
    //   },
    //   attribution: 'GEMAS – Chemistry of Europe’s Agricultural soils, Supporting information',
    //   legendId: 'GemasLegend',
    //   defaultOn: false
    // },
    hydroEurope: {
      name: "HydroEurope",
      url: "https://services.bgr.de/wms/grundwasser/ihme1500/",
      params: {
        layers: "0,1,2",
        format: "image/png",
        transparent: true,
        version: "1.3.0",
      },
      attribution:
        "BGR & UNESCO (eds.) (2019): International Hydrogeological Map of Europe 1:1,500,000 (IHME1500)",
      legendId: "HydroEuropeLegend",
      defaultOn: false,
    },
    hydroGlobal: {
      name: "HydroGlobal",
      url: "https://services.bgr.de/wms/grundwasser/whymap_gwr/",
      params: {
        layers: "0",
        format: "image/png",
        transparent: true,
        version: "1.3.0",
      },
      attribution: "BGR: Groundwater Resources of the World (WHYMAP GWR) (WMS)",
      legendId: "HydroGlobalLegend",
      defaultOn: false,
    },
    BGRNorm: {
      name: "BGRNorm",
      url: "https://services.bgr.de/wms/grundwasser/norm/",
      params: {
        layers: "1,2,3,4,6,7",
        format: "image/png",
        transparent: true,
        version: "1.3.0",
      },
      attribution: "BGR: Natural Radionuclides in Groundwater",
      legendId: "BGRNormLegend",
      defaultOn: false,
    },
  
    BGRrgwb: {
      name: "BGRrgwb",
      url: "https://services.bgr.de/wms/grundwasser/whymap_rgwb/",
      params: {
        layers: "0,1,3,4,5",
        format: "image/png",
        transparent: true,
        version: "1.3.0",
      },
      attribution: "BGR: River and Groundwater Basins of the World (WHYMAP RGWB)",
      legendId: "BGRrgwbLegend",
      defaultOn: false,
    },
  
    BGRwokam: {
      name: "BGRwokam",
      url: "https://services.bgr.de/wms/grundwasser/whymap_wokam/",
      params: {
        layers: "0,1,2,3,4,5,6",
        format: "image/png",
        transparent: true,
        version: "1.3.0",
      },
      attribution: "BGR: World Karst Aquifer Map (WHYMAP WOKAM)",
      legendId: "BGRwokamLegend",
      defaultOn: false,
    },
  
    soilEurope: {
      name: "SoilEurope",
      url: "https://services.bgr.de/wms/boden/eusr5000/",
      params: {
        layers: "1,3,5",
        format: "image/png",
        transparent: true,
        version: "1.3.0",
      },
      attribution:
        "BGR: Soil Regions of the European Union and Adjacent Countries 1:5,000,000 (WMS)",
      legendId: "SoilEuropeLegend",
      defaultOn: false,
    },
    riverNetwork: {
      name: "RiverNetwork",
      url: "https://image.discomap.eea.europa.eu/arcgis/services/EUHydro/EUHydro_RiverNetworkDatabase/MapServer/WMSServer",
      params: {
        layers: "0,1,2,3,4,5",
        format: "image/png",
        transparent: true,
        version: "1.3.0",
      },
      attribution:
        "Generated using European Union's Copernicus Land Monitoring Service information",
      legendId: "RiverNetworkLegend",
      defaultOn: false,
    },
  };