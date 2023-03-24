const isFeatureLoading = {}

export class BaseFeature {
    constructor({ featureState, setFeatureState }) {
        this.state = featureState[this.constructor.name]
        this.setState = (data) => {
            setFeatureState({
                ...featureState, 
                [this.constructor.name]: data,
            })
        }
        this.isFeatureLoading = isFeatureLoading
        this.isFeatureLoading[this.constructor.name] = false
    }

    update = async (args) => {
        this.isFeatureLoading[this.constructor.name] = true
        const data = await this.fetch(args)
        this.updateSeries({ data })
        this.isFeatureLoading[this.constructor.name] = false
        return data
    }

    // The following should be overridden by child class
    fetch = async (args) => {}
    updateSeries = (args) => {}
    incrementSeries = (args) => {}
}
