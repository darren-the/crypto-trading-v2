import { updateRetracementComponent } from './retracement/retracementComponent'
import { updateRetracelongComponent } from './retraceLong/retraceLongComponent'
import { updateRiskComponent } from './risk/riskComponent'

// ============= ADD UPDATE COMPONENT HERE ==============
const componentUpdaters = {
  updateRetracementComponent,
  updateRetracelongComponent,
  updateRiskComponent,
}
// ======================================================

export const updateDfComponent = (name, setDfComponent, data) => {
  const upperName = name.charAt(0).toUpperCase() + name.slice(1)
  const componentUpdaterName = 'update' + upperName + 'Component'
  if (componentUpdaters[componentUpdaterName] === undefined) return
  componentUpdaters[componentUpdaterName](name, setDfComponent, data)
}
