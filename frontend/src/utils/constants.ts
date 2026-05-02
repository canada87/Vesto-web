export const CATEGORY_LABELS: Record<string, string> = {
  top: 'Parte sopra',
  bottom: 'Parte sotto',
  shoes: 'Scarpe',
  outerwear: 'Capospalla',
  accessory: 'Accessorio',
  underwear: 'Intimo',
  sportswear: 'Abbigliamento sportivo',
}

export const CATEGORY_ICONS: Record<string, string> = {
  top: 'mdi-tshirt-crew',
  bottom: 'mdi-hanger',
  shoes: 'mdi-shoe-heel',
  outerwear: 'mdi-coat-rack',
  accessory: 'mdi-watch',
  underwear: 'mdi-hanger',
  sportswear: 'mdi-run',
}

export const SEASON_LABELS: Record<string, string> = {
  spring: 'Primavera',
  summer: 'Estate',
  autumn: 'Autunno',
  winter: 'Inverno',
}

export const SEASON_ICONS: Record<string, string> = {
  spring: 'mdi-flower',
  summer: 'mdi-white-balance-sunny',
  autumn: 'mdi-leaf',
  winter: 'mdi-snowflake',
}

export const WEATHER_LABELS: Record<string, string> = {
  sunny: 'Soleggiato',
  cloudy: 'Nuvoloso',
  rainy: 'Pioggia',
  cold: 'Freddo',
  hot: 'Caldo',
}

export const WEATHER_ICONS: Record<string, string> = {
  sunny: 'mdi-weather-sunny',
  cloudy: 'mdi-weather-cloudy',
  rainy: 'mdi-weather-rainy',
  cold: 'mdi-snowflake',
  hot: 'mdi-thermometer-high',
}

export const USAGE_TYPE_LABELS: Record<string, string> = {
  work: 'Lavoro',
  personal: 'Personale',
  both: 'Entrambi',
}

export const STATUS_LABELS: Record<string, string> = {
  inWardrobe: 'In guardaroba',
  inLaundry: 'In lavanderia',
  inUse: 'In uso',
}

export const STATUS_COLORS: Record<string, string> = {
  inWardrobe: 'success',
  inLaundry: 'warning',
  inUse: 'info',
}

export const CONDITION_LABELS: Record<string, string> = {
  new: 'Nuovo',
  good: 'Buono',
  worn: 'Consumato',
  old: 'Vecchio',
}

export const WEIGHT_LABELS: Record<string, string> = {
  light: 'Leggero',
  medium: 'Medio',
  heavy: 'Pesante',
}

export const CATEGORIES = Object.keys(CATEGORY_LABELS)
export const SEASONS = Object.keys(SEASON_LABELS)
export const WEATHERS = Object.keys(WEATHER_LABELS)
export const USAGE_TYPES = Object.keys(USAGE_TYPE_LABELS)
export const STATUSES = Object.keys(STATUS_LABELS)
export const CONDITIONS = Object.keys(CONDITION_LABELS)
export const WEIGHTS = Object.keys(WEIGHT_LABELS)
