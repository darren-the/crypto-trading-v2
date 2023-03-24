import { store } from '../../app/store'
import config from '../../config.json'
import { selectDfNames } from './dispatch-utils'

export const isPendable = (name, updateMethod) => {
  const state = store.getState()[name]
  if (updateMethod === config.updateMethod.PREPEND) {
    if (state.prependable) return true
    else return false
  } else if (updateMethod === config.updateMethod.APPEND) {
    if (state.appendable) return true
    else return false
  }
  return true
}

export const baseDispatcher = (func, exitConditions) => {
  return async (funcArgs) => {
    const args = funcArgs || {}  // TODO: is this line needed?
    const state = store.getState()

    selectDfNames().map(async (name) => {
      var exit = false
      exitConditions.forEach(exitCondition => {
        switch (exitCondition) {
          default:
          case 'loading':
            if (state[name].status === 'loading' && !args.ignoreLoading) {
              exit = true
            }
            break
          case 'pendable':
            if (!isPendable(name, args.updateMethod)) {
              exit = true
            }
            break
          case 'display':
            if (state[name].displayIndex === -1) {
              exit = true
            }
        }
      })
      if (exit) return false

      store.dispatch({ type: `${name}/startLoading` })
      if (typeof func === 'function') {
        await func({ name, ...args })
      } else if (typeof func === 'object') {
        for (var i = 0; i < func.length; i++) {
          await func[i]({ name, ...args })
        }
      }
      store.dispatch({ type: `${name}/finishLoading` })

      return true
    })

    return true
  }
}

const exitDispatcher = (args) => {
  const { name, updateMethod, exitConditions } = args
  const state = store.getState()[name]
  var exit = false
  exitConditions.forEach(exitCondition => {
    switch (exitCondition) {
      default:
      case 'loading':
        if (state.status === 'loading') {
          exit = true
        }
        break
      case 'pendable':
        if (!isPendable(name, updateMethod)) {
          exit = true
        }
        break
      case 'display':
        if (state.displayIndex === -1) {
          exit = true
        }
    }
  })
  return exit
}

export const horizontalDispatcher = (func, exitConditions) => {
  return async (args) => {
    var exit = false
    selectDfNames().forEach(name => {
      if (exitDispatcher({ name, ...args, exitConditions })) exit = true
    })
    if (exit) return false
    selectDfNames().forEach(name => {
      store.dispatch({ type: `${name}/startLoading` })
    })

    const orderedDfNames = config.dispatchOrder
    const processOrderedDfs = async (func) => {
      for (let i = 0; i < orderedDfNames.length; i++) {
        await func({ name: orderedDfNames[i], ...args })
      }
    }
    const unorderedDfNames = selectDfNames().filter(name => !orderedDfNames.includes(name))
    for (let i = 0; i < func.length; i++) {
      await Promise.all([
        processOrderedDfs(func[i]),
        ...unorderedDfNames.map(async (name) => {
          await func[i]({ name, ...args })
        })
      ])
    }

    selectDfNames().forEach(name => {
      store.dispatch({ type: `${name}/finishLoading` })
    })
  }
}

export const verticalDispatcher = (func, exitConditions) => {
  return async (args) => {
    var exit = false
    selectDfNames().forEach(name => {
      if (exitDispatcher({ name, ...args, exitConditions })) exit = true
    })
    if (exit) return false
    selectDfNames().forEach(name => {
      store.dispatch({ type: `${name}/startLoading` })
    })

    await Promise.all(selectDfNames().map(async (name) => {
      for (let i = 0; i < func.length; i++) {
        await func[i]({ name, ...args })
      }
    }))

    selectDfNames().forEach(name => {
      store.dispatch({ type: `${name}/finishLoading` })
    })
  }
}
