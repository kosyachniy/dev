import { connect } from 'react-redux';
import {
    changeLang,
} from '../../../redus';

import Footer from './Footer';


// AppContainer.jsx
const mapStateToProps = state => ({
    system: state.system,
});

const mapDispatchToProps = {
    changeLang,
};

const FooterContainer = connect(
    mapStateToProps,
    mapDispatchToProps
)(Footer);

export default FooterContainer;
