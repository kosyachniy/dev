import { connect } from 'react-redux';
import { activateGeod, closeGeod } from '../../redus';

import Main from './Main';


const mapStateToProps = state => ({
	geod: state.geod,
});

const mapDispatchToProps = {
	activateGeod,
	closeGeod,
};

const AppContainer = connect(
	mapStateToProps,
	mapDispatchToProps
)(Main);

export default AppContainer;