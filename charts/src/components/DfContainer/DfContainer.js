import RetraceLong from './RetraceLong'
import Retracement from './Retracement'

const DfContainer = () => {
  return (
    <div style={{ width: '50%', display: 'flex', flexDirection: 'column' }}>
      <Retracement />
      <RetraceLong />
    </div>
  )
}

export default DfContainer