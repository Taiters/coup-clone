import {FaUser} from 'react-icons/fa6';
import HGroup from './HGroup';

type Props = {
    name: string,
}

function PlayerName({name}: Props) {
    return (
        <HGroup>
            <FaUser />
            {name}
        </HGroup>
    );
}

export default PlayerName;