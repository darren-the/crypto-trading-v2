import RetraceLong from './RetraceLong'
import Retracement from './Retracement'
import Risk from './Risk'

const DfContainer = () => {
  return (
    <div style={{ width: '50%', display: 'flex', flexDirection: 'column' }}>
      <Retracement />
      <RetraceLong />
      <Risk />
    </div>
  )
}

export default DfContainer