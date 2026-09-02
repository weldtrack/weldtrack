import api from '../api/api'

export interface ServicePricingInfo {
  pricing_type: 'hourly' | 'fixed' | 'hybrid'
  price_fixed: number
  price_hour: number
}

let cachedServicePriceMap: Record<string, number> | null = null
let cachedServicePricingInfoMap: Record<string, ServicePricingInfo> | null = null
let loadingPromise: Promise<Record<string, number>> | null = null

export function normalizeServiceName(value: string) {
  return value.trim().toLowerCase()
}

function extractServiceName(service: any) {
  return String(service?.name ?? service?.serviceName ?? service?.title ?? '').trim()
}

export function extractServicePricingInfo(service: any): ServicePricingInfo {
  const rawType = String(service?.pricing_type ?? '').trim().toLowerCase()
  const pricingType = rawType === 'fixed' || rawType === 'hybrid' ? rawType : 'hourly'
  return {
    pricing_type: pricingType,
    price_fixed: Number(service?.price_fixed ?? 0),
    price_hour: Number(service?.price_hour ?? 0),
  }
}

function extractServicePrice(service: any) {
  const info = extractServicePricingInfo(service)
  if (info.pricing_type === 'fixed') {
    return info.price_fixed
  }
  return info.price_hour
}

export async function loadServicePriceMap(forceReload = false): Promise<Record<string, number>> {
  if (cachedServicePriceMap && !forceReload) return cachedServicePriceMap
  if (loadingPromise && !forceReload) return loadingPromise

  loadingPromise = api
    .get('/services')
    .then((response) => {
      const services = Array.isArray(response.data)
        ? response.data
        : response.data?.data ?? response.data?.services ?? []

      cachedServicePriceMap = {}
      cachedServicePricingInfoMap = {}

      for (const service of services) {
        const name = extractServiceName(service)
        if (!name) continue
        const norm = normalizeServiceName(name)
        const info = extractServicePricingInfo(service)
        cachedServicePricingInfoMap[norm] = info
        cachedServicePriceMap[norm] = extractServicePrice(service)
      }

      return cachedServicePriceMap ?? {}
    })
    .catch((error) => {
      cachedServicePriceMap = {}
      cachedServicePricingInfoMap = {}
      throw error
    })
    .finally(() => {
      loadingPromise = null
    })

  return loadingPromise
}

export async function loadServicePricingInfoMap(forceReload = false): Promise<Record<string, ServicePricingInfo>> {
  await loadServicePriceMap(forceReload)
  return cachedServicePricingInfoMap ?? {}
}

export function getServicePricingInfo(
  projectType: string,
  infoMap: Record<string, ServicePricingInfo> = cachedServicePricingInfoMap ?? {},
): ServicePricingInfo {
  return (
    infoMap[normalizeServiceName(projectType)] ?? {
      pricing_type: 'hourly',
      price_fixed: 0,
      price_hour: 0,
    }
  )
}

export function getServicePrice(
  projectType: string,
  priceMap: Record<string, number> = cachedServicePriceMap ?? {},
) {
  return priceMap[normalizeServiceName(projectType)] ?? 0
}

export function getServicePriceDisplay(
  projectType: string,
  estimatedCost?: number,
  priceMap?: Record<string, number>,
) {
  if (Number(estimatedCost ?? 0) > 0) return Number(estimatedCost)
  return getServicePrice(projectType, priceMap)
}

export function formatServicePricing(serviceOrInfo?: Partial<ServicePricingInfo> | any): string {
  if (!serviceOrInfo) return '₱0.00'
  const type = serviceOrInfo.pricing_type || 'hourly'
  const fixed = Number(serviceOrInfo.price_fixed ?? 0)
  const hour = Number(serviceOrInfo.price_hour ?? 0)

  if (type === 'fixed') {
    return `₱${fixed.toLocaleString('en-PH', { minimumFractionDigits: 2 })} (Fixed)`
  }
  if (type === 'hybrid') {
    return `₱${fixed.toLocaleString('en-PH', { minimumFractionDigits: 2 })} base + ₱${hour.toLocaleString('en-PH', { minimumFractionDigits: 2 })}/hr`
  }
  return `₱${hour.toLocaleString('en-PH', { minimumFractionDigits: 2 })}/hr`
}

export function calculateServiceLabor(
  pricing: Partial<ServicePricingInfo> | null | undefined,
  hours: number,
  staffMultiplier = 1,
): number {
  if (!pricing) return 0
  const type = pricing.pricing_type || 'hourly'
  const fixed = Number(pricing.price_fixed ?? 0)
  const hour = Number(pricing.price_hour ?? 0)
  const h = Math.max(0, Number(hours || 0))
  const multiplier = Math.max(1, Number(staffMultiplier || 1))

  if (type === 'fixed') {
    return fixed
  }
  if (type === 'hybrid') {
    return fixed + h * multiplier * hour
  }
  return h * multiplier * hour
}

export function formatCurrency(value: number): string {
  return `₱${Number(value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2 })}`
}

export function getPricingTypeLabel(type?: string): string {
  if (type === 'fixed') return 'Fixed Price'
  if (type === 'hybrid') return 'Hybrid'
  return 'Hourly Rate'
}
