import RetraceLong from './RetraceLong'
import Retracement from './Retracement'
import Risk from './Risk'
import RsiProject from './RsiProject'

const DfContainer = () => {
  return (
    <div style={{ width: '50%', display: 'flex', flexDirection: 'column' }}>
      <Retracement />
      <RetraceLong />
      <Risk />
      <RsiProject />
    </div>
  )
}

export default DfContainer