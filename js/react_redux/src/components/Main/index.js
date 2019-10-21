import React from 'react';

import { connect } from 'react-redux';

import { activateGeod, closeGeod } from '../../redus';

// App.js
export class App extends React.Component {
  render() {
    return (
      <div>
        <h1>{this.props.geod.title || 'Hello World!'}</h1>

        {this.props.geod.title ? (
          <button onClick={this.props.closeGeod}>Exit Geod</button>
        ) : (
          <button
            onClick={() =>
              this.props.activateGeod({ title: 'I am a geo dude!' })
            }
          >
            Click Me!
          </button>
        )}
      </div>
    );
  }
}

// AppContainer.js
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
)(App);

export default AppContainer;
