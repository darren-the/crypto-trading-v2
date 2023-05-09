import RetraceLong from './RetraceLong'
import Retracement from './Retracement'
import Risk from './Risk'
import RsiProject from './RsiProject'
import Structure from './Structure'

const DfContainer = () => {
  return (
    <div style={{ width: '50%', display: 'flex', flexDirection: 'column' }}>
      <Retracement />
      <RetraceLong />
      <Risk />
      <RsiProject />
      <Structure />
    </div>
  )
}

export default DfContainer