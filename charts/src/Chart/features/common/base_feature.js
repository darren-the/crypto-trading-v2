const isFeatureLoading = {}

export class BaseFeature {
    constructor(context) {
        this.context = context
        const { featureState, setFeatureState, isLoading, setIsLoading } = context
        this.state = featureState[this.constructor.name]
        this.setState = (data) => {
            setFeatureState({
                ...featureState,
                [this.constructor.name]: data,
            })
        }
        this.isLoading = isFeatureLoading
        this.isFeatureLoading[this.constructor.name] = false
    }

    update = async (args) => {
        this.isFeatureLoading[this.constructor.name] = true
        const data = await this.fetch(args)
        this.updateSeries({ data })
        // More stuff should happen here i.e. visiblity etc
        this.isFeatureLoading[this.constructor.name] = false
        return data
    }

    // The following should be overridden by child class
    fetch = async (args) => {}
    updateSeries = (args) => {}
    incrementSeries = (args) => {}
}
