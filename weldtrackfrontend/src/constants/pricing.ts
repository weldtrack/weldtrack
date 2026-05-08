export const laborPriceMap: Record<string, number> = {
  'Gate Welding': 4000,
  'Metal Railings': 6000,
  'Steel Frame Construction': 60000,
  'Staircase Fabrication': 5000,
  'Metal Doors & Windows': 5000,
  'Pipe & Duct Welding': 4000,
  'Metal Shelving': 7000,
  'Automotive Welding': 10000,
  'Fence Installation': 5000,
  'Tank & Vessel Fabrication': 10000,
  'Repair & Maintenance': 6000,
  Other: 0,
}

export function getLaborPrice(projectType: string) {
  return laborPriceMap[projectType] ?? 0
}