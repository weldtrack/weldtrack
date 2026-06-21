import api from '../api/api'

let cachedServicePriceMap: Record<string, number> | null = null
let loadingPromise: Promise<Record<string, number>> | null = null

function normalizeServiceName(value: string) {
  return value.trim().toLowerCase()
}

function extractServiceName(service: any) {
  return String(service?.name ?? service?.serviceName ?? service?.title ?? '').trim()
}

function extractServicePrice(service: any) {
  return Number(service?.price ?? service?.laborPrice ?? service?.labor_price ?? 0)
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

      cachedServicePriceMap = services.reduce((acc: Record<string, number>, service: any) => {
        const name = extractServiceName(service)
        if (!name) return acc
        acc[normalizeServiceName(name)] = extractServicePrice(service)
        return acc
      }, {})

      return cachedServicePriceMap ?? {}
    })
    .catch((error) => {
      cachedServicePriceMap = {}
      throw error
    })
    .finally(() => {
      loadingPromise = null
    })

  return loadingPromise
}

export function getServicePrice(projectType: string, priceMap: Record<string, number> = cachedServicePriceMap ?? {}) {
  return priceMap[normalizeServiceName(projectType)] ?? 0
}

export function getServicePriceDisplay(projectType: string, estimatedCost?: number, priceMap?: Record<string, number>) {
  if (Number(estimatedCost ?? 0) > 0) return Number(estimatedCost)
  return getServicePrice(projectType, priceMap)
}
